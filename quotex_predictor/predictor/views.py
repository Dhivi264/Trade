from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TradingPair, PriceData, Prediction, AccuracyMetrics
from .data_sources import DataSourceManager
from .technical_analysis import AdvancedTechnicalAnalyzer, TechnicalAnalyzer
from django.utils import timezone
from decimal import Decimal
import json
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def index(request):
    """Main dashboard view"""
    return render(request, 'predictor/index.html')


@api_view(['GET'])
def get_trading_pairs(request):
    """Get all active trading pairs"""
    try:
        pairs = TradingPair.objects.filter(is_active=True)
        data = [{'symbol': pair.symbol, 'name': pair.name} for pair in pairs]
        return Response(data)
    except Exception as e:
        logger.error(f"Error fetching trading pairs: {e}")
        return Response({'error': 'Failed to fetch trading pairs'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def get_prediction(request):
    """Generate prediction for a trading pair"""
    try:
        symbol = request.data.get('symbol')
        timeframe = request.data.get('timeframe', '1m')
        
        if not symbol:
            return Response({'error': 'Symbol is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create trading pair
        trading_pair, created = TradingPair.objects.get_or_create(
            symbol=symbol,
            defaults={'name': symbol, 'is_active': True}
        )
        
        # Fetch multi-timeframe price data for advanced analysis
        data_manager = DataSourceManager()
        
        # Get both 1H and 4H data for professional analysis
        multi_tf_data = data_manager.get_multi_timeframe_data(symbol, ['1h', '4h'], 100)
        
        if not multi_tf_data or '1h' not in multi_tf_data:
            return Response({'error': 'No price data available'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Perform advanced technical analysis
        analyzer = AdvancedTechnicalAnalyzer()
        analysis = analyzer.analyze(
            df_1h=multi_tf_data['1h'], 
            df_4h=multi_tf_data.get('4h', None)
        )
        
        # Clean advanced analysis data for JSON serialization
        def clean_for_json(obj):
            """Recursively clean data for JSON serialization"""
            import numpy as np
            import math
            
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif hasattr(obj, 'isoformat'):  # datetime/timestamp objects
                return obj.isoformat()
            elif hasattr(obj, 'tolist'):  # pandas Series/arrays
                return clean_for_json(obj.tolist())
            elif hasattr(obj, 'item') and hasattr(obj, 'size') and obj.size == 1:  # single numpy objects
                return obj.item()
            elif pd.isna(obj) or (isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj))):  # pandas NaN or inf
                return None
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                if np.isnan(obj) or np.isinf(obj):
                    return None
                return float(obj)
            elif isinstance(obj, (int, float, str, bool)) or obj is None:
                return obj
            else:
                return str(obj)  # Convert anything else to string
        
        # Check if prediction meets professional trading standards (70%+ confidence)
        if not analysis.get('meets_threshold', False):
            return Response({
                'symbol': symbol,
                'timeframe': '5m',  # Always 5-minute predictions now
                'prediction': None,
                'message': f'No high-confidence prediction available (confidence: {analysis.get("confidence", 0):.1f}%). Professional trading requires 70%+ confidence.',
                'threshold_met': False,
                'current_price': analysis.get('current_price', 0),
                'analysis_timeframes': analysis.get('analysis_timeframes', ['1h', '4h']),
                'timestamp': timezone.now().isoformat()
            })
        
        # Clean advanced analysis data for database storage
        cleaned_indicators = clean_for_json(analysis.get('advanced_analysis', {}))
        
        # Save prediction to database with error handling
        try:
            prediction = Prediction.objects.create(
                trading_pair=trading_pair,
                direction=analysis['direction'],
                confidence=Decimal(str(analysis['confidence'])),
                timeframe='5m',  # Always 5-minute predictions
                current_price=Decimal(str(analysis['current_price'])),
                technical_indicators=cleaned_indicators
            )
        except Exception as db_error:
            logger.warning(f"Database save error for {symbol}, saving with minimal indicators: {db_error}")
            # Fallback: save with minimal indicators
            prediction = Prediction.objects.create(
                trading_pair=trading_pair,
                direction=analysis['direction'],
                confidence=Decimal(str(analysis['confidence'])),
                timeframe='5m',
                current_price=Decimal(str(analysis['current_price'])),
                technical_indicators={'error': 'Complex indicators could not be saved', 'direction': analysis['direction']}
            )
        
        return Response({
            'symbol': symbol,
            'timeframe': '5m',
            'prediction': {
                'direction': analysis['direction'],
                'confidence': float(analysis['confidence']),
                'current_price': float(analysis['current_price']),
                'prediction_timeframe': analysis.get('prediction_timeframe', '5m'),
                'analysis_timeframes': analysis.get('analysis_timeframes', ['1h', '4h']),
                'signal_breakdown': clean_for_json(analysis['signal_breakdown']),
                'advanced_analysis': clean_for_json(analysis.get('advanced_analysis', {})),
                'confluence_factors': clean_for_json(analysis.get('confluence_factors', {}))
            },
            'threshold_met': True,
            'timestamp': timezone.now().isoformat(),
            'prediction_id': prediction.id
        })
        
    except Exception as e:
        logger.error(f"Error generating prediction: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return Response({'error': f'Failed to generate prediction: {str(e)}'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_accuracy_metrics(request):
    """Get accuracy metrics for all trading pairs"""
    try:
        symbol = request.GET.get('symbol')
        timeframe = request.GET.get('timeframe')
        
        metrics_query = AccuracyMetrics.objects.all()
        
        if symbol:
            metrics_query = metrics_query.filter(trading_pair__symbol=symbol)
        if timeframe:
            metrics_query = metrics_query.filter(timeframe=timeframe)
        
        metrics = []
        for metric in metrics_query:
            metrics.append({
                'symbol': metric.trading_pair.symbol,
                'timeframe': metric.timeframe,
                'total_predictions': metric.total_predictions,
                'correct_predictions': metric.correct_predictions,
                'accuracy_percentage': float(metric.accuracy_percentage),
                'last_updated': metric.last_updated.isoformat()
            })
        
        return Response(metrics)
        
    except Exception as e:
        logger.error(f"Error fetching accuracy metrics: {e}")
        return Response({'error': 'Failed to fetch accuracy metrics'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_recent_predictions(request):
    """Get recent predictions with their outcomes"""
    try:
        symbol = request.GET.get('symbol')
        limit = int(request.GET.get('limit', 20))
        
        predictions_query = Prediction.objects.all()
        
        if symbol:
            predictions_query = predictions_query.filter(trading_pair__symbol=symbol)
        
        predictions = predictions_query[:limit]
        
        data = []
        for pred in predictions:
            data.append({
                'id': pred.id,
                'symbol': pred.trading_pair.symbol,
                'direction': pred.direction,
                'confidence': float(pred.confidence),
                'timeframe': pred.timeframe,
                'current_price': float(pred.current_price),
                'actual_price': float(pred.actual_price) if pred.actual_price else None,
                'is_correct': pred.is_correct,
                'is_resolved': pred.is_resolved,
                'prediction_time': pred.prediction_time.isoformat(),
                'created_at': pred.created_at.isoformat()
            })
        
        return Response(data)
        
    except Exception as e:
        logger.error(f"Error fetching recent predictions: {e}")
        return Response({'error': 'Failed to fetch recent predictions'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@csrf_exempt
def add_manual_price(request):
    """Add manual price data for testing"""
    try:
        symbol = request.data.get('symbol')
        price = request.data.get('price')
        
        if not symbol or not price:
            return Response({'error': 'Symbol and price are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create trading pair
        trading_pair, created = TradingPair.objects.get_or_create(
            symbol=symbol,
            defaults={'name': symbol, 'is_active': True}
        )
        
        # Create price data entry
        price_decimal = Decimal(str(price))
        PriceData.objects.create(
            trading_pair=trading_pair,
            timestamp=timezone.now(),
            open_price=price_decimal,
            high_price=price_decimal * Decimal('1.001'),
            low_price=price_decimal * Decimal('0.999'),
            close_price=price_decimal,
            volume=Decimal('1000'),
            timeframe='1h'
        )
        
        return Response({'message': 'Price data added successfully'})
        
    except Exception as e:
        logger.error(f"Error adding manual price: {e}")
        return Response({'error': 'Failed to add manual price'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_current_price(request):
    """Get current price for a symbol"""
    try:
        symbol = request.GET.get('symbol')
        
        if not symbol:
            return Response({'error': 'Symbol is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch current price data
        data_manager = DataSourceManager()
        price_data = data_manager.get_price_data(symbol, '1h', 1)
        
        if price_data is None or price_data.empty:
            return Response({'error': 'No price data available'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        current_price = float(price_data['close'].iloc[-1])
        timestamp = price_data.index[-1]
        
        return Response({
            'symbol': symbol,
            'price': current_price,
            'timestamp': timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp)
        })
        
    except Exception as e:
        logger.error(f"Error fetching current price: {e}")
        return Response({'error': 'Failed to fetch current price'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def resolve_predictions(request):
    """Manually resolve pending predictions"""
    try:
        from .tasks import simulate_realistic_outcomes
        
        resolved_count = simulate_realistic_outcomes()
        
        return Response({
            'message': f'Resolved {resolved_count} predictions',
            'resolved_count': resolved_count
        })
        
    except Exception as e:
        logger.error(f"Error resolving predictions: {e}")
        return Response({'error': 'Failed to resolve predictions'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def auto_resolve_predictions(request):
    """Auto-resolve predictions that have expired"""
    try:
        from .tasks import resolve_pending_predictions
        
        resolved_count = resolve_pending_predictions()
        
        return Response({
            'message': f'Auto-resolved {resolved_count} predictions',
            'resolved_count': resolved_count
        })
        
    except Exception as e:
        logger.error(f"Error auto-resolving predictions: {e}")
        return Response({'error': 'Failed to auto-resolve predictions'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)