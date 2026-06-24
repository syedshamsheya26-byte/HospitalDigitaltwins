from django.contrib import admin
from .models import Patient, MedicalHistory, FoodHistory

class MedicalHistoryInline(admin.TabularInline):
    model = MedicalHistory
    extra = 0

class FoodHistoryInline(admin.TabularInline):
    model = FoodHistory
    extra = 0

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'first_name', 'last_name', 'gender', 'blood_group', 'status', 'admission_date']
    list_filter = ['status', 'gender', 'blood_group']
    search_fields = ['patient_id', 'first_name', 'last_name', 'phone']
    inlines = [MedicalHistoryInline, FoodHistoryInline]
    date_hierarchy = 'created_at'

@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'record_date', 'created_by']
    list_filter = ['record_date']
    search_fields = ['patient__patient_id', 'patient__first_name']

@admin.register(FoodHistory)
class FoodHistoryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'food_item', 'meal_type', 'consumed_at', 'recorded_by']
    list_filter = ['meal_type', 'consumed_at']
    search_fields = ['patient__patient_id', 'food_item']
