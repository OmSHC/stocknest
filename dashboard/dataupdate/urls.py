from django.urls import path
from . import views

app_name = 'dataupdate'

urlpatterns = [
    path('', views.dataupdate, name='dataupdate'),
    path('allstocks/', views.all_stocks, name='all_stocks'),
    path('refresh-stock-data/', views.refresh_stock_data, name='refresh_stock_data'),
    path('update-all-stocks/', views.update_all_stocks, name='update_all_stocks'),
    path('fetch-yahoo-data/', views.fetch_yahoo_data, name='fetch_yahoo_data'),
]
