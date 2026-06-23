from django.contrib import admin
from .models import DiseaseRiskPrediction


@admin.register(DiseaseRiskPrediction)
class DiseaseRiskPredictionAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'disease_type', 'risk_level', 'risk_score', 'confidence_score', 'created_at']
    list_filter = ['disease_type', 'risk_level']
    search_fields = ['patient_name', 'disease_type']
