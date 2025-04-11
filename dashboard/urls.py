from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html', next_page='dashboard:dashboard'), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='dashboard:login'), name='logout'),
    path('watchlist/', include('dashboard.watchlist.urls', namespace='watchlist')),
    path('dataupdate/', include('dashboard.dataupdate.urls', namespace='dataupdate')),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('market-insights/', views.market_insights, name='market_insights'),
    path('risk-analysis/', views.risk_analysis, name='risk_analysis'),
    path('reports/', views.reports, name='reports'),
    
    # API endpoints
    path('api/update-chart-data/', views.update_chart_data, name='update_chart_data'),
    path('api/search-stocks/', views.search_stocks, name='search_stocks'),
    
    # Fyers API endpoints
    path('api/fyers/quotes/', views.get_stock_quotes, name='get_stock_quotes'),
    path('api/fyers/symbols/', views.get_all_symbols, name='get_all_symbols'),
    path('api/fyers/callback/', views.fyers_callback, name='fyers_callback'),
    
    # Live market data endpoints
    path('api/market/live/', views.get_live_quotes, name='get_live_quotes'),
    path('api/market/historical/', views.get_historical_quotes, name='get_historical_quotes'),
    path('api/market/summary/', views.get_market_summary, name='get_market_summary'),
] 