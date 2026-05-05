"""TradingView OHLC fetching service.

Tries to use `tvdatafeed` if installed. Falls back to a clear error
otherwise. Also supports a CSV fallback for offline/testing use.
"""

from __future__ import annotations

import csv
import io
import math
import os
import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

# --- Safe import of tvdatafeed ---------------------------------------------
TV_AVAILABLE = False
TvDatafeed = None  # type: ignore
Interval = None  # type: ignore
try:  # pragma: no cover - optional dependency
    from tvDatafeed import TvDatafeed, Interval  # type: ignore

    TV_AVAILABLE = True
except Exception:  # noqa: BLE001 - any import error means no tvdatafeed
    TV_AVAILABLE = False


_TV_INSTANCE: Optional[Any] = None
_TV_GUEST_INSTANCE: Optional[Any] = None


def _get_tv_client(force_guest: bool = False) -> Optional[Any]:
    """Get or create a TvDatafeed instance (authenticated or guest)."""
    global _TV_INSTANCE, _TV_GUEST_INSTANCE
    if not TV_AVAILABLE:
        return None

    if force_guest:
        if _TV_GUEST_INSTANCE is None:
            try:
                _TV_GUEST_INSTANCE = TvDatafeed()
            except Exception:
                pass
        return _TV_GUEST_INSTANCE

    if _TV_INSTANCE is None:
        try:
            username = (os.getenv("TV_USERNAME") or "").strip() or None
            password = (os.getenv("TV_PASSWORD") or "").strip() or None
            # If no username, it's guest mode by default
            _TV_INSTANCE = TvDatafeed(username=username, password=password)
        except Exception:
            # Internally tvdatafeed handles most errors by falling back to guest mode
            pass
    return _TV_INSTANCE


# Map the user-friendly timeframe to a tvdatafeed Interval (when available).
def _tv_interval(timeframe: str):
    if not TV_AVAILABLE:
        return None
    tf = timeframe.upper()
    mapping = {
        "1M": getattr(Interval, "in_1_minute", None),
        "5M": getattr(Interval, "in_5_minute", None),
        "15M": getattr(Interval, "in_15_minute", None),
        "30M": getattr(Interval, "in_30_minute", None),
        "1H": getattr(Interval, "in_1_hour", None),
        "4H": getattr(Interval, "in_4_hour", None),
        "1D": getattr(Interval, "in_daily", None),
    }
    return mapping.get(tf)


def _normalize_df(df) -> List[Dict[str, Any]]:
    """Convert a pandas DataFrame from tvdatafeed into our candle schema."""
    out: List[Dict[str, Any]] = []
    if df is None or len(df) == 0:
        return out
    for ts, row in df.iterrows():
        # Ensure time is in YYYY-MM-DD HH:mm format
        if hasattr(ts, "strftime"):
            time_str = ts.strftime("%Y-%m-%d %H:%M")
        else:
            time_str = str(ts)[:16].replace("T", " ")
            
        out.append(
            {
                "time": time_str,
                "open": float(row.get("open", 0)),
                "high": float(row.get("high", 0)),
                "low": float(row.get("low", 0)),
                "close": float(row.get("close", 0)),
                "volume": float(row.get("volume", 0) or 0),
            }
        )
    return out


