"""OHLC analysis + final decision engine.

All thresholds are intentionally conservative — the spec calls for
NO TRADE by default unless several independent pieces of evidence
align. We never claim guaranteed profits or 90%+ confidence.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _arr(candles: List[Dict[str, Any]], key: str) -> np.ndarray:
    return np.asarray([float(c[key]) for c in candles], dtype=float)


def _find_swings(values: np.ndarray, kind: str = "high", left: int = 2, right: int = 2) -> List[int]:
    """Return indices of swing highs (kind='high') or lows (kind='low')."""
    out: List[int] = []
    if len(values) < left + right + 1:
        return out
    for i in range(left, len(values) - right):
        window = values[i - left : i + right + 1]
        if kind == "high" and values[i] == window.max() and (window == values[i]).sum() == 1:
            out.append(i)
        if kind == "low" and values[i] == window.min() and (window == values[i]).sum() == 1:
            out.append(i)
    return out


# ---------------------------------------------------------------------------
# Trend / structure
# ---------------------------------------------------------------------------

def analyze_trend(candles: List[Dict[str, Any]]) -> str:
    """Return BULLISH / BEARISH / RANGE / UNCLEAR."""
    if not candles or len(candles) < 30:
        return "UNCLEAR"
    highs = _arr(candles, "high")
    lows = _arr(candles, "low")
    closes = _arr(candles, "close")

    swing_highs = _find_swings(highs, "high", 3, 3)[-4:]
    swing_lows = _find_swings(lows, "low", 3, 3)[-4:]

    bullish_struct = (
        len(swing_highs) >= 2
        and len(swing_lows) >= 2
        and highs[swing_highs[-1]] > highs[swing_highs[-2]]
        and lows[swing_lows[-1]] > lows[swing_lows[-2]]
    )
    bearish_struct = (
        len(swing_highs) >= 2
        and len(swing_lows) >= 2
        and highs[swing_highs[-1]] < highs[swing_highs[-2]]
        and lows[swing_lows[-1]] < lows[swing_lows[-2]]
    )

    # Slope of the last ~50 closes via simple linear fit (normalised)
    n = min(50, len(closes))
    seg = closes[-n:]
    x = np.arange(n)
    slope = float(np.polyfit(x, seg, 1)[0])
    rng = max(float(seg.max() - seg.min()), 1e-9)
    norm_slope = slope * n / rng  # ~ how much of the range slope covers

    if bullish_struct and norm_slope > 0.15:
        return "BULLISH"
    if bearish_struct and norm_slope < -0.15:
        return "BEARISH"
    if abs(norm_slope) < 0.08:
        return "RANGE"
    if norm_slope > 0.25:
        return "BULLISH"
    if norm_slope < -0.25:
        return "BEARISH"
    return "UNCLEAR"


def detect_impulse(candles: List[Dict[str, Any]]) -> str:
    """Detect unusually large candles vs recent average body size.

    Returns NORMAL / BULLISH_IMPULSE / BEARISH_IMPULSE / OVEREXTENDED.
    """
    if not candles or len(candles) < 20:
        return "NORMAL"
    opens = _arr(candles, "open")
    closes = _arr(candles, "close")
    bodies = np.abs(closes - opens)
    avg = float(np.mean(bodies[-30:])) or 1e-9
    last_body = float(bodies[-1])
    last_dir = 1 if closes[-1] > opens[-1] else -1

    # Last few candles all same direction with growing bodies = overextended
    last5_dirs = np.sign(closes[-5:] - opens[-5:])
    if np.all(last5_dirs == last5_dirs[-1]) and last5_dirs[-1] != 0:
        recent_avg_body = float(np.mean(bodies[-5:]))
        if recent_avg_body > avg * 1.6:
            return "OVEREXTENDED"

    if last_body > avg * 2.0:
        return "BULLISH_IMPULSE" if last_dir > 0 else "BEARISH_IMPULSE"
    return "NORMAL"


def detect_support_resistance(candles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify recent swing highs / lows as approximate S/R zones."""
    if not candles or len(candles) < 20:
        return []
    highs = _arr(candles, "high")
    lows = _arr(candles, "low")
    sh = _find_swings(highs, "high", 3, 3)[-3:]
    sl = _find_swings(lows, "low", 3, 3)[-3:]
    zones: List[Dict[str, Any]] = []
    for i in sh:
        zones.append({"type": "resistance", "price": round(float(highs[i]), 5), "index": int(i)})
    for i in sl:
        zones.append({"type": "support", "price": round(float(lows[i]), 5), "index": int(i)})
    zones.sort(key=lambda z: z["price"], reverse=True)
    return zones


