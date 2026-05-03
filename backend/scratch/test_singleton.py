import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd()))

from services.tv_data import get_ohlc

load_dotenv()

print("--- Calling get_ohlc first time (1H) ---")
try:
    candles, source = get_ohlc("EURUSD", "FX_IDC", "1H", bars=10)
    print(f"Success! Fetched {len(candles)} candles from {source}")
except Exception as e:
    print(f"Error 1: {e}")

print("\n--- Calling get_ohlc second time (15M) ---")
try:
    candles, source = get_ohlc("EURUSD", "FX_IDC", "15M", bars=10)
    print(f"Success! Fetched {len(candles)} candles from {source}")
except Exception as e:
    print(f"Error 2: {e}")

print("\n--- Calling get_ohlc third time (5M) ---")
try:
    candles, source = get_ohlc("EURUSD", "FX_IDC", "5M", bars=10)
    print(f"Success! Fetched {len(candles)} candles from {source}")
except Exception as e:
    print(f"Error 3: {e}")
