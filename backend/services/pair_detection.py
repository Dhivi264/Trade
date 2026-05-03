"""Detect the trading pair (and OTC flag) from an uploaded Quotex
chart screenshot using OCR.

Quotex charts always render the asset name as text in the top-left
of the screen (e.g. "EUR/USD", "EUR/USD OTC", "GBP/JPY OTC 92%").
We OCR the top strip of the image, scan for known currency pairs,
and report back what we found together with a confidence score.

Returns a dict shaped like:
    {
        "symbol":     "EURUSD" | None,
        "is_otc":     bool,
        "raw_text":   "<the raw OCR result>",
        "confidence": 0..100,
        "candidates": ["EURUSD", "GBPJPY", ...],
    }
"""

from __future__ import annotations

import logging
import os
import re
import shutil
from io import BytesIO
from typing import Dict, List, Optional

import cv2
import numpy as np
from PIL import Image


def _ensure_tessdata() -> None:
    """Some Nix profiles ship a leftover empty tessdata directory that
    `tesseract` finds before the real one. Point TESSDATA_PREFIX at a
    directory that actually contains `eng.traineddata` so OCR doesn't
    hang trying to load missing language files."""
    if os.environ.get("TESSDATA_PREFIX"):
        return
    binary = shutil.which("tesseract")
    if not binary:
        return
    # Resolve symlinks (Nix wraps binaries in profile dirs that
    # symlink into /nix/store) and walk up to <prefix>/share/tessdata.
    real = os.path.realpath(binary)
    prefix = os.path.dirname(os.path.dirname(real))
    candidate = os.path.join(prefix, "share", "tessdata")
    if os.path.exists(os.path.join(candidate, "eng.traineddata")):
        os.environ["TESSDATA_PREFIX"] = candidate


_ensure_tessdata()

try:
    import pytesseract  # type: ignore
    # Verify the binary is actually available in the PATH
    pytesseract.get_tesseract_version()
    _OCR_AVAILABLE = True
except Exception:
    _OCR_AVAILABLE = False
    pytesseract = None

logger = logging.getLogger("chart_evidence.pair_detection")

# Pairs we currently support in the rule engine.
# This mirrors the non-OTC FX list available on the Quotex platform,
# plus a small set of metals/crypto we already wire up to TradingView.
SUPPORTED_PAIRS: List[str] = [
    # Quotex non-OTC FX
    "EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDJPY", "USDCAD", "USDCHF",
    "EURJPY", "GBPJPY", "AUDJPY", "CADJPY", "CHFJPY", "NZDJPY",
    "EURGBP", "EURAUD", "EURCAD", "EURCHF", "EURNZD",
    "GBPAUD", "GBPCAD", "GBPCHF", "GBPNZD",
    "AUDCAD", "AUDCHF", "AUDNZD", "CADCHF",
    # Extras (metals, crypto) — auto-detected when present
    "XAUUSD", "XAGUSD",
    "BTCUSD", "ETHUSD", "LTCUSD", "XRPUSD",
]

# Common OCR misreads — fold them back to the right character.
_OCR_FIXES = str.maketrans({
    "0": "O", "1": "I", "5": "S", "8": "B",
    "|": "I", "!": "I",
})

# Best-effort symbol → exchange hint. Forex pairs default to OANDA;
# crypto to BINANCE; metals to FOREXCOM. The frontend may still
# override.
_EXCHANGE_HINT = {
    **{p: "BINANCE" for p in ("BTCUSD", "ETHUSD", "LTCUSD", "XRPUSD")},
    **{p: "FOREXCOM" for p in ("XAUUSD", "XAGUSD")},
}


def _decode(file_bytes: bytes) -> Optional[np.ndarray]:
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        try:
            pil = Image.open(BytesIO(file_bytes)).convert("RGB")
            img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
        except Exception:
            return None
    if img is None or img.size == 0:
        return None
    return img


def _binarize(region: np.ndarray) -> np.ndarray:
    """Return a high-contrast B/W version of `region` for OCR."""
    longest = max(region.shape[:2])
    # Upscale tiny regions so tesseract has something to chew on,
    # but cap the result to keep OCR latency bounded.
    if longest < 600:
        scale = 600 / longest
    elif longest > 1400:
        scale = 1400 / longest
    else:
        scale = 1.0
    if scale != 1.0:
        region = cv2.resize(region, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)

    # Try both polarities — Quotex uses light-on-dark for headers and
    # dark-on-light for some info panels. Pick the one with fewer ink
    # pixels (cleaner text).
    _, dark_on_light = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    light_on_dark = cv2.bitwise_not(dark_on_light)

    def _ink(b: np.ndarray) -> int:
        return int(np.count_nonzero(b == 0))

    chosen = dark_on_light if _ink(dark_on_light) < _ink(light_on_dark) else light_on_dark
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    return cv2.morphologyEx(chosen, cv2.MORPH_CLOSE, kernel)