def detect_current_move(candles: List[Dict[str, Any]]) -> str:
    """Look at the last 5–10 candles. Returns BUY_PRESSURE / SELL_PRESSURE / WEAK / MIXED."""
    if not candles or len(candles) < 10:
        return "WEAK"
    last = candles[-10:]
    opens = _arr(last, "open")
    closes = _arr(last, "close")
    bodies = closes - opens
    bull = int((bodies > 0).sum())
    bear = int((bodies < 0).sum())
    net = float(bodies.sum())
    range_ = float(np.max(_arr(last, "high")) - np.min(_arr(last, "low"))) or 1e-9
    norm_net = net / range_

    if bull >= 7 and norm_net > 0.15:
        return "BUY_PRESSURE"
    if bear >= 7 and norm_net < -0.15:
        return "SELL_PRESSURE"
    if abs(bull - bear) <= 2 and abs(norm_net) < 0.1:
        return "MIXED"
    if bull > bear and norm_net > 0.05:
        return "BUY_PRESSURE"
    if bear > bull and norm_net < -0.05:
        return "SELL_PRESSURE"
    return "WEAK"


# ---------------------------------------------------------------------------
# Position vs. range
# ---------------------------------------------------------------------------

def _is_mid_range(candles: List[Dict[str, Any]]) -> bool:
    """True if the current close is in the mid 30% of the recent N-bar range."""
    if not candles or len(candles) < 30:
        return False
    seg = candles[-50:]
    highs = _arr(seg, "high")
    lows = _arr(seg, "low")
    hi = float(highs.max())
    lo = float(lows.min())
    if hi - lo < 1e-9:
        return True
    pos = (float(seg[-1]["close"]) - lo) / (hi - lo)
    return 0.35 <= pos <= 0.65


# ---------------------------------------------------------------------------
# Final decision engine
# ---------------------------------------------------------------------------

