import os
import sys
import logging
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd()))

from services.tv_data import get_ohlc

# Set up logging
logger = logging.getLogger("test_final_fallback")
logging.basicConfig(level=logging.INFO)

load_dotenv()

def simulate_full_fallback(sym, bars=10):
    series = {}
    source = "Unavailable"

    primary = (os.getenv("DATA_SOURCE_PRIMARY") or "tradingview").lower()
    fallback = (os.getenv("DATA_SOURCE_FALLBACK") or "mt5").lower()

    print(f"DEBUG: Primary={primary}, Fallback={fallback}")

    for current_source_key in [primary, fallback, "tradingview_guest"]:
        print(f"\n--- Trying source: {current_source_key} ---")
        try:
            if current_source_key == "tradingview":
                source = "TradingView"
                # This will FAIL because login fails
                candles, _ = get_ohlc(sym, "OANDA", "1H", bars=bars)
                series["1H"] = candles
                print("SUCCESS: TradingView worked!")
                break
            elif current_source_key == "mt5":
                source = "MetaTrader5"
                print("SIMULATING MT5 FAILURE...")
                raise RuntimeError("MT5: No rates found.")
            elif current_source_key == "tradingview_guest":
                source = "TradingView (Guest Mode)"
                print("USING GUEST MODE FALLBACK...")
                candles, _ = get_ohlc(sym, "OANDA", "1H", bars=bars, force_guest=True)
                series["1H"] = candles
                print("SUCCESS: TradingView Guest Mode worked!")
                break
        except Exception as e:
            print(f"WARNING: {current_source_key} failed: {e}")
            continue
    
    return source

print("=== TESTING MULTI-STAGE FALLBACK ===")
result_source = simulate_full_fallback("GBPJPY")
print(f"\nFINAL ACTIVE SOURCE: {result_source}")
