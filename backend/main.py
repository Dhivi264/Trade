"""Chart Evidence Analyzer — FastAPI entrypoint.

Endpoints:
  GET  /api/healthz                          -> health probe
  GET  /api/                                 -> {"status": "backend running"}
  GET  /api/ohlc?symbol=&exchange=&tf=&bars= -> raw candles for one timeframe
  POST /api/analyze                          -> full multi-timeframe + image analysis
  POST /api/analyze-image                    -> just the image inspection

In production, this same FastAPI process also serves the built React
frontend (see the StaticFiles mount at the bottom of this file). One
process == one Replit web preview.
"""

from __future__ import annotations

import logging
import os
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile

# Load environment variables from .env file
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from models.schemas import AnalyzeResponse, CandlesResponse, Candle, Evidence, ImageAnalysis
from services.image_analysis import analyze_chart_image
from services.pair_detection import SUPPORTED_PAIRS, detect_pair_from_image
from services.rule_engine import make_decision
from services.tv_data import get_demo_ohlc, get_ohlc

logger = logging.getLogger("chart_evidence")
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOWED_SYMBOLS = set(SUPPORTED_PAIRS)
ALLOWED_TIMEFRAMES = {"1M", "5M", "15M", "30M", "1H", "4H", "1D"}
MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8 MB
ALLOWED_MIME = {"image/png", "image/jpeg", "image/jpg", "image/webp"}

app = FastAPI(title="Chart Evidence Analyzer")

# CORS — wide-open for dev; in production the frontend is same-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _validate_symbol(symbol: str) -> str:
    s = (symbol or "").upper().strip()
    if s not in ALLOWED_SYMBOLS:
        raise HTTPException(400, f"Unsupported symbol '{symbol}'.")
    return s




def _validate_timeframe(tf: str) -> str:
    t = (tf or "").upper().strip()
    if t not in ALLOWED_TIMEFRAMES:
        raise HTTPException(400, f"Unsupported timeframe '{tf}'.")
    return t


# ---------------------------------------------------------------------------
# JSON endpoints (mounted under /api)
# ---------------------------------------------------------------------------

@app.get("/api/healthz")
def healthz():
    return {"ok": True}


@app.get("/api/")
def api_root():
    return {"status": "backend running"}


@app.get("/api/ohlc", response_model=CandlesResponse)
def ohlc(
    symbol: str = Query(...),
    exchange: str = Query(...),
    timeframe: str = Query(...),
    bars: int = Query(300, ge=20, le=1000),
    demo: bool = Query(False),
):
    sym = _validate_symbol(symbol)
    exch = _validate_exchange(exchange)
    tf = _validate_timeframe(timeframe)

    if demo:
        return CandlesResponse(
            symbol=sym, exchange=exch, timeframe=tf,
            candles=[Candle(**c) for c in get_demo_ohlc(sym, tf, bars)],
            source="synthetic",
        )

    try:
        candles, source = get_ohlc(sym, exch, tf, bars=bars)
    except RuntimeError as exc:
        raise HTTPException(502, str(exc))
    return CandlesResponse(
        symbol=sym, exchange=exch, timeframe=tf,
        candles=[Candle(**c) for c in candles],
        source=source,
    )


@app.post("/api/analyze-image", response_model=ImageAnalysis)
async def analyze_image(image: UploadFile = File(...)):
    if image.content_type not in ALLOWED_MIME:
        raise HTTPException(400, f"Unsupported file type '{image.content_type}'.")
    data = await image.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Uploaded image exceeds 8 MB limit.")
    if len(data) < 200:
        raise HTTPException(400, "Uploaded image is empty or too small.")
    result = analyze_chart_image(data)
    return ImageAnalysis(**result)


