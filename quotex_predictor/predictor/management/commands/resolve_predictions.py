from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from predictor.models import Prediction, AccuracyMetrics
from predictor.data_sources import DataSourceManager
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Resolve pending predictions and update accuracy metrics'

    def handle(self, *args, **options):
        """Resolve predictions that have expired"""
        self.stdout.write("🔍 Resolving pending predictions...")
        
        # Get predictions that should be resolved
        now = timezone.now()
        
        # For 1-minute predictions, resolve after 1 minute
        # For 5-minute predictions, resolve after 5 minutes
        pending_predictions = Prediction.objects.filter(
            is_resolved=False
        )
        
        resolved_count = 0
        data_manager = DataSourceManager()
        
        for prediction in pending_predictions:
            try:
                # Calculate when this prediction should be resolved
                if prediction.timeframe == '1m':
                    resolve_time = prediction.prediction_time + timedelta(minutes=1)
                elif prediction.timeframe == '5m':
                    resolve_time = prediction.prediction_time + timedelta(minutes=5)
                else:
                    resolve_time = prediction.prediction_time + timedelta(minutes=1)
                
                # Check if enough time has passed
                if now >= resolve_time:
                    # Get current price to compare with prediction
                    current_data = data_manager.get_price_data(
                        prediction.trading_pair.symbol, 
                        '1h', 
                        1
                    )
                    
                    if current_data is not None and not current_data.empty:
                        actual_price = float(current_data['close'].iloc[-1])
                        original_price = float(prediction.current_price)
                        
                        # Determine if prediction was correct
                        price_change = actual_price - original_price
                        
                        if prediction.direction == 'UP':
                            is_correct = price_change > 0
                        else:  # DOWN
                            is_correct = price_change < 0
                        
                        # Update prediction
                        prediction.actual_price = actual_price
                        prediction.is_correct = is_correct
                        prediction.is_resolved = True
                        prediction.save()
                        
                        resolved_count += 1
                        
                        # Update accuracy metrics
                        self._update_accuracy_metrics(prediction)
                        
                        status = "✅ CORRECT" if is_correct else "❌ INCORRECT"
                        self.stdout.write(
                            f"   {prediction.trading_pair.symbol} {prediction.direction} "
                            f"({prediction.confidence}%) - {status}"
                        )
                    else:
                        # If we can't get price data, mark as resolved but unknown
                        prediction.is_resolved = True
                        prediction.save()
                        
                        self.stdout.write(
                            f"   {prediction.trading_pair.symbol} - No price data available"
                        )
                        
            except Exception as e:
                logger.error(f"Error resolving prediction {prediction.id}: {e}")
                continue
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Resolved {resolved_count} predictions')
        )
    
    def _update_accuracy_metrics(self, prediction):
        """Update accuracy metrics for the trading pair and timeframe"""
        try:
            metrics, created = AccuracyMetrics.objects.get_or_create(
                trading_pair=prediction.trading_pair,
                timeframe=prediction.timeframe,
                defaults={
                    'total_predictions': 0,
                    'correct_predictions': 0,
                    'accuracy_percentage': 0
                }
            )
            
            # Recalculate metrics from all resolved predictions
            resolved_predictions = Prediction.objects.filter(
                trading_pair=prediction.trading_pair,
                timeframe=prediction.timeframe,
                is_resolved=True
            )
            
            total = resolved_predictions.count()
            correct = resolved_predictions.filter(is_correct=True).count()
            accuracy = (correct / total * 100) if total > 0 else 0
            
            metrics.total_predictions = total
            metrics.correct_predictions = correct
            metrics.accuracy_percentage = accuracy
            metrics.save()
            
        except Exception as e:
            logger.error(f"Error updating accuracy metrics: {e}")