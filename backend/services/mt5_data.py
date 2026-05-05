"""MetaTrader 5 OHLC fetching service.

Used as a fallback if TradingView data is unavailable.
Requires the `MetaTrader5` package and a running MT5 terminal on Windows.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("chart_evidence.mt5_data")

MT5_AVAILABLE = False
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False


def _mt5_interval(timeframe: str):
    if not MT5_AVAILABLE:
        return None
    tf = timeframe.upper()
    mapping = {
        "1M": mt5.TIMEFRAME_M1,
        "5M": mt5.TIMEFRAME_M5,
        "15M": mt5.TIMEFRAME_M15,
        "30M": mt5.TIMEFRAME_M30,
        "1H": mt5.TIMEFRAME_H1,
        "4H": mt5.TIMEFRAME_H4,
        "1D": mt5.TIMEFRAME_D1,
    }
    return mapping.get(tf)


def get_mt5_ohlc(
    symbol: str,
    timeframe: str,
    bars: int = 300,
) -> Optional[List[Dict[str, Any]]]:
    """Fetch OHLC candles from MetaTrader 5."""
    if not MT5_AVAILABLE:
        logger.warning("MetaTrader5 package not installed.")
        return None

    # MT5 credentials from environment
    login_str = os.getenv("MT5_LOGIN", "0").strip()
    if login_str and not login_str.isdigit():
        logger.error("MT5_LOGIN must be a numeric account number. Found: '%s'", login_str)
        return None

    login = int(login_str) if login_str.isdigit() else 0
    password = os.getenv("MT5_PASSWORD", "").strip()
    server = os.getenv("MT5_SERVER", "").strip()

    initialized = False
    if login:
        initialized = mt5.initialize(login=login, password=password, server=server)
    else:
        initialized = mt5.initialize()

    if not initialized:
        err = mt5.last_error()
        if err[0] == -10003:
            logger.error("MT5 initialization failed: MetaTrader 5 terminal not found. Please ensure the MT5 application is running.")
        else:
            logger.error("mt5.initialize() failed, error code = %s", err)
        return None

    try:
        interval = _mt5_interval(timeframe)
        if interval is None:
            logger.error("Unsupported timeframe for MT5: %s", timeframe)
            return None

        # MT5 symbols often differ (e.g., EURUSD vs EURUSD.m)
        # We try the provided symbol directly first.
        mt5.symbol_select(symbol, True)
        rates = mt5.copy_rates_from_pos(symbol, interval, 0, bars)
        
        if rates is None or len(rates) == 0:
            # Try variations: GBP/JPY, GBPJPY.m, GBPJPY.pro, GBPJPY_otc
            variations = [
                symbol[:3] + "/" + symbol[3:] if len(symbol) == 6 else None,
                symbol + ".m",
                symbol + ".pro",
                symbol + "_otc",
                symbol + ".." # Some brokers use this
            ]
            for alt in variations:
                if not alt: continue
                mt5.symbol_select(alt, True)
                rates = mt5.copy_rates_from_pos(alt, interval, 0, bars)
                if rates is not None and len(rates) > 0:
                    symbol = alt
                    break

        if rates is None or len(rates) == 0:
            logger.warning("MT5 returned no rates for %s (and tried variations)", symbol)
            return None

        out: List[Dict[str, Any]] = []
        for r in rates:
            # MT5 time is a posix timestamp
            dt = datetime.fromtimestamp(r['time'], tz=timezone.utc)
            out.append({
                "time": dt.strftime("%Y-%m-%d %H:%M"),
                "open": float(r['open']),
                "high": float(r['high']),
                "low": float(r['low']),
                "close": float(r['close']),
                "volume": float(r['tick_volume']),
            })
        return out
    finally:
        mt5.shutdown()