def _ocr_regions(file_bytes: bytes) -> List[np.ndarray]:
    """Return preprocessed images of the regions where Quotex draws
    the asset name. Quotex web/desktop renders the pair top-left.
    Quotex mobile renders the active asset on a bottom info bar, so
    on tall (portrait) screenshots we also OCR the bottom strip."""
    img = _decode(file_bytes)
    if img is None:
        return []

    h, w = img.shape[:2]
    regions = []

    # Top header — always scanned. Top 22%, left 60% keeps the OCR
    # fast and avoids the price-axis on the right.
    top = img[: max(60, int(h * 0.22)), : max(200, int(w * 0.60))]
    regions.append(_binarize(top))

    # Mobile / portrait screenshot: also scan the bottom info bar.
    if h > w * 1.3:
        bottom = img[int(h * 0.78):, : max(200, int(w * 0.70))]
        if bottom.size > 0:
            regions.append(_binarize(bottom))

    return regions


def _normalize(s: str) -> str:
    # Keep letters/digits/slash/space only, then upper-case
    cleaned = re.sub(r"[^A-Za-z0-9/ ]", " ", s).upper()
    cleaned = cleaned.translate(_OCR_FIXES)
    return re.sub(r"\s+", " ", cleaned).strip()


def _scan_for_pairs(text: str) -> List[str]:
    """Return supported pairs found in text, in order of appearance."""
    found: List[str] = []
    norm = _normalize(text)
    # Try both with and without slash variants
    candidates = set()
    # Direct match
    for pair in SUPPORTED_PAIRS:
        a, b = pair[:3], pair[3:]
        # Match "EUR/USD", "EUR USD", "EUR-USD" or plain "EURUSD".
        # We don't require word boundaries because OCR routinely
        # merges the surrounding glyphs (e.g. "vrQEUR/JPY",
        # "EURUSDOTE"). Six-letter currency codes are specific
        # enough that incidental substring matches are very rare.
        pattern = rf"{a}\s*[/\- ]?\s*{b}"
        if re.search(pattern, norm):
            if pair not in candidates:
                found.append(pair)
                candidates.add(pair)
    return found


def detect_pair_from_image(file_bytes: bytes) -> Dict:
    """Run OCR on the top strip and return the best candidate pair."""
    if not _OCR_AVAILABLE:
        return {
            "symbol": None,
            "exchange": None,
            "is_otc": False,
            "raw_text": "",
            "confidence": 0,
            "candidates": [],
            "reason": "OCR engine (tesseract) is not available on this host.",
        }

    regions = _ocr_regions(file_bytes)
    if not regions:
        return {
            "symbol": None,
            "exchange": None,
            "is_otc": False,
            "raw_text": "",
            "confidence": 0,
            "candidates": [],
            "reason": "Image could not be decoded for OCR.",
        }

    # PSM 6 = "assume a single uniform block of text" — works well on
    # the densely-packed Quotex header. Restrict character set to
    # alphanumerics + a couple of separators.
    config = (
        "--oem 3 --psm 6 "
        "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/-% "
    )
    raw_text_parts: List[str] = []
    for region in regions:
        try:
            chunk = pytesseract.image_to_string(region, config=config) or ""
        except Exception as exc:
            logger.warning("OCR failed on region: %s", exc)
            chunk = ""
        if chunk.strip():
            raw_text_parts.append(chunk.strip())
    raw_text = "\n".join(raw_text_parts)

    norm = _normalize(raw_text)
    candidates = _scan_for_pairs(raw_text)

    # Tesseract sometimes reads "OTC" as "OTE", "0TC", "OTG" etc.
    is_otc = bool(re.search(r"OT[CGE0Q]", norm))

    symbol: Optional[str] = candidates[0] if candidates else None
    exchange = _EXCHANGE_HINT.get(symbol or "") if symbol else None

    if symbol is None:
        confidence = 0
        reason = "Could not find a known pair name in the chart header."
    else:
        # Confidence heuristic: more candidates = noisier OCR but at
        # least one matched. OTC text being present is a small bonus.
        base = 70 if len(candidates) == 1 else 55
        if is_otc:
            base += 10
        confidence = min(base, 90)
        reason = f"Detected '{symbol}' in chart header text."

    return {
        "symbol": symbol,
        "exchange": exchange,
        "is_otc": is_otc,
        "raw_text": raw_text.strip(),
        "confidence": confidence,
        "candidates": candidates,
        "reason": reason,
    }
