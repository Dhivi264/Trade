#!/usr/bin/env python3
"""
Test API Connection
Quick script to verify API endpoints are working
"""

import requests
import json

def test_api():
    """Test API endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing API Endpoints")
    print("=" * 50)
    
    # Test 1: Trading Pairs
    print("\n1️⃣ Testing /api/trading-pairs/")
    try:
        response = requests.get(f"{base_url}/api/trading-pairs/", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Found {len(data)} trading pairs")
            for pair in data[:3]:
                print(f"      - {pair['symbol']}: {pair['name']}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    # Test 2: Current Price
    print("\n2️⃣ Testing /api/current-price/")
    try:
        response = requests.get(f"{base_url}/api/current-price/?symbol=EURUSD", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! EURUSD price: {data.get('price', 'N/A')}")
        else:
            print(f"   ⚠️ Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    # Test 3: Prediction (POST)
    print("\n3️⃣ Testing /api/prediction/ (POST)")
    try:
        response = requests.post(
            f"{base_url}/api/prediction/",
            json={"symbol": "EURUSD", "timeframe": "5m"},
            timeout=15
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('threshold_met'):
                pred = data.get('prediction', {})
                print(f"   ✅ Prediction: {pred.get('direction')} with {pred.get('confidence')}% confidence")
            else:
                print(f"   ⚠️ No high-confidence prediction available")
        else:
            print(f"   ⚠️ Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    # Test 4: Homepage
    print("\n4️⃣ Testing / (Homepage)")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Homepage loaded successfully")
        else:
            print(f"   ❌ Error loading homepage")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ API Testing Complete!")
    print("\n💡 If all tests passed, the 'Failed to fetch' error is likely:")
    print("   - Browser accessing wrong URL")
    print("   - Frontend not running")
    print("   - CORS issue (check browser console)")
    print("\n🌐 Server should be accessible at: http://127.0.0.1:8000")

if __name__ == "__main__":
    test_api()
