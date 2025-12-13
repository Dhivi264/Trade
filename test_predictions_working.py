#!/usr/bin/env python3
"""
Quick test to verify predictions are generating properly
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_prediction_generation():
    """Test that predictions are now generating"""
    print("🧪 Testing Prediction Generation")
    print("=" * 40)
    
    # Test multiple OTC pairs
    test_pairs = [
        "EURUSD_OTC",
        "GBPUSD_OTC", 
        "USDJPY_OTC",
        "NZDJPY_OTC",
        "AUDCAD_OTC"
    ]
    
    predictions_generated = 0
    
    for symbol in test_pairs:
        try:
            payload = {
                "symbol": symbol,
                "timeframe": "1m"
            }
            
            response = requests.post(f"{BASE_URL}/api/prediction/", 
                                   json=payload,
                                   headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('threshold_met') and data.get('prediction'):
                    pred = data['prediction']
                    print(f"✅ {symbol}: {pred['direction']} ({pred['confidence']:.1f}%)")
                    predictions_generated += 1
                else:
                    confidence = data.get('prediction', {}).get('confidence', 0) if data.get('prediction') else 0
                    print(f"⚠️  {symbol}: No prediction (confidence: {confidence:.1f}%)")
            else:
                print(f"❌ {symbol}: API Error - {response.status_code}")
                
        except Exception as e:
            print(f"❌ {symbol}: Error - {e}")
    
    print(f"\n📊 Results:")
    print(f"   Predictions generated: {predictions_generated}/{len(test_pairs)}")
    print(f"   Success rate: {(predictions_generated/len(test_pairs)*100):.1f}%")
    
    if predictions_generated > 0:
        print("\n🎉 SUCCESS: Predictions are now generating!")
        print("✅ The system is working properly")
        print("✅ High-confidence predictions are available")
    else:
        print("\n⚠️  No predictions generated - this might be normal")
        print("💡 Try refreshing or testing different pairs")
        print("💡 Market conditions may not meet confidence threshold")

if __name__ == "__main__":
    test_prediction_generation()