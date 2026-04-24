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

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from models.schemas import AnalyzeResponse, CandlesResponse, Candle, Evidence, ImageAnalysis
from services.image_analysis import analyze_chart_image
from services.rule_engine import make_decision
from services.tv_data import get_demo_ohlc, get_ohlc

logger = logging.getLogger("chart_evidence")
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOWED_SYMBOLS = {
    "EURUSD", "GBPUSD", "AUDJPY", "USDJPY", "EURJPY",
    "GBPJPY", "USDCAD", "XAUUSD", "BTCUSD", "ETHUSD",
}
ALLOWED_EXCHANGES = {"OANDA", "FX_IDC", "FOREXCOM", "BINANCE"}
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


def _validate_exchange(exchange: str) -> str:
    e = (exchange or "").upper().strip()
    if e not in ALLOWED_EXCHANGES:
        raise HTTPException(400, f"Unsupported exchange '{exchange}'.")
    return e


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


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(
    symbol: str = Form(...),
    exchange: str = Form(...),
    bars: int = Form(300),
    demo: bool = Form(False),
    image: UploadFile = File(...),
):
    sym = _validate_symbol(symbol)
    exch = _validate_exchange(exchange)

    # 1) Validate + read image
    if image.content_type not in ALLOWED_MIME:
        raise HTTPException(400, f"Unsupported file type '{image.content_type}'.")
    data = await image.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Uploaded image exceeds 8 MB limit.")
    if len(data) < 200:
        raise HTTPException(400, "Uploaded image is empty or too small.")

    # 2) Fetch OHLC for 1H, 15M, 5M
    bars = int(max(60, min(bars, 1000)))
    series = {}
    source = None
    try:
        if demo:
            for tf in ("1H", "15M", "5M"):
                series[tf] = get_demo_ohlc(sym, tf, bars)
            source = "synthetic"
        else:
            for tf in ("1H", "15M", "5M"):
                candles, src = get_ohlc(sym, exch, tf, bars=bars)
                if not candles or len(candles) < 30:
                    raise RuntimeError(f"Not enough candles for {tf}.")
                series[tf] = candles
                source = src
    except RuntimeError as exc:
        raise HTTPException(502, str(exc))

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

    if source == "synthetic":
        decision["warnings"].append(
            "DEMO data — synthetic OHLC. This decision is for UI testing only."
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
