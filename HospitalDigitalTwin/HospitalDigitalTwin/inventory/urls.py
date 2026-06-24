from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.medicine_list, name='medicine_list'),
    path('create/', views.medicine_create, name='medicine_create'),
    path('<int:pk>/', views.medicine_detail, name='medicine_detail'),
    path('<int:pk>/update/', views.medicine_update, name='medicine_update'),
    path('<int:pk>/delete/', views.medicine_delete, name='medicine_delete'),
    path('stock/', views.inventory_list, name='inventory_list'),
    path('stock/create/', views.inventory_create, name='inventory_create'),
    path('stock/<int:pk>/update/', views.inventory_update, name='inventory_update'),
    path('stock/<int:pk>/delete/', views.inventory_delete, name='inventory_delete'),
    path('alerts/', views.low_stock_alerts, name='low_stock_alerts'),
    path('dashboard/', views.inventory_dashboard, name='inventory_dashboard'),
]
