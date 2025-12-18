from django.contrib import admin
from .models import TradingPair, PriceData, Prediction, AccuracyMetrics, ChartUpload


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


@admin.register(ChartUpload)
class ChartUploadAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'timeframe', 'uploaded_at', 'analysis_completed', 'get_real_prediction', 'get_visual_trend']
    list_filter = ['timeframe', 'analysis_completed', 'uploaded_at', 'symbol']
    readonly_fields = ['uploaded_at', 'chart_analysis', 'market_structure', 'real_price_prediction']
    search_fields = ['symbol']
    
    def get_real_prediction(self, obj):
        if obj.real_price_prediction:
            direction = obj.real_price_prediction.get('direction', 'N/A')
            confidence = obj.real_price_prediction.get('confidence', 0)
            return f"{direction} ({confidence:.1f}%)"
        return 'N/A'
    get_real_prediction.short_description = 'Real Price Prediction'
    
    def get_visual_trend(self, obj):
        if obj.chart_analysis:
            return obj.chart_analysis.get('trend_direction', 'N/A')
        return 'N/A'
    get_visual_trend.short_description = 'Visual Trend'
    
    fieldsets = (
        ('Chart Information', {
            'fields': ('chart_image', 'symbol', 'timeframe', 'uploaded_at')
        }),
        ('Analysis Status', {
            'fields': ('analysis_completed',)
        }),
        ('Real Price Analysis (Primary)', {
            'fields': ('real_price_prediction',),
            'description': 'Predictions based on real API price data - THIS IS THE PRIMARY SOURCE'
        }),
        ('Visual Analysis (Context Only)', {
            'fields': ('chart_analysis', 'market_structure'),
            'classes': ('collapse',),
            'description': 'Visual patterns from chart image - FOR CONTEXT ONLY, NOT USED FOR PREDICTIONS'
        }),
    )