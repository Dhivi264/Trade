from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import TradingPair, PriceData, Prediction, AccuracyMetrics, ChartUpload
from .data_sources import DataSourceManager
from .technical_analysis import AdvancedTechnicalAnalyzer, TechnicalAnalyzer
from .chart_analyzer import ChartVisualAnalyzer
from django.utils import timezone
from decimal import Decimal
import json
import logging
import pandas as pd
import os

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


@api_view(['POST'])
def get_precise_entry_signal(request):
    """
    🎯 GET PRECISE ENTRY SIGNAL
    Returns exact entry timing with UP/DOWN direction and duration (1/5/10 minutes)
    """
    try:
        symbol = request.data.get('symbol')
        
        if not symbol:
            return Response({'error': 'Symbol is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch multi-timeframe data
        data_manager = DataSourceManager()
        multi_tf_data = data_manager.get_multi_timeframe_data(symbol, ['1h', '4h'], 100)
        
        if not multi_tf_data or '1h' not in multi_tf_data:
            return Response({'error': 'No price data available'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Get precise entry signal
        analyzer = AdvancedTechnicalAnalyzer()
        entry_signal = analyzer.get_precise_entry_signal(
            df_1h=multi_tf_data['1h'], 
            df_4h=multi_tf_data.get('4h', None)
        )
        
        # Clean data for JSON response
        def clean_for_json(obj):
            import numpy as np
            import math
            
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif pd.isna(obj) or (isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj))):
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
                return str(obj)
        
        cleaned_signal = clean_for_json(entry_signal)
        
        return Response({
            'symbol': symbol,
            'timestamp': timezone.now().isoformat(),
            'entry_signal': cleaned_signal,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error getting precise entry signal: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return Response({'error': f'Failed to get entry signal: {str(e)}'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_qxbroker_quote(request):
    """
    📊 GET QXBROKER LIVE QUOTE
    Returns real-time price data similar to QXBroker demo platform
    """
    try:
        symbol = request.GET.get('symbol')
        force_refresh = request.GET.get('refresh', 'false').lower() == 'true'
        
        if not symbol:
            return Response({'error': 'Symbol is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Get live quote from QXBroker source
        data_manager = DataSourceManager()
        qx_source = data_manager.qxbroker
        
        # Force refresh cache if requested
        if force_refresh and symbol in qx_source.price_cache:
            del qx_source.price_cache[symbol]
            del qx_source.last_update[symbol]
            logger.info(f"Forced refresh for {symbol}")
        
        quote = qx_source.get_live_quote(symbol)
        
        if quote is None:
            return Response({'error': 'No quote data available'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Format response similar to QXBroker
        return Response({
            'symbol': quote['symbol'],
            'current_price': round(quote['current_price'], 5),
            'change': round(quote['change'], 5),
            'change_percent': round(quote['change_percent'], 3),
            'bid': round(quote['bid'], 5),
            'ask': round(quote['ask'], 5),
            'high_24h': round(quote['high_24h'], 5),
            'low_24h': round(quote['low_24h'], 5),
            'timestamp': quote['timestamp'].isoformat(),
            'data_source': quote.get('data_source', 'UNKNOWN'),
            'status': 'live',
            'refresh_forced': force_refresh
        })
        
    except Exception as e:
        logger.error(f"Error getting QXBroker quote: {e}")
        return Response({'error': f'Failed to get quote: {str(e)}'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@api_view(['GET'])
def get_chart_analyses(request):
    """
    📋 GET CHART ANALYSIS HISTORY
    Retrieve list of uploaded charts and their combined analysis results
    """
    try:
        limit = int(request.GET.get('limit', 10))
        symbol = request.GET.get('symbol')
        
        uploads_query = ChartUpload.objects.all()
        
        if symbol:
            uploads_query = uploads_query.filter(symbol__icontains=symbol)
        
        uploads = uploads_query[:limit]
        
        data = []
        for upload in uploads:
            real_prediction = upload.real_price_prediction
            visual_analysis = upload.chart_analysis
            
            data.append({
                'id': upload.id,
                'symbol': upload.symbol,
                'timeframe': upload.timeframe,
                'uploaded_at': upload.uploaded_at.isoformat(),
                'analysis_completed': upload.analysis_completed,
                'chart_image_url': upload.chart_image.url if upload.chart_image else None,
                'real_prediction': {
                    'direction': real_prediction.get('direction', 'UNKNOWN'),
                    'confidence': real_prediction.get('confidence', 0),
                    'meets_threshold': real_prediction.get('meets_threshold', False),
                    'current_price': real_prediction.get('current_price', 0),
                    'data_source': 'REAL_API_DATA'
                },
                'visual_analysis': {
                    'trend_direction': visual_analysis.get('trend_direction', 'UNKNOWN'),
                    'pattern_type': visual_analysis.get('pattern_type', 'UNKNOWN'),
                    'chart_quality': visual_analysis.get('chart_quality', 'UNKNOWN')
                },
                'recommendation': real_prediction.get('direction', 'WAIT') if real_prediction.get('meets_threshold', False) else 'WAIT'
            })
        
        return Response(data)
        
    except Exception as e:
        logger.error(f"Error fetching chart analyses: {e}")
        return Response({'error': 'Failed to fetch chart analyses'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_chart_analysis_detail(request, chart_id):
    """
    🔍 GET DETAILED CHART ANALYSIS
    Get detailed analysis results for a specific uploaded chart
    """
    try:
        chart_upload = ChartUpload.objects.get(id=chart_id)
        
        return Response({
            'id': chart_upload.id,
            'symbol': chart_upload.symbol,
            'timeframe': chart_upload.timeframe,
            'uploaded_at': chart_upload.uploaded_at.isoformat(),
            'chart_image_url': chart_upload.chart_image.url if chart_upload.chart_image else None,
            'analysis_completed': chart_upload.analysis_completed,
            'visual_analysis': chart_upload.chart_analysis,
            'real_price_prediction': chart_upload.real_price_prediction,
            'market_structure': chart_upload.market_structure,
            'note': 'Predictions are based on real price data from APIs, not chart image analysis'
        })
        
    except ChartUpload.DoesNotExist:
        return Response({'error': 'Chart analysis not found'}, 
                       status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error fetching chart analysis detail: {e}")
        return Response({'error': 'Failed to fetch chart analysis detail'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_chart_analysis(request, chart_id):
    """
    🗑️ DELETE UPLOADED CHART ANALYSIS
    Delete an uploaded chart and its analysis
    """
    try:
        chart_upload = ChartUpload.objects.get(id=chart_id)
        chart_upload.delete()  # This will also delete the image file
        
        return Response({'success': True, 'message': 'Chart analysis deleted successfully'})
        
    except ChartUpload.DoesNotExist:
        return Response({'error': 'Chart analysis not found'}, 
                       status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error deleting chart analysis: {e}")
        return Response({'error': 'Failed to delete chart analysis'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@csrf_exempt
def upload_chart_analysis(request):
    """
    📊 UPLOAD CHART FOR VISUAL ANALYSIS + REAL PRICE PREDICTION
    Combines visual chart analysis with real price data for accurate predictions
    """
    try:
        if 'chart_image' not in request.FILES:
            return Response({'error': 'No chart image provided'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        chart_file = request.FILES['chart_image']
        symbol = request.data.get('symbol', 'UNKNOWN')
        timeframe = request.data.get('timeframe', '1h')
        
        # Validate file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        file_extension = os.path.splitext(chart_file.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            return Response({'error': 'Invalid file type. Please upload JPG, PNG, or BMP images.'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file size (max 10MB)
        if chart_file.size > 10 * 1024 * 1024:
            return Response({'error': 'File too large. Maximum size is 10MB.'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Create ChartUpload instance
        chart_upload = ChartUpload.objects.create(
            chart_image=chart_file,
            symbol=symbol.upper(),
            timeframe=timeframe
        )
        
        # Analyze chart with real price data
        analyzer = ChartVisualAnalyzer()
        analysis_result = analyzer.analyze_chart_with_real_data(
            chart_upload.chart_image.path, 
            symbol.upper(),
            timeframe
        )
        
        # Clean analysis results for JSON serialization
        def clean_for_json(obj):
            """Recursively clean data for JSON serialization"""
            import numpy as np
            import math
            
            if obj is None:
                return None
            elif isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [clean_for_json(item) for item in obj]
            elif hasattr(obj, 'isoformat'):  # datetime/timestamp objects
                return obj.isoformat()
            elif hasattr(obj, 'tolist'):  # numpy arrays/pandas Series
                try:
                    return clean_for_json(obj.tolist())
                except:
                    return str(obj)
            elif hasattr(obj, 'item') and hasattr(obj, 'size'):  # single numpy objects
                try:
                    return obj.item()
                except:
                    return float(obj) if hasattr(obj, '__float__') else str(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                if np.isnan(obj) or np.isinf(obj):
                    return None
                return float(obj)
            elif isinstance(obj, np.ndarray):
                try:
                    return clean_for_json(obj.tolist())
                except:
                    return str(obj)
            elif isinstance(obj, float):
                if math.isnan(obj) or math.isinf(obj):
                    return None
                return obj
            elif isinstance(obj, (int, str, bool)):
                return obj
            else:
                # Try to convert to basic types
                try:
                    if hasattr(obj, '__float__'):
                        val = float(obj)
                        return None if math.isnan(val) or math.isinf(val) else val
                    elif hasattr(obj, '__int__'):
                        return int(obj)
                    else:
                        return str(obj)
                except:
                    return str(obj)
        
        # Clean and update chart upload with analysis results
        try:
            chart_upload.chart_analysis = clean_for_json(analysis_result.get('visual_analysis', {}))
            chart_upload.market_structure = clean_for_json(analysis_result.get('visual_analysis', {}))
            chart_upload.real_price_prediction = clean_for_json(analysis_result.get('real_price_prediction', {}))
            chart_upload.analysis_completed = True
            chart_upload.save()
        except Exception as save_error:
            logger.warning(f"Error saving analysis results: {save_error}")
            # Fallback: save minimal data
            chart_upload.chart_analysis = {'error': 'Could not save full analysis', 'status': 'partial'}
            chart_upload.market_structure = {'error': 'Could not save market structure'}
            chart_upload.real_price_prediction = clean_for_json(analysis_result.get('real_price_prediction', {}))
            chart_upload.analysis_completed = True
            chart_upload.save()
        
        # Create prediction record ONLY if real price analysis meets threshold
        real_prediction = analysis_result.get('real_price_prediction', {})
        recommendation = analysis_result.get('recommendation', {})
        
        prediction_created = False
        if real_prediction.get('meets_threshold', False) and recommendation.get('final_direction') in ['UP', 'DOWN']:
            # Get or create trading pair
            trading_pair, created = TradingPair.objects.get_or_create(
                symbol=symbol.upper(),
                defaults={'name': symbol.upper(), 'is_active': True}
            )
            
            # Create prediction based on REAL PRICE DATA only
            prediction = Prediction.objects.create(
                trading_pair=trading_pair,
                direction=recommendation['final_direction'],
                confidence=Decimal(str(real_prediction['confidence'])),
                timeframe='5m',  # Always 5-minute predictions
                current_price=Decimal(str(real_prediction.get('current_price', 1.0))),
                technical_indicators={
                    'source': 'chart_upload_with_real_data',
                    'chart_id': chart_upload.id,
                    'real_price_analysis': real_prediction,
                    'visual_confirmation': recommendation.get('visual_confirmation', False)
                }
            )
            prediction_created = True
        
        # Clean the response data as well
        cleaned_analysis = clean_for_json(analysis_result)
        
        return Response({
            'success': True,
            'chart_id': chart_upload.id,
            'symbol': chart_upload.symbol,
            'timeframe': chart_upload.timeframe,
            'analysis': cleaned_analysis,
            'uploaded_at': chart_upload.uploaded_at.isoformat(),
            'prediction_created': prediction_created,
            'message': 'Chart analyzed with real price data for accurate predictions'
        })
        
    except Exception as e:
        logger.error(f"Chart upload analysis error: {e}")
        return Response({'error': f'Failed to analyze chart: {str(e)}'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@api_view(['DELETE'])
def delete_chart_analysis(request, chart_id):
    """
    🗑️ DELETE UPLOADED CHART ANALYSIS
    Delete an uploaded chart and its analysis
    """
    try:
        chart_upload = ChartUpload.objects.get(id=chart_id)
        chart_upload.delete()  # This will also delete the image file
        
        return Response({'success': True, 'message': 'Chart analysis deleted successfully'})
        
    except ChartUpload.DoesNotExist:
        return Response({'error': 'Chart analysis not found'}, 
                       status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error deleting chart analysis: {e}")
        return Response({'error': 'Failed to delete chart analysis'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

