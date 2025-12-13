from django.contrib import admin
from .models import TradingPair, PriceData, Prediction, AccuracyMetrics


@admin.register(TradingPair)
class TradingPairAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['symbol', 'name']


@admin.register(PriceData)
class PriceDataAdmin(admin.ModelAdmin):
    list_display = ['trading_pair', 'timestamp', 'close_price', 'timeframe']
    list_filter = ['trading_pair', 'timeframe', 'timestamp']
    search_fields = ['trading_pair__symbol']
    ordering = ['-timestamp']


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['trading_pair', 'direction', 'confidence', 'timeframe', 
                   'is_correct', 'is_resolved', 'prediction_time']
    list_filter = ['direction', 'timeframe', 'is_correct', 'is_resolved', 
                  'trading_pair', 'prediction_time']
    search_fields = ['trading_pair__symbol']
    ordering = ['-prediction_time']


@admin.register(AccuracyMetrics)
class AccuracyMetricsAdmin(admin.ModelAdmin):
    list_display = ['trading_pair', 'timeframe', 'accuracy_percentage', 
                   'total_predictions', 'correct_predictions', 'last_updated']
    list_filter = ['timeframe', 'trading_pair', 'last_updated']
    search_fields = ['trading_pair__symbol']
    ordering = ['-accuracy_percentage']