from django.contrib import admin
from .models import MedicineCategory, Medicine, Inventory, StockAlert

@admin.register(MedicineCategory)
class MedicineCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['medicine_id', 'name', 'generic_name', 'dosage_form', 'manufacturer', 'unit_price']
    list_filter = ['dosage_form', 'is_active']
    search_fields = ['medicine_id', 'name', 'generic_name']

class StockAlertInline(admin.TabularInline):
    model = StockAlert
    extra = 0

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['medicine', 'batch_number', 'quantity', 'expiry_date', 'is_expired']
    list_filter = ['expiry_date']
    search_fields = ['medicine__name', 'batch_number']
    inlines = [StockAlertInline]

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['inventory_item', 'alert_type', 'message', 'status', 'created_at']
    list_filter = ['alert_type', 'status']
