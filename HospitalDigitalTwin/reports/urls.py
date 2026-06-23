from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('admission-pdf/', views.generate_admission_report, name='generate_admission_report'),
    path('inventory-pdf/', views.generate_inventory_report, name='generate_inventory_report'),
    path('prediction-pdf/', views.generate_prediction_report, name='generate_prediction_report'),
    path('disease-risk-pdf/', views.generate_disease_risk_report, name='generate_disease_risk_report'),
    path('admission-excel/', views.export_admissions_excel, name='export_admissions_excel'),
    path('inventory-excel/', views.export_inventory_excel, name='export_inventory_excel'),
    path('prediction-excel/', views.export_predictions_excel, name='export_predictions_excel'),
    path('disease-risk-excel/', views.export_disease_risk_excel, name='export_disease_risk_excel'),
]
