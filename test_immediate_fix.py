#!/usr/bin/env python3
"""
Immediate test to verify predictions are now working
"""

import requests
import json

def test_immediate_fix():
    """Test that predictions are now generating immediately"""
    print("🔧 Testing Immediate Prediction Fix")
    print("=" * 40)
    
    BASE_URL = "http://localhost:8000"
    
    # Test one prediction
    try:
        payload = {
            "symbol": "EURUSD_OTC",
            "timeframe": "1m"
        }
        
        print("📡 Sending prediction request...")
        response = requests.post(f"{BASE_URL}/api/prediction/", 
                               json=payload,
                               headers={'Content-Type': 'application/json'})
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Response data: {json.dumps(data, indent=2)}")
            
            if data.get('threshold_met') and data.get('prediction'):
                pred = data['prediction']
                print(f"\n🎉 SUCCESS! Prediction generated:")
                print(f"   Direction: {pred['direction']}")
                print(f"   Confidence: {pred['confidence']:.1f}%")
                print(f"   Current Price: ${pred['current_price']:.4f}")
                print(f"   Signals: {pred['signal_breakdown']}")
                return True
            else:
                print(f"\n⚠️  Still no prediction:")
                print(f"   Threshold met: {data.get('threshold_met')}")
                print(f"   Message: {data.get('message', 'No message')}")
                return False
        else:
            print(f"\n❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_immediate_fix()
    if success:
        print("\n✅ Fix successful! Predictions are now working!")
    else:
        print("\n❌ Fix not working yet. May need server restart.")
        print("💡 Try: Restart the server and test again")