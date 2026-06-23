from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='analytics_dashboard'),
    path('daily-admissions/', views.daily_admissions, name='daily_admissions'),
    path('monthly-admissions/', views.monthly_admissions, name='monthly_admissions'),
    path('departments/', views.department_analytics, name='department_analytics'),
    path('bed-utilization/', views.bed_utilization_view, name='bed_utilization'),
    path('medicine-consumption/', views.medicine_consumption_view, name='medicine_consumption'),
]
