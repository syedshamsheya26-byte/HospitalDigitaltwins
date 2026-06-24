from django.contrib import admin
from .models import Ward, Bed

class BedInline(admin.TabularInline):
    model = Bed
    extra = 0

@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ['name', 'floor', 'description']
    inlines = [BedInline]

@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ['bed_number', 'ward', 'bed_type', 'status', 'patient', 'assigned_date']
    list_filter = ['status', 'bed_type', 'ward']
    search_fields = ['bed_number', 'patient__first_name']
