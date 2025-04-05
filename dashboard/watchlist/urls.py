from django.urls import path
from . import views

app_name = 'watchlist'

urlpatterns = [
    path('', views.watchlist, name='list'),
    path('create/', views.create_watchlist, name='create'),
    path('<int:watchlist_id>/', views.watchlist_detail, name='detail'),
    path('<int:watchlist_id>/edit/', views.edit_watchlist, name='edit'),
    path('<int:watchlist_id>/delete/', views.delete_watchlist, name='delete'),
    path('api/create/', views.create_watchlist_api, name='create_api'),
    path('api/list/', views.get_watchlists, name='get_list'),
    path('<int:watchlist_id>/add-stock/', views.add_stock_to_watchlist, name='add_stock'),
    path('<int:watchlist_id>/remove-stock/', views.remove_stock_from_watchlist, name='remove_stock'),
]
