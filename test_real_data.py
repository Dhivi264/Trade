#!/usr/bin/env python3
"""
🔴 REAL MARKET DATA TESTER
Tests the real-time data fetching from actual market APIs
"""

import sys
import os
sys.path.append('quotex_predictor')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quotex_predictor.settings')

import django
django.setup()

from predictor.data_sources import DataSourceManager, RealTimeDataFetcher, ForexAPISource
import requests

def test_yahoo_finance_direct():
    """Test Yahoo Finance API directly"""
    print("🔴 TESTING YAHOO FINANCE API DIRECTLY")
    print("=" * 50)
    
    symbols = {
        'EURUSD': 'EURUSD=X',
        'GOLD': 'GC=F',
        'GBPUSD': 'GBPUSD=X'
    }
    
    for name, yahoo_symbol in symbols.items():
        try:
            print(f"\n📊 Testing {name} ({yahoo_symbol}):")
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
            params = {
                'interval': '1m',
                'period1': 1734393600,  # Recent timestamp
                'period2': 1734397200   # Current timestamp
            }
            
            response = requests.get(url, params=params, timeout=10)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    
                    if 'meta' in result:
                        meta = result['meta']
                        if 'regularMarketPrice' in meta:
                            price = meta['regularMarketPrice']
                            print(f"   🔴 REAL PRICE: ${price}")
                        else:
                            print(f"   ⚠️ No regularMarketPrice in meta")
                    else:
                        print(f"   ⚠️ No meta in result")
                else:
                    print(f"   ❌ No chart result")
            else:
                print(f"   ❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def test_forex_api_direct():
    """Test Forex API directly"""
    print("\n💱 TESTING FOREX API DIRECTLY")
    print("=" * 50)
    
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'rates' in data:
                print(f"🔴 REAL FOREX RATES:")
                for currency in ['EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF']:
                    if currency in data['rates']:
                        rate = data['rates'][currency]
                        print(f"   USD/{currency}: {rate}")
            else:
                print(f"❌ No rates in response")
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_data_source_manager():
    """Test our DataSourceManager with real data"""
    print("\n🎯 TESTING DATA SOURCE MANAGER")
    print("=" * 50)
    
    manager = DataSourceManager()
    
    symbols = ['EURUSD', 'GOLD_OTC', 'GBPUSD', 'USDMXN_OTC']
    
    for symbol in symbols:
        try:
            print(f"\n📊 Testing {symbol}:")
            
            # Test real-time data fetching
            data = manager.get_price_data(symbol, '1h', 10)
            
            if data is not None and not data.empty:
                current_price = data['close'].iloc[-1]
                print(f"   ✅ Got data: {len(data)} candles")
                print(f"   💰 Current Price: {current_price:.5f}")
                print(f"   📈 High: {data['high'].iloc[-1]:.5f}")
                print(f"   📉 Low: {data['low'].iloc[-1]:.5f}")
            else:
                print(f"   ❌ No data available")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def test_qxbroker_live_quotes():
    """Test QXBroker live quotes with real data"""
    print("\n🎮 TESTING QXBROKER LIVE QUOTES")
    print("=" * 50)
    
    manager = DataSourceManager()
    qx_source = manager.qxbroker
    
    symbols = ['GOLD_OTC', 'EURUSD', 'GBPUSD', 'USDMXN_OTC']
    
    for symbol in symbols:
        try:
            print(f"\n📊 Testing {symbol}:")
            
            quote = qx_source.get_live_quote(symbol)
            
            if quote:
                print(f"   💰 Price: {quote['current_price']:.5f}")
                print(f"   📊 Change: {quote['change']:+.5f} ({quote['change_percent']:+.2f}%)")
                print(f"   📋 Bid/Ask: {quote['bid']:.5f} / {quote['ask']:.5f}")
                print(f"   🔴 Data Source: {quote.get('data_source', 'UNKNOWN')}")
                print(f"   ⏰ Time: {quote['timestamp']}")
            else:
                print(f"   ❌ No quote available")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def main():
    """Main test function"""
    print("🔴 REAL MARKET DATA INTEGRATION TESTER")
    print("=" * 60)
    print("Testing connection to real market data APIs...")
    
    try:
        # Test direct API connections
        test_yahoo_finance_direct()
        test_forex_api_direct()
        
        # Test our integration
        test_data_source_manager()
        test_qxbroker_live_quotes()
        
        print(f"\n🎉 TESTING COMPLETED!")
        print("=" * 60)
        print("🔴 If you see REAL PRICE values above, the system is getting live market data!")
        print("🟡 If you see simulated data, check your internet connection and API availability.")
        print("🌐 The web interface will now show live market prices when available.")
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()