from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('premium/', views.dashboard_new, name='dashboard_new'),
    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/profile/', views.patient_profile, name='patient_profile'),
    path('patient/appointments/', views.patient_appointments, name='patient_appointments'),
    path('patient/medical-history/', views.patient_medical_history, name='patient_medical_history'),
    path('patient/disease-risk/', views.patient_disease_risk, name='patient_disease_risk_results'),
    path('patient/reports/', views.patient_reports, name='patient_reports'),
    path('patient/health-analytics/', views.patient_health_analytics, name='patient_health_analytics'),
    path('patient/chat-respond/', views.patient_chat_respond, name='patient_chat_respond'),
]
