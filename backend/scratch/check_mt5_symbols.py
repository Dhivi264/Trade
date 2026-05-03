import os
from dotenv import load_dotenv
import MetaTrader5 as mt5

load_dotenv()

# MT5 credentials from environment
login_str = os.getenv("MT5_LOGIN", "0").strip()
login = int(login_str) if login_str.isdigit() else 0
password = os.getenv("MT5_PASSWORD", "").strip()
server = os.getenv("MT5_SERVER", "").strip()

print(f"Connecting to MT5: {server} (User: {login})")

if not mt5.initialize(login=login, password=password, server=server) if login else mt5.initialize():
    print(f"mt5.initialize() failed, error code = {mt5.last_error()}")
    exit()

# List first 20 symbols
symbols = mt5.symbols_get()
print(f"Total symbols found: {len(symbols)}")

# Look for GBPJPY specifically
gbpjpy_matches = [s.name for s in symbols if "GBPJPY" in s.name.upper()]
print(f"GBPJPY matches: {gbpjpy_matches}")

# Check if GBPJPY is visible in Market Watch
symbol = "GBPJPY"
selected = mt5.symbol_select(symbol, True)
print(f"Symbol {symbol} select status: {selected}")

rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 10)
if rates is not None:
    print(f"Successfully fetched {len(rates)} rates for {symbol}")
else:
    print(f"Failed to fetch rates for {symbol}. Error: {mt5.last_error()}")

mt5.shutdown()
