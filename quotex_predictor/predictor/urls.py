from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/trading-pairs/', views.get_trading_pairs, name='trading_pairs'),
    path('api/prediction/', views.get_prediction, name='get_prediction'),
    path('api/accuracy/', views.get_accuracy_metrics, name='accuracy_metrics'),
    path('api/recent-predictions/', views.get_recent_predictions, name='recent_predictions'),
    path('api/manual-price/', views.add_manual_price, name='add_manual_price'),
    path('api/current-price/', views.get_current_price, name='current_price'),
    path('api/resolve-predictions/', views.resolve_predictions, name='resolve_predictions'),
    path('api/auto-resolve/', views.auto_resolve_predictions, name='auto_resolve_predictions'),
    path('api/precise-entry/', views.get_precise_entry_signal, name='precise_entry_signal'),
    path('api/qxbroker-quote/', views.get_qxbroker_quote, name='qxbroker_quote'),
]