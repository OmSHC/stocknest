from django.urls import path
from . import views

app_name = 'technical'

urlpatterns = [
    path('', views.screener_list, name='screener_list'),
    path('create/', views.create_screener, name='create_screener'),
    path('<int:screener_id>/', views.screener_detail, name='screener_detail'),
    path('<int:screener_id>/run/', views.run_screener, name='run_screener'),
    path('<int:screener_id>/delete/', views.delete_screener, name='delete_screener'),
    path('<int:screener_id>/subscribe/', views.subscribe_screener, name='subscribe_screener'),
    path('<int:screener_id>/unsubscribe/', views.unsubscribe_screener, name='unsubscribe_screener'),
    
    # API endpoints
    path('api/create/', views.create_technical_screener_api, name='create_screener_api'),
    path('api/list/', views.get_technical_screeners, name='get_screeners'),
    path('api/<int:screener_id>/delete/', views.delete_technical_screener, name='delete_screener_api'),
    path('api/<int:screener_id>/edit/', views.edit_technical_screener, name='edit_screener_api'),
] 