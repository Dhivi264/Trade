#!/usr/bin/env python3
"""
Test script for the new Advanced Technical Analysis system
Tests the 5-minute direction prediction using 1H/4H market structure analysis
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append('quotex_predictor')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quotex_predictor.settings')
django.setup()

from predictor.technical_analysis import AdvancedTechnicalAnalyzer
from predictor.data_sources import DataSourceManager

def test_advanced_analysis():
    """Test the new advanced technical analysis system"""
    print("🚀 Testing Advanced Technical Analysis System")
    print("=" * 60)
    
    # Test symbols from Quotex platform
    test_symbols = [
        'EURUSD_OTC',
        'GBPUSD_OTC', 
        'USDJPY_OTC',
        'NZDJPY_OTC',
        'AUDCAD_OTC'
    ]
    
    data_manager = DataSourceManager()
    analyzer = AdvancedTechnicalAnalyzer()
    
    for symbol in test_symbols:
        print(f"\n📊 Analyzing {symbol}")
        print("-" * 40)
        
        try:
            # Get multi-timeframe data
            multi_tf_data = data_manager.get_multi_timeframe_data(symbol, ['1h', '4h'], 100)
            
            if not multi_tf_data or '1h' not in multi_tf_data:
                print(f"❌ No data available for {symbol}")
                continue
            
            # Perform advanced analysis
            analysis = analyzer.analyze(
                df_1h=multi_tf_data['1h'],
                df_4h=multi_tf_data.get('4h', None)
            )
            
            # Display results
            print(f"Direction: {analysis['direction']}")
            print(f"Confidence: {analysis['confidence']:.1f}%")
            print(f"Meets Threshold: {analysis['meets_threshold']}")
            print(f"Current Price: {analysis['current_price']:.4f}")
            print(f"Prediction Timeframe: {analysis['prediction_timeframe']}")
            print(f"Analysis Timeframes: {', '.join(analysis['analysis_timeframes'])}")
            
            # Signal breakdown
            signals = analysis['signal_breakdown']
            print(f"Signals - UP: {signals['up_signals']}, DOWN: {signals['down_signals']}")
            
            # Advanced analysis details
            advanced = analysis.get('advanced_analysis', {})
            if advanced:
                print("\n🔍 Advanced Analysis:")
                
                # HTF Bias
                htf_bias = advanced.get('htf_bias', {})
                if htf_bias:
                    print(f"  HTF Bias: {htf_bias.get('bias', 'N/A')} (Strength: {htf_bias.get('strength', 0):.2f})")
                
                # Break of Structure
                bos = advanced.get('bos', {})
                if bos.get('detected'):
                    print(f"  BOS Detected: {bos.get('type', 'N/A')} (Strength: {bos.get('strength', 0):.2f})")
                
                # Change of Character
                choch = advanced.get('choch', {})
                if choch.get('detected'):
                    print(f"  CHoCH Detected: {choch.get('type', 'N/A')} (Strength: {choch.get('strength', 0):.2f})")
                
                # Fair Value Gaps
                fvg = advanced.get('fvg', {})
                if fvg.get('signal'):
                    print(f"  FVG Signal: {fvg.get('signal', 'N/A')} (Unfilled: {fvg.get('unfilled_count', 0)})")
                
                # Support/Resistance
                sr = advanced.get('support_resistance', {})
                if sr.get('signal'):
                    print(f"  S/R Signal: {sr.get('signal', 'N/A')}")
                    if sr.get('nearest_support'):
                        print(f"    Support: {sr['nearest_support']:.4f} (Distance: {sr.get('support_distance', 0):.2f}%)")
                    if sr.get('nearest_resistance'):
                        print(f"    Resistance: {sr['nearest_resistance']:.4f} (Distance: {sr.get('resistance_distance', 0):.2f}%)")
            
            # Confluence factors
            confluence = analysis.get('confluence_factors', {})
            if confluence:
                print("\n🎯 Confluence Factors:")
                for factor, value in confluence.items():
                    print(f"  {factor.replace('_', ' ').title()}: {'✅' if value else '❌'}")
            
            print(f"\n{'✅ VALID PREDICTION' if analysis['meets_threshold'] else '❌ BELOW THRESHOLD'}")
            
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Advanced Technical Analysis Test Complete!")

if __name__ == "__main__":
    test_advanced_analysis()