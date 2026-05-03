import os
import sys
import logging
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd()))

from services.tv_data import get_ohlc

# Set up logging like in main.py
logger = logging.getLogger("test_fallback")
logging.basicConfig(level=logging.INFO)

load_dotenv()

def simulate_analyze_logic(sym, bars=10):
    series = {}
    source = "Unavailable"

    primary = (os.getenv("DATA_SOURCE_PRIMARY") or "tradingview").lower()
    fallback = (os.getenv("DATA_SOURCE_FALLBACK") or "mt5").lower()

    print(f"DEBUG: Primary={primary}, Fallback={fallback}")

    for current_source_key in [primary, fallback]:
        print(f"\n--- Trying source: {current_source_key} ---")
        try:
            if current_source_key == "tradingview":
                source = "TradingView"
                for tf in ("1H", "15M", "5M"):
                    # This will raise RuntimeError if TV login fails and username is set
                    candles, _ = get_ohlc(sym, "OANDA", tf, bars=bars)
                    series[tf] = candles
                print(f"SUCCESS: TradingView worked!")
                break
            elif current_source_key == "mt5":
                # Mock MT5 call or just print
                print("SIMULATING MT5 FETCH...")
                # from services.mt5_data import get_mt5_ohlc
                # For this test, we just assume MT5 works if it reaches here
                source = "MetaTrader5"
                series = {"1H": [], "15M": [], "5M": []}
                print(f"SUCCESS: MT5 fallback worked!")
                break
        except Exception as e:
            print(f"WARNING: {current_source_key} failed: {e}")
            continue
    else:
        print("ERROR: All sources failed")
    
    return source

# Case 1: TV has credentials but they are invalid (as in user's case)
# The get_ohlc should now raise RuntimeError, and we should move to MT5
print("=== TESTING FALLBACK SCENARIO ===")
result_source = simulate_analyze_logic("EURUSD")
print(f"\nFINAL ACTIVE SOURCE: {result_source}")
