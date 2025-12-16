#!/usr/bin/env python3
"""
🔴 USD/ARS REAL PRICE TESTER
Tests the real USD/ARS exchange rate fetching to match market price of ~1510
"""

import requests
import json
from datetime import datetime

def test_usdars_apis():
    """Test multiple USD/ARS APIs to get real market rate"""
    print("🔴 TESTING USD/ARS REAL MARKET RATE")
    print("=" * 50)
    print("Target: ~1510.00 (as shown in your image)")
    
    # Test multiple USD/ARS sources
    sources = [
        {
            'name': 'ExchangeRate-API',
            'url': 'https://api.exchangerate-api.com/v4/latest/USD',
            'path': ['rates', 'ARS']
        },
        {
            'name': 'Yahoo Finance ARS=X',
            'url': 'https://query1.finance.yahoo.com/v8/finance/chart/ARS=X',
            'path': ['chart', 'result', 0, 'meta', 'regularMarketPrice']
        },
        {
            'name': 'Open Exchange Rates',
            'url': 'https://open.er-api.com/v6/latest/USD',
            'path': ['rates', 'ARS']
        },
        {
            'name': 'Fixer.io (Free)',
            'url': 'https://api.fixer.io/latest?base=USD',
            'path': ['rates', 'ARS']
        }
    ]
    
    real_rates = []
    
    for source in sources:
        try:
            print(f"\n📊 Testing {source['name']}:")
            
            response = requests.get(source['url'], timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Navigate through the path to get the rate
                current = data
                for key in source['path']:
                    if isinstance(key, int):
                        current = current[key]
                    else:
                        current = current.get(key)
                    
                    if current is None:
                        break
                
                if current is not None:
                    rate = float(current)
                    real_rates.append(rate)
                    print(f"   🔴 USD/ARS Rate: {rate:.2f}")
                    
                    # Check if it matches expected range
                    if 1500 <= rate <= 1520:
                        print(f"   ✅ MATCHES MARKET RATE!")
                    else:
                        print(f"   ⚠️ Different from expected ~1510")
                else:
                    print(f"   ❌ No rate found in response")
            else:
                print(f"   ❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Show summary
    if real_rates:
        avg_rate = sum(real_rates) / len(real_rates)
        print(f"\n📊 SUMMARY:")
        print(f"   Found {len(real_rates)} real rates")
        print(f"   Average: {avg_rate:.2f}")
        print(f"   Range: {min(real_rates):.2f} - {max(real_rates):.2f}")
        
        if 1500 <= avg_rate <= 1520:
            print(f"   ✅ AVERAGE MATCHES EXPECTED MARKET RATE!")
        else:
            print(f"   ⚠️ Average differs from expected ~1510")
    else:
        print(f"\n❌ No real rates found from any source")

def test_alternative_sources():
    """Test alternative USD/ARS sources"""
    print(f"\n💱 TESTING ALTERNATIVE USD/ARS SOURCES")
    print("=" * 50)
    
    # Test financial data APIs
    alternatives = [
        'https://api.currencyapi.com/v3/latest?apikey=demo&currencies=ARS&base_currency=USD',
        'https://api.coinbase.com/v2/exchange-rates?currency=USD',
        'https://api.exchangerate.host/latest?base=USD&symbols=ARS'
    ]
    
    for url in alternatives:
        try:
            print(f"\n📊 Testing: {url.split('//')[1].split('/')[0]}")
            
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response keys: {list(data.keys())}")
                
                # Try to find ARS rate in different structures
                if 'data' in data and 'ARS' in data['data']:
                    rate = float(data['data']['ARS']['value'])
                    print(f"   🔴 USD/ARS Rate: {rate:.2f}")
                elif 'rates' in data and 'ARS' in data['rates']:
                    rate = float(data['rates']['ARS'])
                    print(f"   🔴 USD/ARS Rate: {rate:.2f}")
                else:
                    print(f"   ⚠️ ARS rate not found in expected format")
            
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def test_django_integration():
    """Test the Django system integration"""
    print(f"\n🎯 TESTING DJANGO SYSTEM INTEGRATION")
    print("=" * 50)
    
    try:
        # Test the API endpoint
        url = "http://127.0.0.1:8000/api/qxbroker-quote/?symbol=USDARS_OTC"
        
        print(f"📡 Testing: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            current_price = data.get('current_price', 0)
            data_source = data.get('data_source', 'UNKNOWN')
            
            print(f"🔴 Current USD/ARS Price: {current_price:.2f}")
            print(f"📊 Data Source: {data_source}")
            
            if 1500 <= current_price <= 1520:
                print(f"✅ PRICE MATCHES REAL MARKET!")
            else:
                print(f"⚠️ Price differs from expected ~1510")
                
            if data_source == 'REAL':
                print(f"✅ Using REAL market data!")
            else:
                print(f"⚠️ Using simulated data")
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Django test error: {e}")

def main():
    """Main test function"""
    print("🔴 USD/ARS REAL PRICE VERIFICATION")
    print("=" * 60)
    print("Goal: Match real market price of ~1510.00 as shown in your image")
    
    try:
        # Test external APIs
        test_usdars_apis()
        test_alternative_sources()
        
        # Test Django integration
        test_django_integration()
        
        print(f"\n🎉 TESTING COMPLETED!")
        print("=" * 60)
        print("🔴 If real rates ~1510 were found, the system should now show correct prices!")
        print("🌐 Refresh your web interface to see updated USD/ARS rates")
        print("📊 Look for the 🔴 LIVE MARKET badge to confirm real data")
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")

if __name__ == "__main__":
    main()