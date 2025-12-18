"""
Chart Visual Analysis Module
Analyzes uploaded chart images for visual patterns while using real price data for predictions
"""

import cv2
import numpy as np
from PIL import Image
import logging
from typing import Dict, Any
from .data_sources import DataSourceManager
from .technical_analysis import AdvancedTechnicalAnalyzer

logger = logging.getLogger(__name__)


class ChartVisualAnalyzer:
    """
    Analyzes uploaded chart images for visual patterns and combines with real price data
    """
    
    def __init__(self):
        self.data_manager = DataSourceManager()
        self.technical_analyzer = AdvancedTechnicalAnalyzer()
        
    def analyze_chart_with_real_data(self, image_path: str, symbol: str, timeframe: str = '1h') -> Dict[str, Any]:
        """
        Analyze chart image for visual patterns and get real price prediction
        
        Args:
            image_path: Path to uploaded chart image
            symbol: Trading pair symbol
            timeframe: Chart timeframe (15m or 1h)
            
        Returns:
            Combined analysis with visual patterns and real price prediction
        """
        try:
            # 1. Analyze visual patterns from chart image
            visual_analysis = self._analyze_visual_patterns(image_path)
            
            # 2. Get real price data and generate prediction
            real_prediction = self._get_real_price_prediction(symbol)
            
            # 3. Combine both analyses
            combined_analysis = {
                'symbol': symbol,
                'timeframe': timeframe,
                'visual_analysis': visual_analysis,
                'real_price_prediction': real_prediction,
                'recommendation': self._generate_recommendation(visual_analysis, real_prediction),
                'analysis_timestamp': None,
                'success': True
            }
            
            return combined_analysis
            
        except Exception as e:
            logger.error(f"Chart analysis error: {e}")
            return self._get_error_analysis(symbol, str(e))
    
    def _analyze_visual_patterns(self, image_path: str) -> Dict[str, Any]:
        """Analyze visual patterns from chart image"""
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Could not load image")
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Basic visual analysis
            visual_patterns = {
                'trend_direction': self._detect_visual_trend(gray),
                'support_resistance': self._detect_visual_levels(gray),
                'pattern_type': self._identify_visual_patterns(gray),
                'chart_quality': self._assess_chart_quality(gray),
                'confidence': 0.6  # Visual analysis has lower confidence
            }
            
            return visual_patterns
            
        except Exception as e:
            logger.error(f"Visual pattern analysis error: {e}")
            return {
                'trend_direction': 'UNKNOWN',
                'support_resistance': {'levels': []},
                'pattern_type': 'UNCLEAR',
                'chart_quality': 'POOR',
                'confidence': 0.3,
                'error': str(e)
            }
    
    def _detect_visual_trend(self, gray_img: np.ndarray) -> str:
        """Detect trend direction from image"""
        try:
            # Simple edge detection to find trend
            edges = cv2.Canny(gray_img, 50, 150)
            
            # Find lines using Hough transform
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=20)
            
            if lines is not None:
                # Analyze line angles
                upward_lines = 0
                downward_lines = 0
                
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    if x2 - x1 != 0:
                        angle = np.arctan((y2 - y1) / (x2 - x1)) * 180 / np.pi
                        if -45 < angle < -10:  # Upward trend (negative angle in image coords)
                            upward_lines += 1
                        elif 10 < angle < 45:   # Downward trend
                            downward_lines += 1
                
                if upward_lines > downward_lines:
                    return 'BULLISH'
                elif downward_lines > upward_lines:
                    return 'BEARISH'
            
            return 'SIDEWAYS'
            
        except Exception as e:
            logger.error(f"Visual trend detection error: {e}")
            return 'UNKNOWN'
    
    def _detect_visual_levels(self, gray_img: np.ndarray) -> Dict[str, Any]:
        """Detect support/resistance levels visually"""
        try:
            # Find horizontal lines
            edges = cv2.Canny(gray_img, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
            
            horizontal_lines = []
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    if abs(y2 - y1) < 10:  # Horizontal line
                        horizontal_lines.append({
                            'y_position': (y1 + y2) // 2,
                            'length': abs(x2 - x1),
                            'strength': abs(x2 - x1) / gray_img.shape[1]
                        })
            
            return {
                'levels': horizontal_lines[:5],  # Top 5 levels
                'count': len(horizontal_lines)
            }
            
        except Exception as e:
            logger.error(f"Visual level detection error: {e}")
            return {'levels': [], 'count': 0}
    
    def _identify_visual_patterns(self, gray_img: np.ndarray) -> str:
        """Identify chart patterns visually"""
        try:
            # Simple pattern recognition based on image characteristics
            height, width = gray_img.shape
            
            # Analyze image variance to determine pattern type
            variance = np.var(gray_img)
            
            if variance < 1000:
                return 'CONSOLIDATION'
            elif variance > 5000:
                return 'VOLATILE'
            else:
                return 'TRENDING'
                
        except Exception as e:
            logger.error(f"Visual pattern identification error: {e}")
            return 'UNKNOWN'
    
    def _assess_chart_quality(self, gray_img: np.ndarray) -> str:
        """Assess the quality of the uploaded chart"""
        try:
            # Check image clarity and size
            height, width = gray_img.shape
            
            if width < 400 or height < 300:
                return 'TOO_SMALL'
            
            # Check for blur (using Laplacian variance)
            laplacian_var = cv2.Laplacian(gray_img, cv2.CV_64F).var()
            
            if laplacian_var < 100:
                return 'BLURRY'
            elif laplacian_var > 500:
                return 'GOOD'
            else:
                return 'ACCEPTABLE'
                
        except Exception as e:
            logger.error(f"Chart quality assessment error: {e}")
            return 'UNKNOWN'
    
    def _get_real_price_prediction(self, symbol: str) -> Dict[str, Any]:
        """Get prediction using real price data from API"""
        try:
            # Get real price data
            multi_tf_data = self.data_manager.get_multi_timeframe_data(symbol, ['1h', '4h'], 100)
            
            if not multi_tf_data or '1h' not in multi_tf_data:
                return {
                    'error': 'No real price data available',
                    'direction': 'UNKNOWN',
                    'confidence': 0,
                    'current_price': 0
                }
            
            # Perform technical analysis on real data
            analysis = self.technical_analyzer.analyze(
                df_1h=multi_tf_data['1h'], 
                df_4h=multi_tf_data.get('4h', None)
            )
            
            return {
                'direction': analysis.get('direction', 'UNKNOWN'),
                'confidence': analysis.get('confidence', 0),
                'current_price': analysis.get('current_price', 0),
                'meets_threshold': analysis.get('meets_threshold', False),
                'technical_analysis': analysis.get('advanced_analysis', {}),
                'data_source': 'REAL_API_DATA'
            }
            
        except Exception as e:
            logger.error(f"Real price prediction error: {e}")
            return {
                'error': str(e),
                'direction': 'UNKNOWN',
                'confidence': 0,
                'current_price': 0
            }
    
    def _generate_recommendation(self, visual_analysis: Dict, real_prediction: Dict) -> Dict[str, Any]:
        """Generate final recommendation combining visual and real data analysis"""
        try:
            visual_direction = visual_analysis.get('trend_direction', 'UNKNOWN')
            real_direction = real_prediction.get('direction', 'UNKNOWN')
            real_confidence = real_prediction.get('confidence', 0)
            
            # Prioritize real data prediction
            if real_prediction.get('meets_threshold', False):
                recommendation = {
                    'final_direction': real_direction,
                    'confidence': real_confidence,
                    'basis': 'REAL_PRICE_DATA',
                    'visual_confirmation': visual_direction == real_direction,
                    'recommendation_strength': 'HIGH' if real_confidence >= 80 else 'MEDIUM'
                }
            else:
                recommendation = {
                    'final_direction': 'WAIT',
                    'confidence': 50,
                    'basis': 'INSUFFICIENT_CONFIDENCE',
                    'visual_confirmation': False,
                    'recommendation_strength': 'LOW'
                }
            
            # Add visual pattern insights
            recommendation['visual_insights'] = {
                'chart_trend': visual_direction,
                'pattern_type': visual_analysis.get('pattern_type', 'UNKNOWN'),
                'chart_quality': visual_analysis.get('chart_quality', 'UNKNOWN')
            }
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Recommendation generation error: {e}")
            return {
                'final_direction': 'ERROR',
                'confidence': 0,
                'basis': 'ANALYSIS_ERROR',
                'error': str(e)
            }
    
    def _get_error_analysis(self, symbol: str, error_msg: str) -> Dict[str, Any]:
        """Return error analysis structure"""
        return {
            'symbol': symbol,
            'timeframe': 'unknown',
            'visual_analysis': {
                'error': error_msg,
                'confidence': 0
            },
            'real_price_prediction': {
                'error': 'Could not fetch real price data',
                'direction': 'UNKNOWN',
                'confidence': 0
            },
            'recommendation': {
                'final_direction': 'ERROR',
                'confidence': 0,
                'basis': 'SYSTEM_ERROR'
            },
            'success': False,
            'error': error_msg
        }