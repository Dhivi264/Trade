#!/usr/bin/env python3
"""
🎯 QXBROKER INTEGRATION TESTER
Tests the QXBroker demo platform integration with advanced trading concepts

Features:
- Real-time price simulation from QXBroker
- Advanced technical analysis (Order Blocks, ICT, SMC, SMD, QMLR)
- Precise entry signals with exact timing
- Live quote display similar to QXBroker interface
"""

import requests
import json
import time
from datetime import datetime

def test_qxbroker_quotes():
    """Test QXBroker live quotes"""
    print("📊 TESTING QXBROKER LIVE QUOTES")
    print("=" * 50)
    
    # QXBroker OTC pairs
    symbols = [
        'GOLD_OTC',
        'USDARS_OTC', 
        'USDMXN_OTC',
        'USDBRL_OTC',
        'CADCHF_OTC',
        'USDDZD_OTC'
    ]
    
    base_url = "http://localhost:8000"
    
    for symbol in symbols:
        try:
            print(f"\n📈 Testing {symbol}:")
            
            # Test live quote
            response = requests.get(f"{base_url}/api/qxbroker-quote/?symbol={symbol}")
            
            if response.status_code == 200:
                quote = response.json()
                print(f"   💰 Price: {quote['current_price']:.5f}")
                print(f"   📊 Change: {quote['change']:+.5f} ({quote['change_percent']:+.2f}%)")
                print(f"   📋 Bid/Ask: {quote['bid']:.5f} / {quote['ask']:.5f}")
                print(f"   ⏰ Time: {quote['timestamp']}")
                print(f"   ✅ Status: {quote['status']}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def test_precise_entry_signals():
    """Test precise entry signals with QXBroker data"""
    print("\n🎯 TESTING PRECISE ENTRY SIGNALS")
    print("=" * 50)
    
    symbols = ['GOLD_OTC', 'USDARS_OTC', 'USDMXN_OTC']
    base_url = "http://localhost:8000"
    
    for symbol in symbols:
        try:
            print(f"\n🚀 Testing Entry Signal for {symbol}:")
            
            # Test precise entry signal
            response = requests.post(
                f"{base_url}/api/precise-entry/",
                json={"symbol": symbol},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                signal = data['entry_signal']
                
                print(f"   🎯 Entry Signal: {signal.get('entry_signal', 'N/A')}")
                print(f"   📈 Direction: {signal.get('direction', 'N/A')}")
                print(f"   ⏰ Duration: {signal.get('duration_minutes', 'N/A')} minutes")
                print(f"   📊 Confidence: {signal.get('confidence', 0):.1f}%")
                print(f"   💰 Entry Price: {signal.get('entry_price', 'N/A')}")
                print(f"   💲 Current Price: {signal.get('current_price', 'N/A')}")
                print(f"   ⚠️ Risk Level: {signal.get('risk_level', 'N/A')}")
                print(f"   🎬 Action: {signal.get('action', 'N/A')}")
                
                if signal.get('entry_signal') == '🚀 ENTER NOW':
                    print(f"   🚨 TRADE RECOMMENDATION: {signal.get('direction')} for {signal.get('duration_minutes')} minutes!")
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def simulate_qxbroker_trading_session():
    """Simulate a complete QXBroker trading session"""
    print("\n🎮 SIMULATING QXBROKER TRADING SESSION")
    print("=" * 50)
    
    # Focus on Gold OTC - highest profit potential
    symbol = 'GOLD_OTC'
    base_url = "http://localhost:8000"
    
    print(f"🥇 Trading Session: {symbol}")
    print(f"🌐 Platform: QXBroker Demo (qxbroker.com/en/demo-trade)")
    print(f"💰 Investment: $1.00")
    print(f"📊 Analysis: Advanced Technical Concepts")
    
    try:
        # Get live quote
        quote_response = requests.get(f"{base_url}/api/qxbroker-quote/?symbol={symbol}")
        
        if quote_response.status_code == 200:
            quote = quote_response.json()
            
            print(f"\n📊 LIVE QUOTE:")
            print(f"   Current Price: {quote['current_price']:.5f}")
            print(f"   Change: {quote['change']:+.5f} ({quote['change_percent']:+.2f}%)")
            print(f"   Bid: {quote['bid']:.5f} | Ask: {quote['ask']:.5f}")
            
            # Get entry signal
            signal_response = requests.post(
                f"{base_url}/api/precise-entry/",
                json={"symbol": symbol},
                headers={"Content-Type": "application/json"}
            )
            
            if signal_response.status_code == 200:
                data = signal_response.json()
                signal = data['entry_signal']
                
                print(f"\n🎯 ENTRY ANALYSIS:")
                print(f"   Signal: {signal.get('entry_signal', 'N/A')}")
                print(f"   Direction: {signal.get('direction', 'N/A')}")
                print(f"   Duration: {signal.get('duration_minutes', 'N/A')} minutes")
                print(f"   Confidence: {signal.get('confidence', 0):.1f}%")
                print(f"   Risk Level: {signal.get('risk_level', 'N/A')}")
                
                print(f"\n🎬 TRADING INSTRUCTIONS:")
                if signal.get('entry_signal') == '🚀 ENTER NOW':
                    direction = signal.get('direction', 'UP')
                    duration = signal.get('duration_minutes', 1)
                    
                    print(f"   1. 🖱️ Click the {direction} button on QXBroker")
                    print(f"   2. ⏰ Set expiration to {duration} minute{'s' if duration > 1 else ''}")
                    print(f"   3. 💰 Confirm $1.00 investment")
                    print(f"   4. ⏳ Wait {duration} minute{'s' if duration > 1 else ''} for result")
                    print(f"   5. 📊 Expected success rate: {signal.get('confidence', 0):.1f}%")
                    
                elif signal.get('entry_signal') == '⚡ PREPARE':
                    print(f"   1. ⚡ Get ready for {signal.get('direction', 'UP')} signal")
                    print(f"   2. 👀 Monitor price action closely")
                    print(f"   3. ⏰ Entry expected in next 30 seconds")
                    
                elif signal.get('entry_signal') == '⏰ GET READY':
                    print(f"   1. 📊 {signal.get('direction', 'UP')} setup developing")
                    print(f"   2. ⏰ Entry expected in 1-2 minutes")
                    print(f"   3. 🔄 Refresh for updated signal")
                    
                else:
                    print(f"   1. ⏳ Wait for better entry opportunity")
                    print(f"   2. 🔄 Check again in 1 minute")
                    print(f"   3. 📊 Monitor market conditions")
                
                # Show technical analysis summary
                if 'analysis_summary' in signal:
                    print(f"\n📈 TECHNICAL SUMMARY:")
                    print(f"   {signal['analysis_summary']}")
                
                confluence_score = signal.get('confluence_score', 0)
                if confluence_score > 0:
                    print(f"   🔗 Confluence Factors: {confluence_score}/4")
                
            else:
                print(f"❌ Signal Error: {signal_response.status_code}")
        
        else:
            print(f"❌ Quote Error: {quote_response.status_code}")
            
    except Exception as e:
        print(f"❌ Session Error: {e}")

def display_qxbroker_dashboard():
    """Display QXBroker-style dashboard"""
    print("\n" + "=" * 60)
    print("🎯 QXBROKER ADVANCED PREDICTOR DASHBOARD")
    print("=" * 60)
    print("🌐 Platform: qxbroker.com/en/demo-trade")
    print("🔗 Integration: Real-time data & advanced analysis")
    print("📊 Features: Order Blocks, ICT, SMC, SMD, QMLR")
    print("⏰ Timing: Precise 1/5/10 minute entry signals")
    print("=" * 60)
    
    print("\n📋 AVAILABLE TRADING PAIRS:")
    pairs = [
        ("🥇 GOLD_OTC", "Gold (OTC)", "88% Profit Potential"),
        ("🇦🇷 USDARS_OTC", "USD/ARS (OTC)", "88% Profit Potential"),
        ("🇲🇽 USDMXN_OTC", "USD/MXN (OTC)", "81% Profit Potential"),
        ("🇧🇷 USDBRL_OTC", "USD/BRL (OTC)", "80% Profit Potential"),
        ("🇨🇦🇨🇭 CADCHF_OTC", "CAD/CHF (OTC)", "77% Profit Potential"),
        ("🇩🇿 USDDZD_OTC", "USD/DZD (OTC)", "77% Profit Potential")
    ]
    
    for symbol, name, profit in pairs:
        print(f"   {symbol:<15} {name:<15} {profit}")
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"1. Start Django server: python quotex_predictor/manage.py runserver")
    print(f"2. Open browser: http://localhost:8000")
    print(f"3. Select trading pair from QXBroker OTC selection")
    print(f"4. Get live quotes and precise entry signals")
    print(f"5. Follow signals on QXBroker demo platform")
    
    print(f"\n📱 MOBILE TRADING:")
    print(f"• Access QXBroker mobile app")
    print(f"• Use our web interface for signals")
    print(f"• Execute trades on mobile platform")
    print(f"• Real-time synchronization")

def main():
    """Main test function"""
    print("🎯 QXBROKER INTEGRATION TEST SUITE")
    print("=" * 60)
    print("✅ QXBroker Demo Platform Integration")
    print("✅ Real-time Price Simulation")
    print("✅ Advanced Technical Analysis")
    print("✅ Precise Entry Signal System")
    print("✅ Live Quote Display")
    print("✅ Order Blocks, ICT, SMC, SMD, QMLR")
    
    # Display dashboard first
    display_qxbroker_dashboard()
    
    print(f"\n⚠️ NOTE: Server must be running for API tests")
    print(f"Run: python quotex_predictor/manage.py runserver")
    
    # Ask user if they want to run API tests
    try:
        user_input = input(f"\n🤔 Run API tests? (y/n): ").lower().strip()
        
        if user_input == 'y':
            print(f"\n🚀 Running API tests...")
            test_qxbroker_quotes()
            test_precise_entry_signals()
            simulate_qxbroker_trading_session()
            
            print(f"\n🎉 ALL TESTS COMPLETED!")
            print(f"🌐 Open http://localhost:8000 to use the web interface")
            
        else:
            print(f"\n✅ Dashboard displayed. Start the server to test APIs.")
            
    except KeyboardInterrupt:
        print(f"\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")

if __name__ == "__main__":
    main()