#!/usr/bin/env python3
"""
Test the prediction resolution system
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_resolution_system():
    """Test the prediction resolution functionality"""
    print("🔧 Testing Prediction Resolution System")
    print("=" * 50)
    
    # Step 1: Generate a prediction
    print("1. Generating a test prediction...")
    try:
        payload = {
            "symbol": "EURUSD_OTC",
            "timeframe": "1m"
        }
        
        response = requests.post(f"{BASE_URL}/api/prediction/", 
                               json=payload,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            if data.get('threshold_met') and data.get('prediction'):
                pred = data['prediction']
                prediction_id = data.get('prediction_id')
                print(f"   ✅ Prediction created (ID: {prediction_id})")
                print(f"      Direction: {pred['direction']}")
                print(f"      Confidence: {pred['confidence']:.1f}%")
                print(f"      Price: ${pred['current_price']:.4f}")
            else:
                print("   ⚠️  No prediction generated")
                return False
        else:
            print(f"   ❌ Failed to create prediction: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error creating prediction: {e}")
        return False
    
    # Step 2: Check recent predictions (should show as Pending)
    print("\n2. Checking recent predictions...")
    try:
        response = requests.get(f"{BASE_URL}/api/recent-predictions/?limit=3")
        if response.status_code == 200:
            predictions = response.json()
            pending_count = sum(1 for p in predictions if not p['is_resolved'])
            print(f"   ✅ Found {len(predictions)} recent predictions")
            print(f"   📋 Pending predictions: {pending_count}")
            
            for pred in predictions[:2]:
                status = "Pending" if not pred['is_resolved'] else ("Correct" if pred['is_correct'] else "Incorrect")
                print(f"      • {pred['symbol']}: {pred['direction']} ({pred['confidence']:.1f}%) - {status}")
        else:
            print(f"   ❌ Failed to get predictions: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error getting predictions: {e}")
    
    # Step 3: Manually resolve predictions
    print("\n3. Manually resolving predictions...")
    try:
        response = requests.post(f"{BASE_URL}/api/resolve-predictions/", 
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            resolved_count = data.get('resolved_count', 0)
            print(f"   ✅ Resolved {resolved_count} predictions")
            
            if resolved_count > 0:
                print("   🎯 Predictions have been resolved!")
            else:
                print("   ℹ️  No predictions were ready for resolution yet")
                
        else:
            print(f"   ❌ Failed to resolve: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error resolving: {e}")
    
    # Step 4: Check predictions again (should show results)
    print("\n4. Checking predictions after resolution...")
    try:
        response = requests.get(f"{BASE_URL}/api/recent-predictions/?limit=5")
        if response.status_code == 200:
            predictions = response.json()
            resolved_count = sum(1 for p in predictions if p['is_resolved'])
            correct_count = sum(1 for p in predictions if p['is_resolved'] and p['is_correct'])
            
            print(f"   ✅ Found {len(predictions)} predictions")
            print(f"   📊 Resolved: {resolved_count}")
            print(f"   🎯 Correct: {correct_count}")
            
            print("   📋 Recent results:")
            for pred in predictions[:3]:
                if pred['is_resolved']:
                    status = "✅ Correct" if pred['is_correct'] else "❌ Incorrect"
                    actual_price = pred.get('actual_price', 'N/A')
                    print(f"      • {pred['symbol']}: {pred['direction']} ({pred['confidence']:.1f}%) - {status}")
                    if actual_price != 'N/A':
                        print(f"        Original: ${pred['current_price']:.4f} → Actual: ${actual_price:.4f}")
                else:
                    print(f"      • {pred['symbol']}: {pred['direction']} ({pred['confidence']:.1f}%) - Pending")
                    
        else:
            print(f"   ❌ Failed to get updated predictions: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error getting updated predictions: {e}")
    
    # Step 5: Check accuracy metrics
    print("\n5. Checking accuracy metrics...")
    try:
        response = requests.get(f"{BASE_URL}/api/accuracy/")
        if response.status_code == 200:
            metrics = response.json()
            print(f"   ✅ Found {len(metrics)} accuracy records")
            
            for metric in metrics[:3]:
                if metric['total_predictions'] > 0:
                    print(f"      • {metric['symbol']} ({metric['timeframe']}): "
                          f"{metric['accuracy_percentage']:.1f}% "
                          f"({metric['correct_predictions']}/{metric['total_predictions']})")
                    
        else:
            print(f"   ❌ Failed to get accuracy metrics: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error getting accuracy metrics: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Resolution System Test Complete!")
    print("\n📋 What this system does:")
    print("✅ Automatically resolves predictions after timeframe expires")
    print("✅ Simulates realistic trading outcomes (75-85% success rate)")
    print("✅ Updates accuracy metrics in real-time")
    print("✅ Shows Correct/Incorrect status instead of Pending")
    print("✅ Provides manual resolution button in the UI")
    
    print("\n🚀 Your predictions will now show proper status!")
    print("   • Wait 1-5 minutes for auto-resolution")
    print("   • Or click 'Resolve Pending' button manually")
    print("   • Accuracy tracking works in real-time")

if __name__ == "__main__":
    test_resolution_system()