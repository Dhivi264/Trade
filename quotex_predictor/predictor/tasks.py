from django.utils import timezone
from datetime import timedelta
from .models import Prediction, AccuracyMetrics
from .data_sources import DataSourceManager
import logging

logger = logging.getLogger(__name__)


def resolve_pending_predictions():
    """
    Resolve pending predictions that have expired
    This function can be called periodically to update prediction statuses
    """
    try:
        now = timezone.now()
        data_manager = DataSourceManager()
        resolved_count = 0
        
        # Get all pending predictions
        pending_predictions = Prediction.objects.filter(is_resolved=False)
        
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
                        update_accuracy_metrics(prediction)
                        
                        logger.info(
                            f"Resolved prediction {prediction.id}: "
                            f"{prediction.trading_pair.symbol} {prediction.direction} "
                            f"- {'CORRECT' if is_correct else 'INCORRECT'}"
                        )
                    else:
                        # If we can't get price data, mark as resolved but unknown
                        prediction.is_resolved = True
                        prediction.save()
                        logger.warning(f"No price data for prediction {prediction.id}")
                        
            except Exception as e:
                logger.error(f"Error resolving prediction {prediction.id}: {e}")
                continue
        
        logger.info(f"Resolved {resolved_count} predictions")
        return resolved_count
        
    except Exception as e:
        logger.error(f"Error in resolve_pending_predictions: {e}")
        return 0


def update_accuracy_metrics(prediction):
    """Update accuracy metrics for a trading pair and timeframe"""
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
        
        logger.info(
            f"Updated metrics for {prediction.trading_pair.symbol} "
            f"({prediction.timeframe}): {accuracy:.1f}% ({correct}/{total})"
        )
        
    except Exception as e:
        logger.error(f"Error updating accuracy metrics: {e}")


def simulate_realistic_outcomes():
    """
    Simulate realistic trading outcomes for demo purposes
    This creates more realistic win/loss patterns
    """
    try:
        pending_predictions = Prediction.objects.filter(is_resolved=False)
        resolved_count = 0
        
        for prediction in pending_predictions:
            try:
                now = timezone.now()
                
                # Calculate when this prediction should be resolved
                if prediction.timeframe == '1m':
                    resolve_time = prediction.prediction_time + timedelta(minutes=1)
                elif prediction.timeframe == '5m':
                    resolve_time = prediction.prediction_time + timedelta(minutes=5)
                else:
                    resolve_time = prediction.prediction_time + timedelta(minutes=1)
                
                # Check if enough time has passed
                if now >= resolve_time:
                    # Simulate realistic outcome based on confidence
                    confidence = float(prediction.confidence)
                    
                    # Higher confidence = higher chance of being correct
                    # 90% confidence = ~75% actual success rate (realistic)
                    # 80% confidence = ~65% actual success rate
                    # 75% confidence = ~60% actual success rate
                    
                    import random
                    success_probability = (confidence - 15) / 100  # Adjust for realism
                    is_correct = random.random() < success_probability
                    
                    # Simulate price movement
                    original_price = float(prediction.current_price)
                    
                    if is_correct:
                        # Price moved in predicted direction
                        if prediction.direction == 'UP':
                            price_change = random.uniform(0.0001, 0.002)  # Small upward movement
                        else:
                            price_change = random.uniform(-0.002, -0.0001)  # Small downward movement
                    else:
                        # Price moved opposite to prediction
                        if prediction.direction == 'UP':
                            price_change = random.uniform(-0.002, -0.0001)  # Moved down instead
                        else:
                            price_change = random.uniform(0.0001, 0.002)  # Moved up instead
                    
                    actual_price = original_price + (original_price * price_change)
                    
                    # Update prediction
                    prediction.actual_price = actual_price
                    prediction.is_correct = is_correct
                    prediction.is_resolved = True
                    prediction.save()
                    
                    resolved_count += 1
                    
                    # Update accuracy metrics
                    update_accuracy_metrics(prediction)
                    
                    logger.info(
                        f"Simulated outcome for prediction {prediction.id}: "
                        f"{prediction.trading_pair.symbol} {prediction.direction} "
                        f"({confidence}%) - {'CORRECT' if is_correct else 'INCORRECT'}"
                    )
                    
            except Exception as e:
                logger.error(f"Error simulating outcome for prediction {prediction.id}: {e}")
                continue
        
        logger.info(f"Simulated outcomes for {resolved_count} predictions")
        return resolved_count
        
    except Exception as e:
        logger.error(f"Error in simulate_realistic_outcomes: {e}")
        return 0