from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path('watchlist/create/', views.create_watchlist, name='create_watchlist'),
    path('watchlist/<int:watchlist_id>/', views.watchlist_detail, name='watchlist_detail'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('market-insights/', views.market_insights, name='market_insights'),
    path('risk-analysis/', views.risk_analysis, name='risk_analysis'),
    path('reports/', views.reports, name='reports'),
    
    # API endpoints
    path('api/update-chart-data/', views.update_chart_data, name='update_chart_data'),
    path('api/search-stocks/', views.search_stocks, name='search_stocks'),
    path('api/watchlists/', views.get_watchlists, name='get_watchlists'),
    path('api/watchlists/create/', views.create_watchlist_api, name='create_watchlist_api'),
    
    # Fyers API endpoints
    path('api/fyers/quotes/', views.get_stock_quotes, name='get_stock_quotes'),
    path('api/fyers/symbols/', views.get_all_symbols, name='get_all_symbols'),
    path('api/fyers/callback/', views.fyers_callback, name='fyers_callback'),
    
    # Live market data endpoints
    path('api/market/live/', views.get_live_quotes, name='get_live_quotes'),
    path('api/market/historical/', views.get_historical_quotes, name='get_historical_quotes'),
    path('api/market/summary/', views.get_market_summary, name='get_market_summary'),
] 