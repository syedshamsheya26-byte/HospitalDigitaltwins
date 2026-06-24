from django.contrib import admin
from .models import Prediction, RiskPrediction, PredictionModel

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['prediction_type', 'department_name', 'predicted_date', 'predicted_value', 'confidence_score']
    list_filter = ['prediction_type', 'predicted_date']
    search_fields = ['prediction_type']

@admin.register(RiskPrediction)
class RiskPredictionAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'risk_level', 'risk_score', 'predicted_condition', 'created_at']
    list_filter = ['risk_level', 'created_at']
    search_fields = ['patient_name', 'diagnosis']

@admin.register(PredictionModel)
class PredictionModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_type', 'accuracy', 'trained_on', 'is_active']
    list_filter = ['is_active', 'model_type']