def make_decision(
    h1_candles: List[Dict[str, Any]],
    m15_candles: List[Dict[str, Any]],
    m5_candles: List[Dict[str, Any]],
    image: Dict[str, Any],
) -> Dict[str, Any]:
    """Combine all evidence into the final decision payload."""
    warnings: List[str] = []

    h1_trend = analyze_trend(h1_candles)
    m15_trend = analyze_trend(m15_candles)
    m5_move = detect_current_move(m5_candles)
    m5_impulse = detect_impulse(m5_candles)
    sr_zones = detect_support_resistance(m15_candles)

    image_bias = (image or {}).get("visual_bias", "UNKNOWN")
    image_quality = (image or {}).get("image_quality", "LOW")

    mid_range = _is_mid_range(m5_candles)
    overextended = m5_impulse == "OVEREXTENDED"

    decision = "NO TRADE"
    reason_parts: List[str] = []
    confidence = 30

    # Hard guard rails ------------------------------------------------------
    if image_quality == "LOW":
        warnings.append("Image quality is LOW — visual confirmation cannot be trusted.")
        return _package(
            decision="NO TRADE",
            confidence=min(50, confidence),
            reason="Uploaded chart screenshot is too low quality for confirmation.",
            h1_trend=h1_trend,
            m15_trend=m15_trend,
            m5_move=m5_move,
            image_bias=image_bias,
            image_quality=image_quality,
            sr_zones=sr_zones,
            warnings=warnings,
        )

    if h1_trend in ("RANGE", "UNCLEAR") or m15_trend in ("RANGE", "UNCLEAR"):
        warnings.append("Higher-timeframe structure is unclear or ranging.")
        return _package(
            decision="NO TRADE",
            confidence=35,
            reason="Higher timeframe trend is RANGE/UNCLEAR — no high-quality setup.",
            h1_trend=h1_trend,
            m15_trend=m15_trend,
            m5_move=m5_move,
            image_bias=image_bias,
            image_quality=image_quality,
            sr_zones=sr_zones,
            warnings=warnings,
        )

    # Disagreement check between OHLC trend and image bias
    ohlc_dir = "BULL" if h1_trend == "BULLISH" else "BEAR"
    img_dir = None
    if image_bias == "BULLISH":
        img_dir = "BULL"
    elif image_bias == "BEARISH":
        img_dir = "BEAR"
    if img_dir is not None and img_dir != ohlc_dir:
        warnings.append("TradingView OHLC trend disagrees with the screenshot's visual bias.")
        return _package(
            decision="NO TRADE",
            confidence=40,
            reason="Conflicting evidence between OHLC data and uploaded screenshot.",
            h1_trend=h1_trend,
            m15_trend=m15_trend,
            m5_move=m5_move,
            image_bias=image_bias,
            image_quality=image_quality,
            sr_zones=sr_zones,
            warnings=warnings,
        )

    # Aligned evidence checks ----------------------------------------------
    bullish_aligned = (
        h1_trend == "BULLISH"
        and m15_trend == "BULLISH"
        and m5_move == "BUY_PRESSURE"
        and image_bias in ("BULLISH", "UNKNOWN")
        and not overextended
        and not mid_range
    )
    bearish_aligned = (
        h1_trend == "BEARISH"
        and m15_trend == "BEARISH"
        and m5_move == "SELL_PRESSURE"
        and image_bias in ("BEARISH", "UNKNOWN")
        and not overextended
        and not mid_range
    )

    if bullish_aligned:
        decision = "BUY"
        confidence = 70
        reason_parts.append("1H bullish, 15M bullish, 5M shows buy pressure.")
        if image_bias == "BULLISH":
            confidence += 10
            reason_parts.append("Screenshot visually confirms bullish bias.")
        if image_quality == "HIGH":
            confidence += 5
    elif bearish_aligned:
        decision = "SELL"
        confidence = 70
        reason_parts.append("1H bearish, 15M bearish, 5M shows sell pressure.")
        if image_bias == "BEARISH":
            confidence += 10
            reason_parts.append("Screenshot visually confirms bearish bias.")
        if image_quality == "HIGH":
            confidence += 5
    else:
        warnings.append("Evidence not fully aligned across timeframes.")
        if mid_range:
            warnings.append("Price is in the mid-range — wait for displacement.")
        if overextended:
            warnings.append("Last several candles look overextended — risk of reversal.")
        return _package(
            decision="NO TRADE",
            confidence=45,
            reason="Evidence does not align strongly across all timeframes.",
            h1_trend=h1_trend,
            m15_trend=m15_trend,
            m5_move=m5_move,
            image_bias=image_bias,
            image_quality=image_quality,
            sr_zones=sr_zones,
            warnings=warnings,
        )

    # Cap confidence per spec
    confidence = min(confidence, 85)
    if image_quality == "MEDIUM":
        confidence = min(confidence, 75)

    if not reason_parts:
        reason_parts.append("All independent signals are aligned.")
    return _package(
        decision=decision,
        confidence=confidence,
        reason=" ".join(reason_parts),
        h1_trend=h1_trend,
        m15_trend=m15_trend,
        m5_move=m5_move,
        image_bias=image_bias,
        image_quality=image_quality,
        sr_zones=sr_zones,
        warnings=warnings,
    )


def _package(
    *,
    decision: str,
    confidence: int,
    reason: str,
    h1_trend: str,
    m15_trend: str,
    m5_move: str,
    image_bias: str,
    image_quality: str,
    sr_zones: List[Dict[str, Any]],
    warnings: List[str],
) -> Dict[str, Any]:
    return {
        "decision": decision,
        "confidence": int(max(0, min(85, confidence))),
        "reason": reason,
        "evidence": {
            "one_hour_trend": h1_trend,
            "fifteen_min_structure": m15_trend,
            "five_min_move": m5_move,
            "image_bias": image_bias,
            "image_quality": image_quality,
            "support_resistance": sr_zones,
        },
        "warnings": warnings,
    }
