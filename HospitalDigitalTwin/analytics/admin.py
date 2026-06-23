from django.contrib import admin
from .models import DailyAdmission, MonthlyReport, DepartmentStat, BedUtilizationReport, MedicineConsumption

@admin.register(DailyAdmission)
class DailyAdmissionAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_admissions', 'total_discharges', 'emergency_cases', 'outpatient_visits']
    list_filter = ['date']
    date_hierarchy = 'date'

@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ['month', 'year', 'total_patients', 'total_admissions', 'bed_utilization_rate']
    list_filter = ['year']

@admin.register(DepartmentStat)
class DepartmentStatAdmin(admin.ModelAdmin):
    list_display = ['department_name', 'date', 'patient_count', 'appointment_count', 'bed_utilization']
    list_filter = ['date', 'department_name']

@admin.register(BedUtilizationReport)
class BedUtilizationReportAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_beds', 'occupied_beds', 'utilization_rate']
    list_filter = ['date']

@admin.register(MedicineConsumption)
class MedicineConsumptionAdmin(admin.ModelAdmin):
    list_display = ['medicine_name', 'month', 'year', 'quantity_consumed', 'total_cost']
    list_filter = ['year', 'month']
