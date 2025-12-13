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
from .technical_analysis import TechnicalAnalyzer
from django.utils import timezone
from decimal import Decimal
import json
import logging

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
        
        # Fetch price data
        data_manager = DataSourceManager()
        price_data = data_manager.get_price_data(symbol, '1h', 100)
        
        if price_data is None or price_data.empty:
            return Response({'error': 'No price data available'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Perform technical analysis
        analyzer = TechnicalAnalyzer()
        analysis = analyzer.analyze(price_data)
        
        # Only return predictions that meet the 90% threshold
        if not analysis.get('meets_threshold', False):
            return Response({
                'symbol': symbol,
                'timeframe': timeframe,
                'prediction': None,
                'message': f'No high-confidence prediction available (confidence: {analysis.get("confidence", 0):.1f}%)',
                'threshold_met': False,
                'current_price': analysis.get('current_price', 0),
                'timestamp': timezone.now().isoformat()
            })
        
        # Save prediction to database
        prediction = Prediction.objects.create(
            trading_pair=trading_pair,
            direction=analysis['direction'],
            confidence=Decimal(str(analysis['confidence'])),
            timeframe=timeframe,
            current_price=Decimal(str(analysis['current_price'])),
            technical_indicators=analysis['indicators']
        )
        
        return Response({
            'symbol': symbol,
            'timeframe': timeframe,
            'prediction': {
                'direction': analysis['direction'],
                'confidence': analysis['confidence'],
                'current_price': analysis['current_price'],
                'indicators': analysis['indicators'],
                'signal_breakdown': analysis['signal_breakdown']
            },
            'threshold_met': True,
            'timestamp': timezone.now().isoformat(),
            'prediction_id': prediction.id
        })
        
    except Exception as e:
        logger.error(f"Error generating prediction: {e}")
        return Response({'error': 'Failed to generate prediction'}, 
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