#!/usr/bin/env python3
"""
Demo: How the 5-Minute Direction Prediction Works
"""

import requests
import json
from datetime import datetime, timedelta

def demo_5min_prediction():
    print("🎯 QUOTEX 5-MINUTE DIRECTION PREDICTION DEMO")
    print("=" * 50)
    
    # Test with USD/ARS (high profit pair)
    symbol = "USDARS_OTC"
    
    print(f"📊 Testing {symbol} for 5-minute direction prediction...")
    print(f"⏰ Current Time: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # Make prediction request
        response = requests.post("http://localhost:8000/api/prediction/", 
                               json={"symbol": symbol, "timeframe": "5m"},
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('threshold_met') and data.get('prediction'):
                pred = data['prediction']
                
                print("\n✅ PREDICTION GENERATED!")
                print("-" * 30)
                print(f"🎯 DIRECTION: {pred['direction']}")
                print(f"📈 CONFIDENCE: {pred['confidence']:.1f}%")
                print(f"💰 CURRENT PRICE: {pred['current_price']:.4f}")
                print(f"⏱️  TIMEFRAME: 5 minutes")
                print(f"📊 ANALYSIS USED: {', '.join(pred.get('analysis_timeframes', ['1H', '4H']))}")
                
                # Calculate when to check result
                prediction_time = datetime.now()
                check_time = prediction_time + timedelta(minutes=5)
                
                print(f"\n🕐 PREDICTION TIMELINE:")
                print(f"   • Prediction Made: {prediction_time.strftime('%H:%M:%S')}")
                print(f"   • Check Result At: {check_time.strftime('%H:%M:%S')}")
                print(f"   • Duration: 5 minutes")
                
                print(f"\n🎲 HOW IT WORKS:")
                print(f"   1. System analyzes 1H and 4H market structure")
                print(f"   2. Identifies key levels, trends, and patterns")
                print(f"   3. Predicts if price will go UP or DOWN in next 5 minutes")
                print(f"   4. Only shows predictions with 70%+ confidence")
                print(f"   5. Auto-resolves after 5 minutes to track accuracy")
                
                # Show signal breakdown
                if 'signal_breakdown' in pred:
                    signals = pred['signal_breakdown']
                    print(f"\n📊 SIGNAL ANALYSIS:")
                    print(f"   • UP Signals: {signals.get('up_signals', 0)}")
                    print(f"   • DOWN Signals: {signals.get('down_signals', 0)}")
                    print(f"   • Total Signals: {signals.get('total_signals', 0)}")
                
                print(f"\n💡 TRADING STRATEGY:")
                if pred['direction'] == 'UP':
                    print(f"   • Place a CALL (UP) trade for 5 minutes")
                    print(f"   • Expected: Price will be HIGHER than {pred['current_price']:.4f}")
                else:
                    print(f"   • Place a PUT (DOWN) trade for 5 minutes")
                    print(f"   • Expected: Price will be LOWER than {pred['current_price']:.4f}")
                
                print(f"\n🏆 PROFIT POTENTIAL:")
                print(f"   • {symbol}: 88% profit rate")
                print(f"   • High confidence: {pred['confidence']:.1f}%")
                print(f"   • Professional analysis using 1H/4H timeframes")
                
            else:
                print(f"\n⚠️  NO PREDICTION AVAILABLE")
                print(f"   Reason: {data.get('message', 'Unknown')}")
                print(f"   Note: System only shows predictions with 70%+ confidence")
                
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    demo_5min_prediction()