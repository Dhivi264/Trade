from django.db import models
from django.utils import timezone
import os


class ChartUpload(models.Model):
    """Model for storing uploaded chart images and their analysis"""
    TIMEFRAME_CHOICES = [
        ('15m', '15 Minutes'),
        ('1h', '1 Hour'),
    ]
    
    chart_image = models.ImageField(upload_to='charts/', help_text="Upload 15-minute or 1-hour chart image")
    symbol = models.CharField(max_length=20, help_text="Trading pair symbol (e.g., EURUSD)")
    timeframe = models.CharField(max_length=3, choices=TIMEFRAME_CHOICES, default='1h')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    analysis_completed = models.BooleanField(default=False)
    
    # Chart Analysis Results (visual analysis only)
    chart_analysis = models.JSONField(default=dict, blank=True, help_text="Visual chart pattern analysis")
    market_structure = models.JSONField(default=dict, blank=True, help_text="Market structure from chart")
    
    # Real Price Prediction (using API data)
    real_price_prediction = models.JSONField(default=dict, blank=True, help_text="Prediction using real price data")
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.symbol} - {self.timeframe} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    def delete(self, *args, **kwargs):
        # Delete the image file when the model instance is deleted
        if self.chart_image:
            if os.path.isfile(self.chart_image.path):
                os.remove(self.chart_image.path)
        super().delete(*args, **kwargs)


class TradingPair(models.Model):
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol} - {self.name}"


class PriceData(models.Model):
    trading_pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    open_price = models.DecimalField(max_digits=20, decimal_places=8)
    high_price = models.DecimalField(max_digits=20, decimal_places=8)
    low_price = models.DecimalField(max_digits=20, decimal_places=8)
    close_price = models.DecimalField(max_digits=20, decimal_places=8)
    volume = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    timeframe = models.CharField(max_length=10, default='1h')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['trading_pair', 'timestamp', 'timeframe']
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.trading_pair.symbol} - {self.timestamp} - {self.close_price}"


class Prediction(models.Model):
    DIRECTION_CHOICES = [
        ('UP', 'Up'),
        ('DOWN', 'Down'),
    ]
    
    TIMEFRAME_CHOICES = [
        ('5m', '5 Minutes'),  # Primary prediction timeframe
        ('1m', '1 Minute'),   # Legacy support
    ]

    trading_pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE)
    prediction_time = models.DateTimeField(default=timezone.now)
    direction = models.CharField(max_length=4, choices=DIRECTION_CHOICES)
    confidence = models.DecimalField(max_digits=5, decimal_places=2)
    timeframe = models.CharField(max_length=2, choices=TIMEFRAME_CHOICES)
    current_price = models.DecimalField(max_digits=20, decimal_places=8)
    target_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    actual_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    technical_indicators = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-prediction_time']

    def __str__(self):
        return f"{self.trading_pair.symbol} - {self.direction} - {self.confidence}%"


class AccuracyMetrics(models.Model):
    trading_pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE)
    timeframe = models.CharField(max_length=2, choices=Prediction.TIMEFRAME_CHOICES)
    total_predictions = models.IntegerField(default=0)
    correct_predictions = models.IntegerField(default=0)
    accuracy_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['trading_pair', 'timeframe']

    def __str__(self):
        return f"{self.trading_pair.symbol} - {self.timeframe} - {self.accuracy_percentage}%"