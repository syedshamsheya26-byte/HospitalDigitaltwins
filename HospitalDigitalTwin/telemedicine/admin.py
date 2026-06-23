from django.contrib import admin
from .models import TelemedicineSession

@admin.register(TelemedicineSession)
class TelemedicineSessionAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'doctor_name', 'appointment_date', 'status']
    list_filter = ['status', 'appointment_date']
    search_fields = ['patient_name', 'doctor_name']
