from django.urls import path
from . import views

app_name = 'beds'

urlpatterns = [
    path('', views.bed_list, name='bed_list'),
    path('create/', views.bed_create, name='bed_create'),
    path('<int:pk>/', views.bed_detail, name='bed_detail'),
    path('<int:pk>/update/', views.bed_update, name='bed_update'),
    path('<int:pk>/delete/', views.bed_delete, name='bed_delete'),
    path('<int:pk>/assign/', views.assign_bed, name='assign_bed'),
    path('<int:pk>/discharge/', views.discharge_bed, name='discharge_bed'),
    path('wards/', views.ward_list, name='ward_list'),
    path('wards/create/', views.ward_create, name='ward_create'),
    path('occupancy/', views.occupancy_dashboard, name='occupancy_dashboard'),
]
