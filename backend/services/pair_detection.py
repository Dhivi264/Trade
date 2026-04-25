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
import re
from io import BytesIO
from typing import Dict, List, Optional

import cv2
import numpy as np
from PIL import Image

try:
    import pytesseract  # type: ignore
    _OCR_AVAILABLE = True
except Exception:  # pragma: no cover - tesseract optional
    pytesseract = None
    _OCR_AVAILABLE = False

logger = logging.getLogger("chart_evidence.pair_detection")

# Pairs we currently support in the rule engine. Extend as the
# product expands.
SUPPORTED_PAIRS: List[str] = [
    "EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDJPY", "USDCAD", "USDCHF",
    "EURJPY", "GBPJPY", "AUDJPY", "EURGBP", "EURAUD", "EURNZD", "EURCHF",
    "GBPAUD", "GBPCAD", "GBPCHF", "AUDNZD", "AUDCAD", "AUDCHF",
    "NZDJPY", "CADJPY", "CHFJPY", "NZDCAD",
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


def _preprocess_top_strip(file_bytes: bytes) -> Optional[np.ndarray]:
    """Return a high-contrast grayscale of the top ~18% of the chart."""
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

    h, w = img.shape[:2]
    # Quotex always shows the asset name top-left. Crop the top 18%
    # and the left 60% for cleaner OCR with fewer false positives.
    top = img[: max(60, int(h * 0.18)), : max(200, int(w * 0.6))]

    # Upscale tiny screenshots so tesseract has something to chew on.
    if max(top.shape[:2]) < 600:
        scale = 600 / max(top.shape[:2])
        top = cv2.resize(top, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(top, cv2.COLOR_BGR2GRAY)

    # Quotex uses light text on a dark background. Both polarities
    # are tried; the one with more letter-like contours wins.
    _, dark_on_light = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    light_on_dark = cv2.bitwise_not(dark_on_light)

    def _score(b: np.ndarray) -> int:
        # Heuristic: count "ink" pixels — fewer is better for OCR
        # on top of dark UI chrome, but not too few.
        return int(np.count_nonzero(b == 0))

    chosen = dark_on_light if _score(dark_on_light) < _score(light_on_dark) else light_on_dark

    # Slight dilation joins broken letters
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    chosen = cv2.morphologyEx(chosen, cv2.MORPH_CLOSE, kernel)
    return chosen


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
        # No trailing word boundary because OCR commonly merges the
        # following token (e.g. "EURUSDOTC" -> "EURUSDOTE"); we just
        # require the pair starts on a word boundary.
        pattern = rf"(?:^|\W){a}\s*[/\- ]?\s*{b}"
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

    pre = _preprocess_top_strip(file_bytes)
    if pre is None:
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
    try:
        raw_text = pytesseract.image_to_string(pre, config=config) or ""
    except Exception as exc:
        logger.warning("OCR failed: %s", exc)
        raw_text = ""

    norm = _normalize(raw_text)
    candidates = _scan_for_pairs(raw_text)

    # Tesseract sometimes reads "OTC" as "OTE", "0TC", "OTG" etc.
    is_otc = bool(re.search(r"OT[CGE0Q]", norm))

    symbol: Optional[str] = candidates[0] if candidates else None
    exchange = _EXCHANGE_HINT.get(symbol or "", "OANDA") if symbol else None

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
