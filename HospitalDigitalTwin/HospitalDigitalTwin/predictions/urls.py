from django.urls import path
from . import views

app_name = 'predictions'

urlpatterns = [
    path('', views.prediction_dashboard, name='prediction_dashboard'),
    path('bed-occupancy/', views.predict_bed_occupancy, name='predict_bed_occupancy'),
    path('medicine-shortage/', views.predict_medicine_shortage, name='predict_medicine_shortage'),
    path('patient-load/', views.predict_patient_load, name='predict_patient_load'),
    path('risk-prediction/', views.risk_prediction, name='risk_prediction'),
    path('risk-prediction/<int:pk>/', views.risk_prediction_detail, name='risk_prediction_detail'),
    path('risk-predictions/', views.risk_prediction_list, name='risk_prediction_list'),
    path('model-performance/', views.model_performance, name='model_performance'),
]
