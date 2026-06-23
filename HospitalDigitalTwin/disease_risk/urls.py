from django.urls import path
from . import views

app_name = 'disease_risk'

urlpatterns = [
    path('', views.risk_assessment, name='risk_assessment'),
    path('history/', views.prediction_history, name='prediction_history'),
    path('detail/<int:pk>/', views.prediction_detail, name='prediction_detail'),
    path('analytics/', views.disease_analytics, name='disease_analytics'),
]
