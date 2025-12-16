#!/usr/bin/env python3
"""
Test script to verify real market prices are working correctly
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'quotex_predictor'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quotex_predictor.settings')

# Setup Django
django.setup()

from predictor.data_sources import DataSourceManager, QXBrokerSource

def test_real_prices():
    """Test real market price fetching"""
    print("🔍 Testing Real Market Price Fetching")
    print("=" * 50)
    
    # Initialize data source manager
    data_manager = DataSourceManager()
    qx_source = QXBrokerSource()
    
    # Test symbols
    test_symbols = [
        'USDARS_OTC',  # This should show ~1510 as per user's image
        'GOLD_OTC',
        'USDMXN_OTC',
        'USDBRL_OTC',
        'EURUSD'
    ]
    
    print("\n📊 Testing Current Prices:")
    for symbol in test_symbols:
        try:
            # Test QXBroker source directly
            qx_price = qx_source.get_current_price(symbol)
            
            # Test data manager
            dm_data = data_manager.get_price_data(symbol, '1h', 1)
            dm_price = dm_data['close'].iloc[-1] if dm_data is not None and not dm_data.empty else None
            
            print(f"\n{symbol}:")
            print(f"  QXBroker Source: {qx_price:.5f}" if qx_price else "  QXBroker Source: None")
            print(f"  Data Manager:    {dm_price:.5f}" if dm_price else "  Data Manager:    None")
            
            # Special check for USD/ARS
            if symbol == 'USDARS_OTC' and qx_price:
                if 1400 <= qx_price <= 1600:
                    print(f"  ✅ USD/ARS price {qx_price:.2f} is in expected range (1400-1600)")
                    if 1500 <= qx_price <= 1520:
                        print(f"  🎯 USD/ARS price {qx_price:.2f} matches user's image (~1510)!")
                else:
                    print(f"  ⚠️  USD/ARS price {qx_price:.2f} is outside expected range")
            
        except Exception as e:
            print(f"\n{symbol}: ❌ Error - {e}")
    
    print("\n🌐 Testing Real Market Data Sources:")
    
    # Test USD/ARS real rate specifically
    try:
        real_usdars = qx_source._get_usdars_real_rate()
        print(f"USD/ARS Real Rate: {real_usdars:.2f}" if real_usdars else "USD/ARS Real Rate: None")
        
        if real_usdars and 1400 <= real_usdars <= 1600:
            print("✅ USD/ARS real rate is in expected range")
        elif real_usdars:
            print("⚠️  USD/ARS real rate is outside expected range")
    except Exception as e:
        print(f"USD/ARS Real Rate: ❌ Error - {e}")
    
    # Test real market prices collection
    try:
        real_prices = qx_source._get_real_market_prices()
        print(f"\nReal Market Prices Found: {len(real_prices)} symbols")
        for symbol, price in real_prices.items():
            print(f"  {symbol}: {price:.5f}")
    except Exception as e:
        print(f"Real Market Prices: ❌ Error - {e}")
    
    print("\n🔄 Testing Live Quote API:")
    
    # Test live quote functionality
    for symbol in ['USDARS_OTC', 'GOLD_OTC']:
        try:
            quote = qx_source.get_live_quote(symbol)
            if quote:
                print(f"\n{symbol} Live Quote:")
                print(f"  Current Price: {quote['current_price']:.5f}")
                print(f"  Change: {quote['change']:+.5f} ({quote['change_percent']:+.2f}%)")
                print(f"  Data Source: {quote['data_source']}")
                print(f"  Timestamp: {quote['timestamp']}")
            else:
                print(f"\n{symbol}: No live quote available")
        except Exception as e:
            print(f"\n{symbol} Live Quote: ❌ Error - {e}")

if __name__ == "__main__":
    test_real_prices()