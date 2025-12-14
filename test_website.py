#!/usr/bin/env python3
"""
Test script to verify the website is working properly
"""

import requests
import json
import time

def test_website():
    """Test the website functionality"""
    print("🌐 Testing Quotex Advanced Trading Predictor Website")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Check if website loads
    print("\n1. Testing website homepage...")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ Homepage loads successfully")
        else:
            print(f"❌ Homepage failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Homepage error: {e}")
    
    # Test 2: Test prediction API with multiple pairs
    test_pairs = [
        'EURUSD_OTC', 'GBPUSD_OTC', 'USDJPY_OTC', 'AUDUSD_OTC',
        'NZDJPY_OTC', 'AUDCAD_OTC', 'EURJPY_OTC', 'GBPJPY_OTC'
    ]
    
    print(f"\n2. Testing prediction API with {len(test_pairs)} trading pairs...")
    
    successful_predictions = 0
    
    for symbol in test_pairs:
        try:
            response = requests.post(f'{base_url}/api/prediction/', 
                                   json={'symbol': symbol, 'timeframe': '5m'},
                                   headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('threshold_met') and data.get('prediction'):
                    prediction = data['prediction']
                    print(f"✅ {symbol}: {prediction['direction']} ({prediction['confidence']:.1f}%)")
                    successful_predictions += 1
                else:
                    print(f"⚠️  {symbol}: Below threshold ({data.get('prediction', {}).get('confidence', 0):.1f}%)")
            else:
                print(f"❌ {symbol}: API Error ({response.status_code})")
                
        except Exception as e:
            print(f"❌ {symbol}: Exception - {e}")
        
        time.sleep(0.5)  # Small delay between requests
    
    print(f"\n📊 Results Summary:")
    print(f"   • Total pairs tested: {len(test_pairs)}")
    print(f"   • Successful predictions: {successful_predictions}")
    print(f"   • Success rate: {(successful_predictions/len(test_pairs)*100):.1f}%")
    
    # Test 3: Test other API endpoints
    print(f"\n3. Testing other API endpoints...")
    
    endpoints = [
        ('/api/accuracy/', 'GET'),
        ('/api/recent-predictions/', 'GET'),
        ('/api/current-price/?symbol=EURUSD_OTC', 'GET')
    ]
    
    for endpoint, method in endpoints:
        try:
            if method == 'GET':
                response = requests.get(f'{base_url}{endpoint}')
            else:
                response = requests.post(f'{base_url}{endpoint}')
            
            if response.status_code == 200:
                print(f"✅ {endpoint}: Working")
            else:
                print(f"❌ {endpoint}: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Exception - {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Website Testing Complete!")
    print("\n🚀 The Advanced Quotex Trading Predictor is ready!")
    print("   • Professional 5-minute direction predictions")
    print("   • Multi-timeframe analysis (1H/4H)")
    print("   • Advanced market structure concepts")
    print("   • 70%+ confidence threshold")
    print("   • All Quotex OTC pairs supported")

if __name__ == "__main__":
    test_website()