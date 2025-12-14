#!/usr/bin/env python3
"""
Test USD/ARS and USD/MXN specifically
"""

import requests
import json

def test_pair(symbol):
    """Test prediction for a specific symbol"""
    print(f"\n🔍 Testing {symbol}...")
    
    try:
        response = requests.post("http://localhost:8000/api/prediction/", 
                               json={"symbol": symbol, "timeframe": "5m"},
                               timeout=10)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('threshold_met') and data.get('prediction'):
                pred = data['prediction']
                print(f"✅ {symbol}: {pred['direction']} - {pred['confidence']:.1f}% confidence")
                print(f"   Current Price: {pred['current_price']:.4f}")
                return True
            else:
                print(f"⚠️  {symbol}: {data.get('message', 'No high-confidence prediction')}")
                return False
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("🎯 Testing USD/ARS and USD/MXN pairs")
    print("=" * 40)
    
    pairs = ['USDARS_OTC', 'USDMXN_OTC']
    
    for pair in pairs:
        success = test_pair(pair)
        if success:
            print(f"✅ {pair} is working correctly!")
        else:
            print(f"❌ {pair} has issues")

if __name__ == "__main__":
    main()