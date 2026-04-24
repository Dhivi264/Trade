"""Image analysis for uploaded Quotex chart screenshots.

This module performs LIGHTWEIGHT visual inspection only — it does NOT
attempt to extract exact OHLC values from a screenshot (that requires
price-axis calibration which we don't have).

What we infer:
  * image quality   (LOW / MEDIUM / HIGH) from sharpness and resolution
  * visual bias     (BULLISH / BEARISH / RANGE / UNKNOWN) from the
                    distribution and position of bullish vs bearish
                    candle pixels across the image
  * visual notes    short, human-readable observations
"""

from __future__ import annotations

from io import BytesIO
from typing import Dict, List, Tuple

import cv2
import numpy as np
from PIL import Image


# HSV ranges that capture the typical chart palettes used by Quotex /
# TradingView candles. Quotex defaults to bright green / red, but we
# include a wider range so other themes still classify reasonably.
_GREEN_RANGES = [
    (np.array([35, 50, 50]), np.array([90, 255, 255])),     # green
    (np.array([85, 40, 80]), np.array([105, 255, 255])),    # teal/cyan-ish
]
_RED_RANGES = [
    (np.array([0, 70, 50]), np.array([10, 255, 255])),      # red (low hue)
    (np.array([170, 70, 50]), np.array([180, 255, 255])),   # red (high hue)
    (np.array([10, 90, 80]), np.array([20, 255, 255])),     # orange-ish red
]


def _read_image(file_bytes: bytes) -> np.ndarray:
    """Decode bytes into an OpenCV BGR image."""
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        # PIL fallback for less common encodings (e.g. some webp variants)
        pil = Image.open(BytesIO(file_bytes)).convert("RGB")
        img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    return img


def _mask_for_ranges(hsv: np.ndarray, ranges) -> np.ndarray:
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for lo, hi in ranges:
        mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lo, hi))
    return mask


def _quality(img: np.ndarray) -> Tuple[str, float]:
    """Classify image sharpness/resolution into LOW/MEDIUM/HIGH."""
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Variance of Laplacian = sharpness proxy
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    # Score combines resolution and sharpness
    long_side = max(h, w)
    if long_side < 480 or sharpness < 25:
        return "LOW", sharpness
    if long_side < 900 or sharpness < 80:
        return "MEDIUM", sharpness
    return "HIGH", sharpness


def _direction_from_split(green_mask: np.ndarray, red_mask: np.ndarray) -> Tuple[str, Dict[str, float]]:
    """Look at green vs red density across left/right halves.

    If the right half has materially more bullish pixels than the left,
    that's a BULLISH visual bias and vice versa.
    """
    h, w = green_mask.shape
    half = w // 2
    g_left = float(green_mask[:, :half].sum())
    g_right = float(green_mask[:, half:].sum())
    r_left = float(red_mask[:, :half].sum())
    r_right = float(red_mask[:, half:].sum())
    total_g = g_left + g_right
    total_r = r_left + r_right
    total = total_g + total_r

    info = {
        "green_pixels": total_g,
        "red_pixels": total_r,
        "green_left": g_left,
        "green_right": g_right,
        "red_left": r_left,
        "red_right": r_right,
    }

    if total < 1000:
        return "UNKNOWN", info

    # Net bullishness on each half
    net_left = g_left - r_left
    net_right = g_right - r_right

    # Strong bias: right half clearly more bullish (or bearish) than left
    diff = net_right - net_left
    norm = max(total * 0.05, 1.0)
    score = diff / norm

    # Also consider the overall green/red ratio
    ratio = (total_g - total_r) / total

    if abs(score) < 0.15 and abs(ratio) < 0.05:
        return "RANGE", info
    if score > 0.2 or (ratio > 0.15 and net_right >= 0):
        return "BULLISH", info
    if score < -0.2 or (ratio < -0.15 and net_right <= 0):
        return "BEARISH", info
    return "UNKNOWN", info


def analyze_chart_image(file_bytes: bytes) -> Dict:
    """Main entrypoint. Returns the public ImageAnalysis dict."""
    img = _read_image(file_bytes)
    if img is None or img.size == 0:
        return {
            "image_quality": "LOW",
            "visual_bias": "UNKNOWN",
            "visual_notes": ["Image could not be decoded."],
        }

    quality_label, sharpness = _quality(img)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    green_mask = _mask_for_ranges(hsv, _GREEN_RANGES)
    red_mask = _mask_for_ranges(hsv, _RED_RANGES)

    # Suppress UI/background noise via a small open op
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)

    bias, info = _direction_from_split(green_mask, red_mask)

    notes: List[str] = []
    h, w = img.shape[:2]
    notes.append(f"Resolution: {w}x{h}, sharpness score: {sharpness:.1f}")

    total = info["green_pixels"] + info["red_pixels"]
    if total > 0:
        gp = 100.0 * info["green_pixels"] / total
        rp = 100.0 * info["red_pixels"] / total
        notes.append(f"Bullish pixel share: {gp:.1f}%, bearish: {rp:.1f}%")

    # Detect impulse vs compression via vertical column variance
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    col_std = float(np.std(gray.std(axis=0)))
    if col_std < 8:
        notes.append("Chart looks compressed / sideways (low column variance).")
    elif col_std > 28:
        notes.append("Chart shows strong vertical movement (possible impulse).")

    if quality_label == "LOW":
        notes.append("Low image quality reduces visual confidence.")

    if bias == "UNKNOWN":
        notes.append("Could not determine a clear visual bias.")

    return {
        "image_quality": quality_label,
        "visual_bias": bias,
        "visual_notes": notes,
    }
