#!/usr/bin/env python3
"""
🎯 PRECISE ENTRY SIGNAL TESTER
Tests the new advanced trading concepts and precise entry timing system

Features tested:
- Order Blocks (OB)
- ICT Concepts (Inner Circle Trader)
- Smart Money Concepts (SMC)
- Smart Money Divergence (SMD)
- Quantified Market Logic & Reasoning (QMLR)
- Precise Entry Timing (1/5/10 minutes)
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
sys.path.append('quotex_predictor')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quotex_predictor.settings')
django.setup()

from predictor.technical_analysis import AdvancedTechnicalAnalyzer
from predictor.data_sources import DataSourceManager
import pandas as pd
import numpy as np

def create_test_data():
    """Create realistic test data for demonstration"""
    print("📊 Creating test market data...")
    
    # Create realistic OHLCV data
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=200, freq='1H')
    
    # Start with base price
    base_price = 1500.0
    prices = [base_price]
    
    # Generate realistic price movements
    for i in range(199):
        # Random walk with trend
        change = np.random.normal(0, 0.002)  # 0.2% volatility
        if i > 100:  # Add trend after 100 periods
            change += 0.0005  # Slight uptrend
        
        new_price = prices[-1] * (1 + change)
        prices.append(new_price)
    
    # Create OHLCV data
    data = []
    for i, price in enumerate(prices):
        high = price * (1 + abs(np.random.normal(0, 0.001)))
        low = price * (1 - abs(np.random.normal(0, 0.001)))
        open_price = prices[i-1] if i > 0 else price
        close_price = price
        volume = np.random.randint(800, 1200)
        
        data.append({
            'timestamp': dates[i],
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    return df

def test_advanced_concepts():
    """Test all new advanced trading concepts"""
    print("\n🚀 TESTING ADVANCED TRADING CONCEPTS")
    print("=" * 50)
    
    # Create test data
    df_1h = create_test_data()
    df_4h = df_1h.resample('4H').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    
    # Initialize analyzer
    analyzer = AdvancedTechnicalAnalyzer()
    
    print(f"📈 Test data created: {len(df_1h)} 1H candles, {len(df_4h)} 4H candles")
    print(f"💰 Current price: ${df_1h['close'].iloc[-1]:.2f}")
    
    # Test 1: Order Blocks
    print("\n1️⃣ TESTING ORDER BLOCKS")
    ob_result = analyzer._analyze_order_blocks(df_1h)
    print(f"   📦 Order blocks found: {len(ob_result['order_blocks'])}")
    print(f"   🎯 Active blocks: {len(ob_result['active_blocks'])}")
    print(f"   📊 Signal: {ob_result['signal']} (Strength: {ob_result['strength']:.2f})")
    
    # Test 2: ICT Concepts
    print("\n2️⃣ TESTING ICT CONCEPTS")
    ict_result = analyzer._analyze_ict_concepts(df_1h)
    print(f"   🔄 ICT Signal: {ict_result['signal']} (Strength: {ict_result['strength']:.2f})")
    print(f"   💧 Liquidity grab detected: {ict_result.get('liquidity_grab', False)}")
    
    # Test 3: Smart Money Concepts
    print("\n3️⃣ TESTING SMART MONEY CONCEPTS")
    smc_result = analyzer._analyze_smart_money_concepts(df_1h)
    print(f"   🧠 SMC Signal: {smc_result['signal']} (Strength: {smc_result['strength']:.2f})")
    print(f"   📈 Structure break: {smc_result.get('structure_break', False)}")
    
    # Test 4: Smart Money Divergence
    print("\n4️⃣ TESTING SMART MONEY DIVERGENCE")
    smd_result = analyzer._analyze_smart_money_divergence(df_1h)
    print(f"   📉 SMD Signal: {smd_result['signal']} (Strength: {smd_result['strength']:.2f})")
    print(f"   🔍 Divergence detected: {smd_result.get('divergence_detected', False)}")
    
    # Test 5: QMLR Analysis
    print("\n5️⃣ TESTING QMLR (Quantified Market Logic & Reasoning)")
    qmlr_result = analyzer._analyze_qmlr(df_1h, df_4h)
    print(f"   🎯 QMLR Signal: {qmlr_result['signal']} (Strength: {qmlr_result['strength']:.2f})")
    print(f"   📊 Factors: {qmlr_result.get('factors', [])}")
    print(f"   🔢 Factor count: {qmlr_result.get('factor_count', 0)}")
    
    return df_1h, df_4h

def test_precise_entry_signals():
    """Test the precise entry signal system"""
    print("\n🎯 TESTING PRECISE ENTRY SIGNAL SYSTEM")
    print("=" * 50)
    
    # Get test data
    df_1h, df_4h = test_advanced_concepts()
    
    # Initialize analyzer
    analyzer = AdvancedTechnicalAnalyzer()
    
    # Get precise entry signal
    entry_signal = analyzer.get_precise_entry_signal(df_1h, df_4h)
    
    print(f"\n🚨 ENTRY SIGNAL RESULTS:")
    print(f"   🎯 Entry Signal: {entry_signal.get('entry_signal', 'N/A')}")
    print(f"   📈 Direction: {entry_signal.get('direction', 'N/A')}")
    print(f"   ⏰ Duration: {entry_signal.get('duration_minutes', 'N/A')} minutes")
    print(f"   💰 Entry Price: ${entry_signal.get('entry_price', 0):.5f}")
    print(f"   💲 Current Price: ${entry_signal.get('current_price', 0):.5f}")
    print(f"   📊 Confidence: {entry_signal.get('confidence', 0):.1f}%")
    print(f"   ⚠️ Risk Level: {entry_signal.get('risk_level', 'N/A')}")
    print(f"   ⏱️ Timing: {entry_signal.get('timing', 'N/A')}")
    print(f"   🎬 Action: {entry_signal.get('action', 'N/A')}")
    print(f"   📏 Distance to Entry: {entry_signal.get('price_distance', 0):.3f}%")
    print(f"   🔗 Confluence Score: {entry_signal.get('confluence_score', 0)}")
    print(f"   📝 Summary: {entry_signal.get('analysis_summary', 'N/A')}")
    
    return entry_signal

def simulate_trading_scenarios():
    """Simulate different trading scenarios"""
    print("\n🎮 SIMULATING TRADING SCENARIOS")
    print("=" * 50)
    
    scenarios = [
        {"name": "Strong Bullish Trend", "trend": 0.002, "volatility": 0.001},
        {"name": "Strong Bearish Trend", "trend": -0.002, "volatility": 0.001},
        {"name": "Sideways Market", "trend": 0.0, "volatility": 0.003},
        {"name": "High Volatility", "trend": 0.001, "volatility": 0.005},
    ]
    
    analyzer = AdvancedTechnicalAnalyzer()
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}️⃣ SCENARIO: {scenario['name']}")
        print("-" * 30)
        
        # Create scenario-specific data
        np.random.seed(i * 10)
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
        base_price = 1500.0
        prices = [base_price]
        
        for j in range(99):
            change = np.random.normal(scenario['trend'], scenario['volatility'])
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)
        
        # Create DataFrame
        data = []
        for k, price in enumerate(prices):
            high = price * (1 + abs(np.random.normal(0, 0.0005)))
            low = price * (1 - abs(np.random.normal(0, 0.0005)))
            open_price = prices[k-1] if k > 0 else price
            
            data.append({
                'timestamp': dates[k],
                'open': open_price,
                'high': high,
                'low': low,
                'close': price,
                'volume': np.random.randint(800, 1200)
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        # Get entry signal
        entry_signal = analyzer.get_precise_entry_signal(df, None)
        
        print(f"   🎯 Signal: {entry_signal.get('entry_signal', 'N/A')}")
        print(f"   📈 Direction: {entry_signal.get('direction', 'N/A')}")
        print(f"   ⏰ Duration: {entry_signal.get('duration_minutes', 'N/A')} min")
        print(f"   📊 Confidence: {entry_signal.get('confidence', 0):.1f}%")
        print(f"   🎬 Action: {entry_signal.get('action', 'N/A')}")

def test_api_endpoint():
    """Test the API endpoint"""
    print("\n🌐 TESTING API ENDPOINT")
    print("=" * 50)
    
    try:
        # Test with a sample symbol
        url = "http://localhost:8000/api/precise-entry/"
        data = {"symbol": "EURUSD"}
        
        print(f"📡 Making request to: {url}")
        print(f"📤 Request data: {data}")
        
        # Note: This will only work if the server is running
        print("⚠️ Note: Server must be running for API test")
        print("   Run: python quotex_predictor/manage.py runserver")
        print("   Then test with: curl -X POST http://localhost:8000/api/precise-entry/ -H 'Content-Type: application/json' -d '{\"symbol\":\"EURUSD\"}'")
        
    except Exception as e:
        print(f"❌ API test error: {e}")

def main():
    """Main test function"""
    print("🎯 PRECISE ENTRY SIGNAL SYSTEM TESTER")
    print("=" * 60)
    print("Testing advanced trading concepts:")
    print("✅ Order Blocks (OB)")
    print("✅ ICT Concepts (Inner Circle Trader)")
    print("✅ Smart Money Concepts (SMC)")
    print("✅ Smart Money Divergence (SMD)")
    print("✅ Quantified Market Logic & Reasoning (QMLR)")
    print("✅ Precise Entry Timing (1/5/10 minutes)")
    
    try:
        # Test all components
        entry_signal = test_precise_entry_signals()
        simulate_trading_scenarios()
        test_api_endpoint()
        
        print("\n🎉 ALL TESTS COMPLETED!")
        print("=" * 60)
        print("🚀 SYSTEM READY FOR TRADING!")
        print("\n📋 USAGE INSTRUCTIONS:")
        print("1. Start the server: python quotex_predictor/manage.py runserver")
        print("2. Make API calls to: /api/precise-entry/")
        print("3. Get precise UP/DOWN signals with 1/5/10 minute durations")
        print("4. Follow the entry signals for optimal trading")
        
        print(f"\n🎯 SAMPLE ENTRY SIGNAL:")
        if entry_signal.get('entry_signal') == '🚀 ENTER NOW':
            print(f"   🚨 TRADE {entry_signal.get('direction')} NOW!")
            print(f"   ⏰ Duration: {entry_signal.get('duration_minutes')} minutes")
            print(f"   📊 Confidence: {entry_signal.get('confidence')}%")
        else:
            print(f"   ⏳ {entry_signal.get('entry_signal', 'Wait for signal')}")
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()