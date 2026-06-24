from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['report_id', 'title', 'report_type', 'generated_by', 'format', 'created_at']
    list_filter = ['report_type', 'format', 'created_at']
    search_fields = ['title', 'report_id']
