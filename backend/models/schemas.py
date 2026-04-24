"""Pydantic schemas used by the Chart Evidence Analyzer API."""

from typing import Any, List, Optional

from pydantic import BaseModel


class Candle(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


class CandlesResponse(BaseModel):
    symbol: str
    exchange: str
    timeframe: str
    candles: List[Candle]
    source: str  # "tvdatafeed" or "csv-fallback" or "synthetic"


class ImageAnalysis(BaseModel):
    image_quality: str  # HIGH / MEDIUM / LOW
    visual_bias: str  # BULLISH / BEARISH / RANGE / UNKNOWN
    visual_notes: List[str]


class Evidence(BaseModel):
    one_hour_trend: str
    fifteen_min_structure: str
    five_min_move: str
    image_bias: str
    image_quality: str
    support_resistance: List[Any]


class AnalyzeResponse(BaseModel):
    decision: str  # BUY / SELL / NO TRADE
    confidence: int  # 0-100
    reason: str
    evidence: Evidence
    warnings: List[str]
    candles_preview: Optional[List[Candle]] = None
    data_source: Optional[str] = None