def get_ohlc(
    symbol: str,
    exchange: str,
    timeframe: str,
    bars: int = 300,
    force_guest: bool = False,
) -> Tuple[List[Dict[str, Any]], str]:
    """Fetch OHLC candles for a symbol/exchange/timeframe.

    Returns (candles, source). If the live source is unavailable, raises
    `RuntimeError` with a user-friendly message that the API surface can
    forward to the frontend.
    """
    # 1) Try tvdatafeed
    if TV_AVAILABLE:
        try:
            interval = _tv_interval(timeframe)
            if interval is None:
                raise ValueError(f"Unsupported timeframe: {timeframe}")

            tv = _get_tv_client(force_guest=force_guest)
            if tv is None:
                raise RuntimeError("TradingView client could not be initialized.")

            # Check if login was requested but failed (unauthorized token)
            # We only raise this error if force_guest is False.
            username = (os.getenv("TV_USERNAME") or "").strip()
            if not force_guest and username and hasattr(tv, 'token') and str(tv.token).startswith('unauthorized'):
                # We log this specifically so the user knows why we are falling back to other sources
                raise RuntimeError(f"TradingView login failed for user '{username}'.")

            df = tv.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                n_bars=int(bars),
            )
            candles = _normalize_df(df)
            if not candles:
                raise RuntimeError("TradingView returned no candles.")
            return candles, "tvdatafeed"
        except Exception as exc:  # noqa: BLE001
            # fall through to CSV / synthetic fallbacks
            last_err = str(exc)
    else:
        last_err = "tvdatafeed package not installed"

    # 2) Try local CSV fallback at backend/data/<EXCHANGE>_<SYMBOL>_<TF>.csv
    csv_candles = _try_csv_fallback(symbol, exchange, timeframe, bars)
    if csv_candles is not None:
        return csv_candles, "csv-fallback"

    # 3) Nothing worked -> raise an explicit error
    raise RuntimeError(
        "TradingView data fetch failed. "
        "Check symbol/exchange/timeframe or use CSV fallback. "
        f"Reason: {last_err}"
    )


def _try_csv_fallback(
    symbol: str,
    exchange: str,
    timeframe: str,
    bars: int,
) -> Optional[List[Dict[str, Any]]]:
    """Load CSV fallback if a file exists at backend/data/."""
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(here, "data")
    if not os.path.isdir(data_dir):
        return None
    fname = f"{exchange.upper()}_{symbol.upper()}_{timeframe.upper()}.csv"
    fpath = os.path.join(data_dir, fname)
    if not os.path.exists(fpath):
        return None
    rows: List[Dict[str, Any]] = []
    with open(fpath, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            try:
                rows.append(
                    {
                        "time": r.get("time") or r.get("date") or "",
                        "open": float(r["open"]),
                        "high": float(r["high"]),
                        "low": float(r["low"]),
                        "close": float(r["close"]),
                        "volume": float(r.get("volume", 0) or 0),
                    }
                )
            except (KeyError, ValueError):
                continue
    if not rows:
        return None
    return rows[-int(bars):]


def get_demo_ohlc(symbol: str, timeframe: str, bars: int = 300, seed: int = 42) -> List[Dict[str, Any]]:
    """Generate a deterministic, realistic-looking demo OHLC series.

    Used ONLY when explicitly requested by the user (?demo=true). This is
    NOT a substitute for real market data, and the API marks the source
    as "synthetic" so the frontend can warn the user.
    """
    tf_minutes = {"1M": 1, "5M": 5, "15M": 15, "30M": 30, "1H": 60, "4H": 240, "1D": 1440}
    step = tf_minutes.get(timeframe.upper(), 5)
    rng = random.Random(seed + hash(symbol) % 100000 + step)
    # base price
    base = 1.10 if "USD" in symbol and "JPY" not in symbol and "NZD" not in symbol else (
        0.60 if "NZDUSD" in symbol.upper() else (
            150.0 if "JPY" in symbol else (
                2400.0 if symbol.upper() == "XAUUSD" else (
                    65000.0 if symbol.upper() == "BTCUSD" else (
                        3500.0 if symbol.upper() == "ETHUSD" else 1.0
                    )
                )
            )
        )
    )
    price = base
    out: List[Dict[str, Any]] = []
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    drift = rng.uniform(-0.0005, 0.0005)
    for i in range(bars):
        t = now - timedelta(minutes=step * (bars - i))
        vol = base * 0.0015
        change = rng.gauss(drift, vol)
        open_ = price
        close = max(0.0001, price + change)
        high = max(open_, close) + abs(rng.gauss(0, vol * 0.5))
        low = min(open_, close) - abs(rng.gauss(0, vol * 0.5))
        out.append(
            {
                "time": t.isoformat(),
                "open": round(open_, 5),
                "high": round(high, 5),
                "low": round(low, 5),
                "close": round(close, 5),
                "volume": round(rng.uniform(100, 1000), 2),
            }
        )
        price = close
    return out
