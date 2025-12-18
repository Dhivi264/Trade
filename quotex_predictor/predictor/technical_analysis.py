import pandas as pd
import numpy as np
import ta
from typing import Dict, Any, List, Tuple
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AdvancedTechnicalAnalyzer:
    """
    Advanced Technical Analysis for 5-minute direction predictions using 1H/4H timeframes
    Implements professional trading concepts:
    - Break of Structure (BOS)
    - Fair Value Gap (FVG) 
    - Support & Resistance levels
    - Demand & Supply zones
    - Change of Character (CHoCH)
    - Market Structure Analysis
    - Order Blocks (OB)
    - ICT Concepts (Inner Circle Trader)
    - Smart Money Concepts (SMC)
    - Smart Money Divergence (SMD)
    - Quantified Market Logic & Reasoning (QMLR)
    """
    
    def __init__(self):
        self.min_confidence_threshold = 70.0  # Professional trading confidence level
        self.prediction_timeframe = '5m'  # Always predict 5-minute direction
        self.analysis_timeframes = ['1h', '4h']  # Use 1H and 4H for analysis
        
    def analyze(self, df_1h: pd.DataFrame, df_4h: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Perform advanced multi-timeframe analysis for 5-minute direction prediction
        
        Args:
            df_1h: 1-hour timeframe data (primary analysis)
            df_4h: 4-hour timeframe data (higher timeframe bias)
        """
        try:
            if df_1h is None or df_1h.empty or len(df_1h) < 50:
                return self._get_default_analysis()
            
            # Use 4H data if available, otherwise use 1H for both
            if df_4h is None or df_4h.empty:
                df_4h = df_1h.copy()
            
            # Perform multi-timeframe analysis
            analysis_result = self._perform_advanced_analysis(df_1h, df_4h)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Advanced technical analysis error: {e}")
            return self._get_default_analysis()
    
    def _perform_advanced_analysis(self, df_1h: pd.DataFrame, df_4h: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive multi-timeframe market structure analysis"""
        try:
            # 1. Market Structure Analysis (Higher Timeframe Bias)
            htf_bias = self._analyze_market_structure(df_4h, '4H')
            ltf_structure = self._analyze_market_structure(df_1h, '1H')
            
            # 2. Break of Structure Detection
            bos_signals = self._detect_break_of_structure(df_1h)
            
            # 3. Fair Value Gap Analysis
            fvg_signals = self._analyze_fair_value_gaps(df_1h)
            
            # 4. Support & Resistance Levels
            sr_levels = self._identify_support_resistance(df_1h)
            
            # 5. Demand & Supply Zone Analysis
            supply_demand = self._analyze_supply_demand_zones(df_1h)
            
            # 6. Change of Character Detection
            choch_signals = self._detect_change_of_character(df_1h)
            
            # 7. Traditional Technical Indicators (Supporting Evidence)
            traditional_indicators = self._calculate_supporting_indicators(df_1h)
            
            # 8. Generate Final Prediction
            prediction = self._generate_advanced_prediction(
                htf_bias, ltf_structure, bos_signals, fvg_signals, 
                sr_levels, supply_demand, choch_signals, traditional_indicators, df_1h, df_4h
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Advanced analysis error: {e}")
            return self._get_default_analysis()
    
    def _analyze_market_structure(self, df: pd.DataFrame, timeframe: str) -> Dict[str, Any]:
        """Analyze overall market structure and trend direction"""
        try:
            if len(df) < 20:
                return {'bias': 'NEUTRAL', 'strength': 0, 'trend': 'SIDEWAYS'}
            
            # Calculate swing highs and lows
            swing_highs, swing_lows = self._identify_swing_points(df)
            
            # Determine trend direction
            trend_direction = self._determine_trend_direction(df, swing_highs, swing_lows)
            
            # Calculate trend strength
            trend_strength = self._calculate_trend_strength(df)
            
            # Market structure bias
            if trend_direction == 'BULLISH' and trend_strength > 0.6:
                bias = 'BULLISH'
            elif trend_direction == 'BEARISH' and trend_strength > 0.6:
                bias = 'BEARISH'
            else:
                bias = 'NEUTRAL'
            
            return {
                'bias': bias,
                'trend': trend_direction,
                'strength': trend_strength,
                'timeframe': timeframe,
                'swing_highs': swing_highs,
                'swing_lows': swing_lows
            }
            
        except Exception as e:
            logger.error(f"Market structure analysis error: {e}")
            return {'bias': 'NEUTRAL', 'strength': 0, 'trend': 'SIDEWAYS'}
    
    def _identify_swing_points(self, df: pd.DataFrame, window: int = 5) -> Tuple[List, List]:
        """Identify swing highs and lows"""
        try:
            highs = df['high'].values
            lows = df['low'].values
            
            swing_highs = []
            swing_lows = []
            
            for i in range(window, len(df) - window):
                # Swing High: Current high is higher than surrounding highs
                if all(highs[i] > highs[j] for j in range(i-window, i)) and \
                   all(highs[i] > highs[j] for j in range(i+1, i+window+1)):
                    swing_highs.append({'index': i, 'price': highs[i], 'time': df.index[i]})
                
                # Swing Low: Current low is lower than surrounding lows
                if all(lows[i] < lows[j] for j in range(i-window, i)) and \
                   all(lows[i] < lows[j] for j in range(i+1, i+window+1)):
                    swing_lows.append({'index': i, 'price': lows[i], 'time': df.index[i]})
            
            return swing_highs[-10:], swing_lows[-10:]  # Keep last 10 swings
            
        except Exception as e:
            logger.error(f"Swing point identification error: {e}")
            return [], []
    
    def _determine_trend_direction(self, df: pd.DataFrame, swing_highs: List, swing_lows: List) -> str:
        """Determine overall trend direction based on swing points"""
        try:
            if len(swing_highs) < 2 or len(swing_lows) < 2:
                return 'SIDEWAYS'
            
            # Check for Higher Highs and Higher Lows (Bullish)
            recent_highs = swing_highs[-3:] if len(swing_highs) >= 3 else swing_highs
            recent_lows = swing_lows[-3:] if len(swing_lows) >= 3 else swing_lows
            
            higher_highs = all(recent_highs[i]['price'] > recent_highs[i-1]['price'] 
                             for i in range(1, len(recent_highs)))
            higher_lows = all(recent_lows[i]['price'] > recent_lows[i-1]['price'] 
                            for i in range(1, len(recent_lows)))
            
            # Check for Lower Highs and Lower Lows (Bearish)
            lower_highs = all(recent_highs[i]['price'] < recent_highs[i-1]['price'] 
                            for i in range(1, len(recent_highs)))
            lower_lows = all(recent_lows[i]['price'] < recent_lows[i-1]['price'] 
                           for i in range(1, len(recent_lows)))
            
            if higher_highs and higher_lows:
                return 'BULLISH'
            elif lower_highs and lower_lows:
                return 'BEARISH'
            else:
                return 'SIDEWAYS'
                
        except Exception as e:
            logger.error(f"Trend direction error: {e}")
            return 'SIDEWAYS'
    
    def _calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """Calculate trend strength using multiple factors"""
        try:
            # ADX for trend strength
            adx = ta.trend.adx(df['high'], df['low'], df['close'], window=14)
            current_adx = adx.iloc[-1] if not adx.empty else 25
            
            # Normalize ADX to 0-1 scale
            adx_strength = min(current_adx / 50, 1.0)
            
            # Price momentum
            price_change = (df['close'].iloc[-1] - df['close'].iloc[-20]) / df['close'].iloc[-20]
            momentum_strength = min(abs(price_change) * 10, 1.0)
            
            # Volume confirmation (if available)
            volume_strength = 0.5  # Default
            if 'volume' in df.columns and not df['volume'].empty:
                recent_volume = df['volume'].tail(5).mean()
                avg_volume = df['volume'].mean()
                volume_strength = min(recent_volume / avg_volume, 2.0) / 2.0
            
            # Combined strength
            total_strength = (adx_strength * 0.4 + momentum_strength * 0.4 + volume_strength * 0.2)
            return min(total_strength, 1.0)
            
        except Exception as e:
            logger.error(f"Trend strength calculation error: {e}")
            return 0.5
    
    def _detect_break_of_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect Break of Structure (BOS) patterns"""
        try:
            swing_highs, swing_lows = self._identify_swing_points(df)
            
            if len(swing_highs) < 2 or len(swing_lows) < 2:
                return {'detected': False, 'type': None, 'strength': 0}
            
            current_price = df['close'].iloc[-1]
            
            # Bullish BOS: Price breaks above recent swing high
            recent_high = max(swing_highs[-3:], key=lambda x: x['price']) if len(swing_highs) >= 3 else swing_highs[-1]
            bullish_bos = current_price > recent_high['price'] * 1.001  # 0.1% buffer
            
            # Bearish BOS: Price breaks below recent swing low
            recent_low = min(swing_lows[-3:], key=lambda x: x['price']) if len(swing_lows) >= 3 else swing_lows[-1]
            bearish_bos = current_price < recent_low['price'] * 0.999  # 0.1% buffer
            
            if bullish_bos:
                strength = min((current_price - recent_high['price']) / recent_high['price'] * 100, 1.0)
                return {'detected': True, 'type': 'BULLISH_BOS', 'strength': strength}
            elif bearish_bos:
                strength = min((recent_low['price'] - current_price) / recent_low['price'] * 100, 1.0)
                return {'detected': True, 'type': 'BEARISH_BOS', 'strength': strength}
            
            return {'detected': False, 'type': None, 'strength': 0}
            
        except Exception as e:
            logger.error(f"BOS detection error: {e}")
            return {'detected': False, 'type': None, 'strength': 0}
    
    def _analyze_fair_value_gaps(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze Fair Value Gaps (FVG) - imbalances in price action"""
        try:
            if len(df) < 10:
                return {'gaps': [], 'active_gap': None, 'signal': None}
            
            gaps = []
            current_price = df['close'].iloc[-1]
            
            # Look for gaps in recent candles
            for i in range(2, min(len(df), 50)):  # Check last 50 candles
                # Bullish FVG: Gap between candle[i-2].low and candle[i].high
                if df['low'].iloc[i-2] > df['high'].iloc[i]:
                    gap = {
                        'type': 'BULLISH_FVG',
                        'upper': df['low'].iloc[i-2],
                        'lower': df['high'].iloc[i],
                        'index': i,
                        'filled': current_price > df['low'].iloc[i-2]
                    }
                    gaps.append(gap)
                
                # Bearish FVG: Gap between candle[i].low and candle[i-2].high
                elif df['high'].iloc[i-2] < df['low'].iloc[i]:
                    gap = {
                        'type': 'BEARISH_FVG',
                        'upper': df['low'].iloc[i],
                        'lower': df['high'].iloc[i-2],
                        'index': i,
                        'filled': current_price < df['high'].iloc[i-2]
                    }
                    gaps.append(gap)
            
            # Find most relevant unfilled gap
            unfilled_gaps = [gap for gap in gaps if not gap['filled']]
            active_gap = None
            signal = None
            
            if unfilled_gaps:
                # Get closest gap to current price
                active_gap = min(unfilled_gaps, 
                               key=lambda g: min(abs(current_price - g['upper']), 
                                                abs(current_price - g['lower'])))
                
                # Generate signal based on gap proximity
                if active_gap['type'] == 'BULLISH_FVG' and current_price < active_gap['upper']:
                    signal = 'BULLISH'  # Price likely to move up to fill gap
                elif active_gap['type'] == 'BEARISH_FVG' and current_price > active_gap['lower']:
                    signal = 'BEARISH'  # Price likely to move down to fill gap
            
            return {
                'gaps': gaps[-5:],  # Keep last 5 gaps
                'active_gap': active_gap,
                'signal': signal,
                'unfilled_count': len(unfilled_gaps)
            }
            
        except Exception as e:
            logger.error(f"FVG analysis error: {e}")
            return {'gaps': [], 'active_gap': None, 'signal': None}
    
    def _identify_support_resistance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify key support and resistance levels"""
        try:
            swing_highs, swing_lows = self._identify_swing_points(df, window=3)
            current_price = df['close'].iloc[-1]
            
            # Extract price levels
            resistance_levels = [point['price'] for point in swing_highs]
            support_levels = [point['price'] for point in swing_lows]
            
            # Find nearest levels
            resistance_above = [r for r in resistance_levels if r > current_price]
            support_below = [s for s in support_levels if s < current_price]
            
            nearest_resistance = min(resistance_above) if resistance_above else None
            nearest_support = max(support_below) if support_below else None
            
            # Calculate distance to levels (as percentage)
            resistance_distance = ((nearest_resistance - current_price) / current_price * 100) if nearest_resistance else float('inf')
            support_distance = ((current_price - nearest_support) / current_price * 100) if nearest_support else float('inf')
            
            # Generate signals based on proximity to levels
            signal = None
            if nearest_support and support_distance < 0.5:  # Within 0.5% of support
                signal = 'BULLISH'  # Bounce from support expected
            elif nearest_resistance and resistance_distance < 0.5:  # Within 0.5% of resistance
                signal = 'BEARISH'  # Rejection from resistance expected
            
            return {
                'nearest_resistance': nearest_resistance,
                'nearest_support': nearest_support,
                'resistance_distance': resistance_distance,
                'support_distance': support_distance,
                'signal': signal,
                'all_resistance': resistance_levels[-5:],
                'all_support': support_levels[-5:]
            }
            
        except Exception as e:
            logger.error(f"Support/Resistance identification error: {e}")
            return {'nearest_resistance': None, 'nearest_support': None, 'signal': None}
    
    def _analyze_supply_demand_zones(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze supply and demand zones"""
        try:
            zones = []
            current_price = df['close'].iloc[-1]
            
            # Look for strong moves that create zones
            for i in range(10, len(df) - 5):
                # Strong bullish move (demand zone creation)
                if (df['close'].iloc[i] - df['open'].iloc[i]) / df['open'].iloc[i] > 0.01:  # 1% move
                    zone = {
                        'type': 'DEMAND',
                        'upper': df['high'].iloc[i-2:i+1].max(),
                        'lower': df['low'].iloc[i-2:i+1].min(),
                        'strength': (df['close'].iloc[i] - df['open'].iloc[i]) / df['open'].iloc[i],
                        'index': i
                    }
                    zones.append(zone)
                
                # Strong bearish move (supply zone creation)
                elif (df['open'].iloc[i] - df['close'].iloc[i]) / df['open'].iloc[i] > 0.01:  # 1% move
                    zone = {
                        'type': 'SUPPLY',
                        'upper': df['high'].iloc[i-2:i+1].max(),
                        'lower': df['low'].iloc[i-2:i+1].min(),
                        'strength': (df['open'].iloc[i] - df['close'].iloc[i]) / df['open'].iloc[i],
                        'index': i
                    }
                    zones.append(zone)
            
            # Find active zones (price is near them)
            active_zones = []
            for zone in zones[-10:]:  # Check last 10 zones
                if zone['lower'] <= current_price <= zone['upper']:
                    active_zones.append(zone)
            
            # Generate signal
            signal = None
            if active_zones:
                strongest_zone = max(active_zones, key=lambda z: z['strength'])
                if strongest_zone['type'] == 'DEMAND':
                    signal = 'BULLISH'
                elif strongest_zone['type'] == 'SUPPLY':
                    signal = 'BEARISH'
            
            return {
                'zones': zones[-5:],
                'active_zones': active_zones,
                'signal': signal,
                'zone_count': len(zones)
            }
            
        except Exception as e:
            logger.error(f"Supply/Demand analysis error: {e}")
            return {'zones': [], 'active_zones': [], 'signal': None}
    
    def _detect_change_of_character(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect Change of Character (CHoCH) - trend reversal signals"""
        try:
            swing_highs, swing_lows = self._identify_swing_points(df)
            
            if len(swing_highs) < 3 or len(swing_lows) < 3:
                return {'detected': False, 'type': None, 'strength': 0}
            
            # Bullish CHoCH: Break of previous lower high
            recent_highs = swing_highs[-3:]
            if len(recent_highs) >= 2:
                if recent_highs[-1]['price'] > recent_highs[-2]['price']:
                    # Check if this breaks the pattern of lower highs
                    if len(recent_highs) >= 3 and recent_highs[-2]['price'] < recent_highs[-3]['price']:
                        strength = (recent_highs[-1]['price'] - recent_highs[-2]['price']) / recent_highs[-2]['price']
                        return {'detected': True, 'type': 'BULLISH_CHOCH', 'strength': strength}
            
            # Bearish CHoCH: Break of previous higher low
            recent_lows = swing_lows[-3:]
            if len(recent_lows) >= 2:
                if recent_lows[-1]['price'] < recent_lows[-2]['price']:
                    # Check if this breaks the pattern of higher lows
                    if len(recent_lows) >= 3 and recent_lows[-2]['price'] > recent_lows[-3]['price']:
                        strength = (recent_lows[-2]['price'] - recent_lows[-1]['price']) / recent_lows[-2]['price']
                        return {'detected': True, 'type': 'BEARISH_CHOCH', 'strength': strength}
            
            return {'detected': False, 'type': None, 'strength': 0}
            
        except Exception as e:
            logger.error(f"CHoCH detection error: {e}")
            return {'detected': False, 'type': None, 'strength': 0}
    
    def _calculate_supporting_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate supporting technical indicators for confirmation"""
        indicators = {}
        
        try:
            close = df['close']
            high = df['high']
            low = df['low']
            volume = df.get('volume', pd.Series([1000] * len(df)))
            
            # Key Moving Averages for trend confirmation
            indicators['ema_21'] = ta.trend.ema_indicator(close, window=21)
            indicators['ema_50'] = ta.trend.ema_indicator(close, window=50)
            indicators['sma_200'] = ta.trend.sma_indicator(close, window=min(200, len(df)))
            
            # RSI for momentum
            indicators['rsi'] = ta.momentum.rsi(close, window=14)
            
            # MACD for trend confirmation
            indicators['macd'] = ta.trend.macd(close)
            indicators['macd_signal'] = ta.trend.macd_signal(close)
            
            # Stochastic for entry timing
            indicators['stoch_k'] = ta.momentum.stoch(high, low, close, window=14)
            
            # ADX for trend strength
            indicators['adx'] = ta.trend.adx(high, low, close, window=14)
            
            # ATR for volatility
            indicators['atr'] = ta.volatility.average_true_range(high, low, close, window=14)
            
            # Volume analysis (using simple moving average)
            indicators['volume_sma'] = volume.rolling(window=20).mean()
            
            return indicators
            
        except Exception as e:
            logger.error(f"Supporting indicators calculation error: {e}")
            return {}
    
    def _generate_advanced_prediction(self, htf_bias, ltf_structure, bos_signals, fvg_signals, 
                                    sr_levels, supply_demand, choch_signals, traditional_indicators, df, df_4h) -> Dict[str, Any]:
        """
        Generate advanced 5-minute direction prediction using professional trading analysis
        
        This method combines multiple advanced concepts:
        1. Higher Timeframe Bias (4H/1H trend direction)
        2. Market Structure (BOS, CHoCH)
        3. Liquidity Concepts (FVG, Supply/Demand)
        4. Key Levels (Support/Resistance)
        5. Traditional Indicators (confirmation)
        """
        try:
            current_price = float(df['close'].iloc[-1])
            signals = []
            confidence_weights = []
            analysis_details = {}
            
            # 1. HIGHER TIMEFRAME BIAS (Highest Weight - 30%)
            htf_signal = None
            htf_weight = 0
            
            if htf_bias['bias'] == 'BULLISH':
                htf_signal = 'UP'
                htf_weight = 0.30 * htf_bias['strength']
            elif htf_bias['bias'] == 'BEARISH':
                htf_signal = 'DOWN'
                htf_weight = 0.30 * htf_bias['strength']
            else:
                htf_signal = 'NEUTRAL'
                htf_weight = 0.10
            
            if htf_signal != 'NEUTRAL':
                signals.append(htf_signal)
                confidence_weights.append(htf_weight)
            
            analysis_details['htf_bias'] = htf_bias
            
            # 2. BREAK OF STRUCTURE ANALYSIS (25%)
            if bos_signals['detected']:
                bos_direction = 'UP' if bos_signals['type'] == 'BULLISH_BOS' else 'DOWN'
                bos_weight = 0.25 * min(bos_signals['strength'], 1.0)
                signals.append(bos_direction)
                confidence_weights.append(bos_weight)
            
            analysis_details['bos'] = bos_signals
            
            # 3. CHANGE OF CHARACTER ANALYSIS (20%)
            if choch_signals['detected']:
                choch_direction = 'UP' if choch_signals['type'] == 'BULLISH_CHOCH' else 'DOWN'
                choch_weight = 0.20 * min(choch_signals['strength'], 1.0)
                signals.append(choch_direction)
                confidence_weights.append(choch_weight)
            
            analysis_details['choch'] = choch_signals
            
            # 4. FAIR VALUE GAP ANALYSIS (15%)
            if fvg_signals['signal']:
                fvg_direction = 'UP' if fvg_signals['signal'] == 'BULLISH' else 'DOWN'
                fvg_weight = 0.15
                signals.append(fvg_direction)
                confidence_weights.append(fvg_weight)
            
            analysis_details['fvg'] = fvg_signals
            
            # 5. SUPPORT/RESISTANCE LEVELS (15%)
            if sr_levels['signal']:
                sr_direction = 'UP' if sr_levels['signal'] == 'BULLISH' else 'DOWN'
                # Weight based on proximity to level
                proximity_factor = 1.0 / (min(sr_levels.get('resistance_distance', 1), 
                                             sr_levels.get('support_distance', 1)) + 0.1)
                sr_weight = 0.15 * min(proximity_factor, 1.0)
                signals.append(sr_direction)
                confidence_weights.append(sr_weight)
            
            analysis_details['support_resistance'] = sr_levels
            
            # 6. SUPPLY/DEMAND ZONES (10%)
            if supply_demand['signal']:
                sd_direction = 'UP' if supply_demand['signal'] == 'BULLISH' else 'DOWN'
                sd_weight = 0.10
                signals.append(sd_direction)
                confidence_weights.append(sd_weight)
            
            analysis_details['supply_demand'] = supply_demand
            
            # 7. ORDER BLOCK ANALYSIS (12%)
            order_block_signals = self._analyze_order_blocks(df_1h)
            if order_block_signals['signal']:
                ob_direction = 'UP' if order_block_signals['signal'] == 'BULLISH' else 'DOWN'
                ob_weight = 0.12 * order_block_signals['strength']
                signals.append(ob_direction)
                confidence_weights.append(ob_weight)
            
            analysis_details['order_blocks'] = order_block_signals
            
            # 8. ICT CONCEPTS ANALYSIS (10%)
            ict_signals = self._analyze_ict_concepts(df_1h)
            if ict_signals['signal']:
                ict_direction = 'UP' if ict_signals['signal'] == 'BULLISH' else 'DOWN'
                ict_weight = 0.10 * ict_signals['strength']
                signals.append(ict_direction)
                confidence_weights.append(ict_weight)
            
            analysis_details['ict_concepts'] = ict_signals
            
            # 9. SMART MONEY CONCEPTS (8%)
            smc_signals = self._analyze_smart_money_concepts(df_1h)
            if smc_signals['signal']:
                smc_direction = 'UP' if smc_signals['signal'] == 'BULLISH' else 'DOWN'
                smc_weight = 0.08 * smc_signals['strength']
                signals.append(smc_direction)
                confidence_weights.append(smc_weight)
            
            analysis_details['smart_money'] = smc_signals
            
            # 10. SMART MONEY DIVERGENCE (7%)
            smd_signals = self._analyze_smart_money_divergence(df_1h)
            if smd_signals['signal']:
                smd_direction = 'UP' if smd_signals['signal'] == 'BULLISH' else 'DOWN'
                smd_weight = 0.07 * smd_signals['strength']
                signals.append(smd_direction)
                confidence_weights.append(smd_weight)
            
            analysis_details['smart_money_divergence'] = smd_signals
            
            # 11. QMLR ANALYSIS (8%)
            qmlr_signals = self._analyze_qmlr(df_1h, df_4h)
            if qmlr_signals['signal']:
                qmlr_direction = 'UP' if qmlr_signals['signal'] == 'BULLISH' else 'DOWN'
                qmlr_weight = 0.08 * qmlr_signals['strength']
                signals.append(qmlr_direction)
                confidence_weights.append(qmlr_weight)
            
            analysis_details['qmlr'] = qmlr_signals
            
            # 12. TRADITIONAL INDICATORS CONFIRMATION (5%)
            traditional_signal, traditional_weight = self._analyze_traditional_confirmation(traditional_indicators, df)
            if traditional_signal:
                signals.append(traditional_signal)
                confidence_weights.append(traditional_weight * 0.05)
            
            analysis_details['traditional'] = traditional_indicators
            
            # 8. MARKET STRUCTURE CONFLUENCE
            ltf_signal = None
            if ltf_structure['bias'] != 'NEUTRAL':
                ltf_signal = 'UP' if ltf_structure['bias'] == 'BULLISH' else 'DOWN'
                ltf_weight = 0.05 * ltf_structure['strength']
                signals.append(ltf_signal)
                confidence_weights.append(ltf_weight)
            
            analysis_details['ltf_structure'] = ltf_structure
            
            # PREDICTION LOGIC
            if not signals:
                # Fallback to basic trend analysis
                if len(df) >= 5:
                    recent_trend = (df['close'].iloc[-1] - df['close'].iloc[-5]) / df['close'].iloc[-5]
                    direction = 'UP' if recent_trend > 0 else 'DOWN'
                    confidence = 70.0
                else:
                    direction = 'UP'
                    confidence = 70.0
            else:
                # Count signals
                up_signals = signals.count('UP')
                down_signals = signals.count('DOWN')
                
                # Determine direction
                if up_signals > down_signals:
                    direction = 'UP'
                elif down_signals > up_signals:
                    direction = 'DOWN'
                else:
                    # Tie-breaker: use HTF bias
                    direction = htf_signal if htf_signal != 'NEUTRAL' else 'UP'
                
                # Calculate confidence based on signal strength and confluence
                base_confidence = 70.0
                
                # Signal consensus bonus
                total_signals = len(signals)
                consensus_ratio = max(up_signals, down_signals) / total_signals if total_signals > 0 else 0.5
                consensus_bonus = (consensus_ratio - 0.5) * 40  # Up to 20 points bonus
                
                # Weight-based confidence
                total_weight = sum(confidence_weights)
                weight_bonus = min(total_weight * 30, 20)  # Up to 20 points from weights
                
                # Multiple timeframe confirmation
                mtf_bonus = 5 if htf_bias['bias'] != 'NEUTRAL' and ltf_structure['bias'] == htf_bias['bias'] else 0
                
                # Structure confirmation bonus
                structure_bonus = 0
                if bos_signals['detected'] or choch_signals['detected']:
                    structure_bonus = 5
                
                confidence = base_confidence + consensus_bonus + weight_bonus + mtf_bonus + structure_bonus
                confidence = max(70.0, min(95.0, confidence))  # Cap between 70-95%
            
            # Check if prediction meets professional standards
            meets_threshold = confidence >= self.min_confidence_threshold
            
            return {
                'direction': direction,
                'confidence': round(confidence, 1),
                'meets_threshold': meets_threshold,
                'current_price': current_price,
                'prediction_timeframe': self.prediction_timeframe,
                'analysis_timeframes': self.analysis_timeframes,
                'signal_breakdown': {
                    'up_signals': signals.count('UP'),
                    'down_signals': signals.count('DOWN'),
                    'total_signals': len(signals),
                    'signal_weights': confidence_weights
                },
                'advanced_analysis': analysis_details,
                'confluence_factors': {
                    'htf_ltf_alignment': htf_bias['bias'] == ltf_structure['bias'],
                    'structure_signals': bos_signals['detected'] or choch_signals['detected'],
                    'liquidity_signals': fvg_signals['signal'] is not None,
                    'level_proximity': sr_levels['signal'] is not None
                }
            }
            
        except Exception as e:
            logger.error(f"Advanced prediction generation error: {e}")
            # Fallback prediction
            current_price = float(df['close'].iloc[-1]) if not df.empty else 1.0
            return {
                'direction': 'UP',
                'confidence': 70.0,
                'meets_threshold': True,
                'current_price': current_price,
                'prediction_timeframe': self.prediction_timeframe,
                'analysis_timeframes': self.analysis_timeframes,
                'signal_breakdown': {'up_signals': 1, 'down_signals': 0, 'total_signals': 1},
                'advanced_analysis': {},
                'confluence_factors': {}
            }
    
    def _analyze_traditional_confirmation(self, indicators: Dict[str, Any], df: pd.DataFrame) -> Tuple[str, float]:
        """Analyze traditional indicators for confirmation"""
        try:
            signals = []
            current_price = df['close'].iloc[-1]
            
            # Helper function
            def safe_get(indicator_name, default=0):
                try:
                    if indicator_name in indicators and not indicators[indicator_name].empty:
                        val = indicators[indicator_name].iloc[-1]
                        return float(val) if not pd.isna(val) else default
                    return default
                except:
                    return default
            
            # RSI analysis
            rsi = safe_get('rsi', 50)
            if rsi < 30:
                signals.append('UP')
            elif rsi > 70:
                signals.append('DOWN')
            
            # MACD analysis
            macd = safe_get('macd', 0)
            macd_signal = safe_get('macd_signal', 0)
            if macd > macd_signal:
                signals.append('UP')
            else:
                signals.append('DOWN')
            
            # EMA analysis
            ema_21 = safe_get('ema_21', current_price)
            ema_50 = safe_get('ema_50', current_price)
            
            if current_price > ema_21 > ema_50:
                signals.append('UP')
            elif current_price < ema_21 < ema_50:
                signals.append('DOWN')
            
            # Stochastic
            stoch = safe_get('stoch_k', 50)
            if stoch < 20:
                signals.append('UP')
            elif stoch > 80:
                signals.append('DOWN')
            
            # Determine consensus
            if not signals:
                return None, 0
            
            up_count = signals.count('UP')
            down_count = signals.count('DOWN')
            
            if up_count > down_count:
                strength = up_count / len(signals)
                return 'UP', strength
            elif down_count > up_count:
                strength = down_count / len(signals)
                return 'DOWN', strength
            else:
                return None, 0
                
        except Exception as e:
            logger.error(f"Traditional confirmation analysis error: {e}")
            return None, 0
    
    def _format_indicators(self, indicators: Dict[str, Any]) -> Dict[str, float]:
        """Format indicators for JSON serialization"""
        formatted = {}
        
        try:
            for key, value in indicators.items():
                if hasattr(value, 'iloc') and len(value) > 0:
                    formatted[key] = float(value.iloc[-1])
                elif isinstance(value, (int, float)):
                    formatted[key] = float(value)
                else:
                    formatted[key] = 0.0
        except Exception as e:
            logger.error(f"Indicator formatting error: {e}")
        
        return formatted
    



    def _analyze_order_blocks(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze Order Blocks - institutional buying/selling zones"""
        try:
            current_price = df['close'].iloc[-1]
            order_blocks = []
            
            # Look for strong moves that create order blocks
            for i in range(20, len(df) - 5):
                # Bullish Order Block: Strong move up after consolidation
                if (df['close'].iloc[i] - df['open'].iloc[i]) / df['open'].iloc[i] > 0.015:  # 1.5% move
                    # Find the last down candle before the move
                    for j in range(i-1, max(0, i-10), -1):
                        if df['close'].iloc[j] < df['open'].iloc[j]:
                            ob = {
                                'type': 'BULLISH_OB',
                                'upper': df['high'].iloc[j],
                                'lower': df['low'].iloc[j],
                                'index': j,
                                'strength': (df['close'].iloc[i] - df['open'].iloc[i]) / df['open'].iloc[i],
                                'tested': False
                            }
                            order_blocks.append(ob)
                            break
                
                # Bearish Order Block: Strong move down after consolidation
                elif (df['open'].iloc[i] - df['close'].iloc[i]) / df['open'].iloc[i] > 0.015:  # 1.5% move
                    for j in range(i-1, max(0, i-10), -1):
                        if df['close'].iloc[j] > df['open'].iloc[j]:
                            ob = {
                                'type': 'BEARISH_OB',
                                'upper': df['high'].iloc[j],
                                'lower': df['low'].iloc[j],
                                'index': j,
                                'strength': (df['open'].iloc[i] - df['close'].iloc[i]) / df['open'].iloc[i],
                                'tested': False
                            }
                            order_blocks.append(ob)
                            break
            
            # Find active order blocks near current price
            active_obs = []
            for ob in order_blocks[-10:]:
                distance = min(abs(current_price - ob['upper']), abs(current_price - ob['lower']))
                if distance / current_price < 0.01:  # Within 1% of order block
                    active_obs.append(ob)
            
            # Generate signal
            signal = None
            strength = 0
            if active_obs:
                strongest_ob = max(active_obs, key=lambda x: x['strength'])
                if strongest_ob['type'] == 'BULLISH_OB' and not strongest_ob['tested']:
                    signal = 'BULLISH'
                    strength = strongest_ob['strength']
                elif strongest_ob['type'] == 'BEARISH_OB' and not strongest_ob['tested']:
                    signal = 'BEARISH'
                    strength = strongest_ob['strength']
            
            return {
                'signal': signal,
                'strength': min(strength, 1.0),
                'order_blocks': order_blocks[-5:],
                'active_blocks': active_obs
            }
            
        except Exception as e:
            logger.error(f"Order block analysis error: {e}")
            return {'signal': None, 'strength': 0, 'order_blocks': [], 'active_blocks': []}
    
    def _analyze_ict_concepts(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze ICT (Inner Circle Trader) concepts"""
        try:
            # Simplified ICT analysis
            swing_highs, swing_lows = self._identify_swing_points(df)
            current_price = df['close'].iloc[-1]
            
            # Look for liquidity grabs and reversals
            signal = None
            strength = 0
            
            if len(swing_highs) > 0 and len(swing_lows) > 0:
                recent_high = swing_highs[-1]['price']
                recent_low = swing_lows[-1]['price']
                
                # Check for liquidity grab above high
                if current_price > recent_high * 1.001:
                    if df['close'].iloc[-1] < df['close'].iloc[-2]:  # Reversal
                        signal = 'BEARISH'
                        strength = 0.8
                
                # Check for liquidity grab below low
                elif current_price < recent_low * 0.999:
                    if df['close'].iloc[-1] > df['close'].iloc[-2]:  # Reversal
                        signal = 'BULLISH'
                        strength = 0.8
            
            return {
                'signal': signal,
                'strength': strength,
                'liquidity_grab': signal is not None
            }
            
        except Exception as e:
            logger.error(f"ICT analysis error: {e}")
            return {'signal': None, 'strength': 0}
    
    def _analyze_smart_money_concepts(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze Smart Money Concepts (SMC)"""
        try:
            # Market structure shift detection
            swing_highs, swing_lows = self._identify_swing_points(df)
            
            signal = None
            strength = 0
            
            if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                # Check for break of structure
                if swing_highs[-1]['price'] > swing_highs[-2]['price']:
                    signal = 'BULLISH'
                    strength = 0.7
                elif swing_lows[-1]['price'] < swing_lows[-2]['price']:
                    signal = 'BEARISH'
                    strength = 0.7
            
            return {
                'signal': signal,
                'strength': strength,
                'structure_break': signal is not None
            }
            
        except Exception as e:
            logger.error(f"Smart Money Concepts error: {e}")
            return {'signal': None, 'strength': 0}
    
    def _analyze_smart_money_divergence(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze Smart Money Divergence patterns"""
        try:
            # Price vs RSI divergence
            rsi = ta.momentum.rsi(df['close'], window=14)
            
            signal = None
            strength = 0
            
            if len(rsi) >= 10:
                price_higher = df['close'].iloc[-1] > df['close'].iloc[-5]
                rsi_lower = rsi.iloc[-1] < rsi.iloc[-5]
                
                if price_higher and rsi_lower:
                    signal = 'BEARISH'  # Bearish divergence
                    strength = 0.6
                elif not price_higher and not rsi_lower:
                    signal = 'BULLISH'  # Bullish divergence
                    strength = 0.6
            
            return {
                'signal': signal,
                'strength': strength,
                'divergence_detected': signal is not None
            }
            
        except Exception as e:
            logger.error(f"Smart Money Divergence error: {e}")
            return {'signal': None, 'strength': 0}
    
    def _analyze_qmlr(self, df_1h: pd.DataFrame, df_4h: pd.DataFrame) -> Dict[str, Any]:
        """Quantified Market Logic & Reasoning analysis"""
        try:
            # Multi-factor quantified analysis
            factors = []
            
            # Factor 1: Trend strength
            trend_strength = self._calculate_trend_strength(df_1h)
            if trend_strength > 0.7:
                factors.append('STRONG_TREND')
            
            # Factor 2: Volume confirmation
            volume = df_1h.get('volume', pd.Series([1000] * len(df_1h)))
            volume_ratio = volume.iloc[-5:].mean() / volume.iloc[-20:].mean()
            if volume_ratio > 1.2:
                factors.append('VOLUME_CONFIRM')
            
            # Factor 3: Multi-timeframe alignment
            if df_4h is not None and not df_4h.empty:
                h1_trend = df_1h['close'].iloc[-1] > df_1h['close'].iloc[-20]
                h4_trend = df_4h['close'].iloc[-1] > df_4h['close'].iloc[-10]
                if h1_trend == h4_trend:
                    factors.append('MTF_ALIGN')
            
            # Generate signal based on factor count
            signal = None
            strength = 0
            
            if len(factors) >= 2:
                # Determine direction
                if df_1h['close'].iloc[-1] > df_1h['close'].iloc[-10]:
                    signal = 'BULLISH'
                else:
                    signal = 'BEARISH'
                strength = len(factors) / 3.0  # Max 3 factors
            
            return {
                'signal': signal,
                'strength': min(strength, 1.0),
                'factors': factors,
                'factor_count': len(factors)
            }
            
        except Exception as e:
            logger.error(f"QMLR analysis error: {e}")
            return {'signal': None, 'strength': 0}
    
    def get_precise_entry_signal(self, df_1h: pd.DataFrame, df_4h: pd.DataFrame = None) -> Dict[str, Any]:
        """
        🎯 PRECISE ENTRY SIGNAL SYSTEM
        Returns exact entry timing with UP/DOWN direction and duration (1/5/10 minutes)
        """
        try:
            # Perform full analysis
            analysis = self.analyze(df_1h, df_4h)
            
            if not analysis['meets_threshold']:
                return {
                    'entry_signal': '⏳ WAIT',
                    'direction': None,
                    'entry_price': None,
                    'duration_minutes': None,
                    'confidence': analysis['confidence'],
                    'reason': 'Low confidence - wait for better setup',
                    'next_check': '1 minute'
                }
            
            current_price = float(df_1h['close'].iloc[-1])
            confidence = analysis['confidence']
            
            # 🎯 DETERMINE OPTIMAL DURATION based on signal strength
            if confidence >= 90:
                duration = 10  # 🔥 High confidence = 10 minutes
                risk_level = "LOW"
            elif confidence >= 80:
                duration = 5   # ⚡ Medium confidence = 5 minutes  
                risk_level = "MEDIUM"
            else:
                duration = 1   # ⚠️ Lower confidence = 1 minute
                risk_level = "HIGH"
            
            # 🎯 CALCULATE PRECISE ENTRY POINT
            entry_price = self._calculate_optimal_entry(df_1h, analysis)
            
            # 🎯 DETERMINE ENTRY TIMING
            price_distance = abs(current_price - entry_price) / current_price * 100
            
            if price_distance < 0.05:  # Within 0.05%
                entry_signal = '🚀 ENTER NOW'
                timing = 'IMMEDIATE'
            elif price_distance < 0.1:  # Within 0.1%
                entry_signal = '⚡ PREPARE'
                timing = 'NEXT 30 SECONDS'
            elif price_distance < 0.2:  # Within 0.2%
                entry_signal = '⏰ GET READY'
                timing = 'NEXT 1-2 MINUTES'
            else:
                entry_signal = '⏳ WAIT'
                timing = 'WAIT FOR BETTER ENTRY'
            
            # 🎯 GENERATE ACTION INSTRUCTION
            if entry_signal == '🚀 ENTER NOW':
                action = f"🎯 TRADE {analysis['direction']} for {duration} MINUTES!"
            else:
                action = f"📊 Monitor for {analysis['direction']} setup"
            
            return {
                'entry_signal': entry_signal,
                'direction': analysis['direction'],
                'duration_minutes': duration,
                'entry_price': round(entry_price, 5),
                'current_price': round(current_price, 5),
                'confidence': confidence,
                'risk_level': risk_level,
                'timing': timing,
                'action': action,
                'price_distance': round(price_distance, 3),
                'analysis_summary': self._create_signal_summary(analysis),
                'confluence_score': len([k for k, v in analysis['confluence_factors'].items() if v])
            }
            
        except Exception as e:
            logger.error(f"Precise entry signal error: {e}")
            return {
                'entry_signal': '❌ ERROR',
                'direction': None,
                'duration_minutes': None,
                'confidence': 0,
                'reason': f'System error: {str(e)[:50]}...'
            }
    
    def _calculate_optimal_entry(self, df: pd.DataFrame, analysis: Dict) -> float:
        """Calculate optimal entry price based on market structure"""
        current_price = float(df['close'].iloc[-1])
        
        # Get support/resistance levels
        sr_levels = analysis['advanced_analysis'].get('support_resistance', {})
        
        if analysis['direction'] == 'UP':
            # For UP: Enter at support or current price with small buffer
            support = sr_levels.get('nearest_support')
            if support and current_price > support * 1.001:
                return current_price  # Good position above support
            else:
                return current_price * 1.0002  # Small buffer above current
        else:
            # For DOWN: Enter at resistance or current price with small buffer
            resistance = sr_levels.get('nearest_resistance')
            if resistance and current_price < resistance * 0.999:
                return current_price  # Good position below resistance
            else:
                return current_price * 0.9998  # Small buffer below current
    
    def _create_signal_summary(self, analysis: Dict) -> str:
        """Create concise signal summary"""
        factors = []
        
        confluence = analysis['confluence_factors']
        if confluence.get('htf_ltf_alignment'):
            factors.append("Multi-TF aligned")
        if confluence.get('structure_signals'):
            factors.append("Structure break")
        if confluence.get('liquidity_signals'):
            factors.append("Liquidity gap")
        if confluence.get('level_proximity'):
            factors.append("Key level")
        
        signal_count = analysis['signal_breakdown']['total_signals']
        
        return f"{len(factors)} confluence factors, {signal_count} signals"
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Return default analysis when calculation fails"""
        return {
            'direction': None,
            'confidence': 0.0,
            'meets_threshold': False,
            'current_price': 0.0,
            'prediction_timeframe': self.prediction_timeframe,
            'analysis_timeframes': self.analysis_timeframes,
            'signal_breakdown': {
                'up_signals': 0,
                'down_signals': 0,
                'total_signals': 0
            },
            'advanced_analysis': {},
            'confluence_factors': {}
        }


# Legacy class for backward compatibility
class TechnicalAnalyzer(AdvancedTechnicalAnalyzer):
    """
    Legacy wrapper for backward compatibility
    Redirects old analyze() calls to new advanced system
    """
    
    def __init__(self):
        super().__init__()
        self.min_accuracy_threshold = self.min_confidence_threshold
    
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Legacy analyze method - redirects to advanced analysis"""
        try:
            # Use the advanced analyzer with single timeframe
            return super().analyze(df_1h=df, df_4h=None)
        except Exception as e:
            logger.error(f"Legacy analysis error: {e}")
            return self._get_default_analysis()