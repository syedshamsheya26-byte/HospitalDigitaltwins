from django.contrib import admin
from .models import SurgeryRobot, RoboticProcedure

@admin.register(SurgeryRobot)
class SurgeryRobotAdmin(admin.ModelAdmin):
    list_display = ['name', 'robot_id', 'robot_type', 'status', 'location']
    list_filter = ['status', 'robot_type']

@admin.register(RoboticProcedure)
class RoboticProcedureAdmin(admin.ModelAdmin):
    list_display = ['procedure_id', 'patient_name', 'robot', 'procedure_type', 'scheduled_date', 'status']
    list_filter = ['status', 'scheduled_date']