@app.post("/api/detect-from-image")
async def detect_from_image(image: UploadFile = File(...)):
    """OCR the uploaded chart screenshot and return the detected
    trading pair, OTC flag and an exchange hint."""
    if image.content_type not in ALLOWED_MIME:
        raise HTTPException(400, f"Unsupported file type '{image.content_type}'.")
    data = await image.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Uploaded image exceeds 8 MB limit.")
    if len(data) < 200:
        raise HTTPException(400, "Uploaded image is empty or too small.")
    result = detect_pair_from_image(data)
    # Only surface symbols we currently support in the rule engine.
    if result.get("symbol") and result["symbol"] not in ALLOWED_SYMBOLS:
        result["symbol"] = None
        result["exchange"] = None
        result["confidence"] = 0
        result["reason"] = (
            "Detected pair is not currently supported by the analyzer."
        )
    return JSONResponse(result)


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(
    symbol: Optional[str] = Form(None),
    bars: int = Form(300),
    image: UploadFile = File(...),
):
    # 1) Validate + read image
    if image.content_type not in ALLOWED_MIME:
        raise HTTPException(400, f"Unsupported file type '{image.content_type}'.")
    data = await image.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Uploaded image exceeds 8 MB limit.")
    if len(data) < 200:
        raise HTTPException(400, "Uploaded image is empty or too small.")

    # 1a) OCR the chart header to detect pair and OTC status.
    det = detect_pair_from_image(data)
    detected_symbol = det.get("symbol")
    detected_otc = bool(det.get("is_otc"))
    detection_warning: Optional[str] = None

    if not symbol:
        # If no symbol provided, we MUST detect it from image.
        if detected_symbol and detected_symbol in ALLOWED_SYMBOLS:
            symbol = detected_symbol
            detection_warning = (
                f"Pair auto-detected from screenshot: {symbol}"
                + (" (OTC)" if detected_otc else "")
                + ". Data source: TradingView (MT5 Fallback)."
            )
        else:
            raise HTTPException(
                400,
                "Could not detect a trading pair from the uploaded chart. "
                "Please pick a pair manually.",
            )
    else:
        # Symbol was provided manually. Just check for mismatch/OTC.
        if detected_symbol and detected_symbol != symbol:
            detection_warning = (
                f"Mismatched pair? Screenshot appears to be {detected_symbol}"
                + (" (OTC)" if detected_otc else "")
                + f", but you selected {symbol}. Analyzing {symbol}."
            )
        elif detected_otc:
            detection_warning = f"Quotex OTC asset detected ({symbol})."

    sym = _validate_symbol(symbol)

    # 2) Fetch OHLC for 1H, 15M, 5M (Respecting .env configuration)
    bars = int(max(60, min(bars, 1000)))
    series = {}
    source = "Unavailable"

    primary = (os.getenv("DATA_SOURCE_PRIMARY") or "tradingview").lower()
    fallback = (os.getenv("DATA_SOURCE_FALLBACK") or "mt5").lower()

    # Try sources in order (Primary -> Fallback -> Guest Fallback)
    for current_source_key in [primary, fallback, "tradingview_guest"]:
        try:
            if current_source_key == "tradingview":
                source = "TradingView"
                for tf in ("1H", "15M", "5M"):
                    candles, _ = get_ohlc(sym, "OANDA", tf, bars=bars)
                    if not candles or len(candles) < 30:
                        raise RuntimeError(f"TradingView: Not enough candles for {tf}.")
                    series[tf] = candles
                break  # Success!
            elif current_source_key == "mt5":
                from services.mt5_data import get_mt5_ohlc
                source = "MetaTrader5"
                for tf in ("1H", "15M", "5M"):
                    candles = get_mt5_ohlc(sym, tf, bars=bars)
                    if not candles or len(candles) < 30:
                        raise RuntimeError(f"MT5: Not enough candles for {tf}.")
                    series[tf] = candles
                break  # Success!
            elif current_source_key == "tradingview_guest":
                source = "TradingView (Guest Mode)"
                for tf in ("1H", "15M", "5M"):
                    candles, _ = get_ohlc(sym, "OANDA", tf, bars=bars, force_guest=True)
                    if not candles or len(candles) < 30:
                        raise RuntimeError(f"TradingView Guest: Not enough candles for {tf}.")
                    series[tf] = candles
                break  # Success!
        except Exception as e:
            logger.warning("%s fetch failed: %s", current_source_key.capitalize(), e)
            continue
    else:
        # Loop finished without breaking -> all sources failed
        raise HTTPException(502, f"OHLC data unavailable from {primary} and {fallback}")

    # 3) Image analysis
    image_result = analyze_chart_image(data)

    # 4) Decision
    decision = make_decision(
        h1_candles=series["1H"],
        m15_candles=series["15M"],
        m5_candles=series["5M"],
        image=image_result,
    )

    # 5) Image-trumping rules from spec
    if image_result.get("image_quality") == "LOW":
        decision["decision"] = "NO TRADE"
        decision["confidence"] = min(decision["confidence"], 50)
        if "Image quality is LOW — visual confirmation cannot be trusted." not in decision["warnings"]:
            decision["warnings"].append("Image quality is LOW — visual confirmation cannot be trusted.")

    # Hard cap per spec
    if decision["confidence"] > 85:
        decision["confidence"] = 85
    if decision["decision"] == "NO TRADE" and decision["confidence"] > 60:
        decision["confidence"] = 60


    if detection_warning:
        decision["warnings"].insert(0, detection_warning)
    if detected_otc:
        decision["warnings"].append(
            "Quotex OTC asset detected — TradingView OHLC may NOT match Quotex OTC prices."
        )

    last_5m = series["5M"][-10:]
    return AnalyzeResponse(
        decision=decision["decision"],
        confidence=decision["confidence"],
        reason=decision["reason"],
        evidence=Evidence(**decision["evidence"]),
        warnings=decision["warnings"],
        candles_preview=[Candle(**c) for c in last_5m],
        data_source=source,
    )


# ---------------------------------------------------------------------------
# Static frontend (production build)
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))
_FRONTEND_DIST = os.path.normpath(os.path.join(_HERE, "..", "frontend", "dist"))


@app.get("/")
def root_index():
    """Serve the SPA index (or a friendly placeholder if not built yet)."""
    index_path = os.path.join(_FRONTEND_DIST, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(
        {
            "status": "backend running",
            "message": (
                "Frontend has not been built yet. "
                "Run `cd frontend && npm install && npm run build` "
                "or use the Vite dev server."
            ),
        }
    )


# Mount static files LAST so /api/* routes still match first.
if os.path.isdir(_FRONTEND_DIST):
    # Serve compiled assets (vite places them under /assets/ by default).
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(_FRONTEND_DIST, "assets")),
        name="assets",
    )

    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str):
        # Don't shadow API routes
        if full_path.startswith("api/"):
            raise HTTPException(404)
        candidate = os.path.join(_FRONTEND_DIST, full_path)
        if os.path.isfile(candidate):
            return FileResponse(candidate)
        index_path = os.path.join(_FRONTEND_DIST, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        raise HTTPException(404)
