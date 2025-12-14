#!/usr/bin/env python3
"""
Test script for Top 5 OTC pairs functionality
"""

import requests
import json
import time

# Server URL
BASE_URL = "http://localhost:8000"

# Top 5 OTC pairs to test
TOP_5_PAIRS = [
    "GOLD_OTC",
    "USDARS_OTC", 
    "USDMXN_OTC",
    "USDBRL_OTC",
    "CADCHF_OTC",
    "USDDZD_OTC"
]

def test_prediction(symbol):
    """Test prediction for a specific symbol"""
    print(f"\n🔍 Testing {symbol}...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/prediction/", 
                               json={"symbol": symbol, "timeframe": "5m"},
                               timeout=10)
        
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
            print(f"❌ {symbol}: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ {symbol}: Error - {str(e)}")
        return False

def test_current_price(symbol):
    """Test current price endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/current-price/?symbol={symbol}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"💰 {symbol} Current Price: {data['price']:.4f}")
            return True
        else:
            print(f"❌ Price fetch failed for {symbol}")
            return False
            
    except Exception as e:
        print(f"❌ Price error for {symbol}: {str(e)}")
        return False

def main():
    print("🚀 Testing Top 5 OTC Pairs System")
    print("=" * 50)
    
    # Test server connectivity
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print(f"❌ Server returned status {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    print(f"\n📊 Testing {len(TOP_5_PAIRS)} OTC pairs...")
    
    successful_predictions = 0
    successful_prices = 0
    
    for symbol in TOP_5_PAIRS:
        # Test current price
        if test_current_price(symbol):
            successful_prices += 1
        
        # Small delay between requests
        time.sleep(1)
        
        # Test prediction
        if test_prediction(symbol):
            successful_predictions += 1
        
        # Delay between symbols
        time.sleep(2)
    
    print("\n" + "=" * 50)
    print("📈 RESULTS SUMMARY")
    print("=" * 50)
    print(f"✅ Successful Price Fetches: {successful_prices}/{len(TOP_5_PAIRS)}")
    print(f"✅ Successful Predictions: {successful_predictions}/{len(TOP_5_PAIRS)}")
    print(f"📊 Overall Success Rate: {((successful_predictions + successful_prices) / (len(TOP_5_PAIRS) * 2) * 100):.1f}%")
    
    if successful_predictions > 0:
        print(f"\n🎯 System is working! {successful_predictions} pairs generated predictions.")
    else:
        print(f"\n⚠️  No predictions generated. This may be normal if confidence thresholds aren't met.")

if __name__ == "__main__":
    main()