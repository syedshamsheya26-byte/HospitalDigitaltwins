from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from datetime import date

from accounts.decorators import admin_required
from .models import Medicine, MedicineCategory, Inventory, StockAlert
from .forms import MedicineForm, MedicineCategoryForm, InventoryForm


@admin_required
def medicine_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    medicines = Medicine.objects.select_related('category').all()

    if query:
        medicines = medicines.filter(
            Q(name__icontains=query) | Q(generic_name__icontains=query)
        )
    if category_id:
        medicines = medicines.filter(category_id=category_id)

    categories = MedicineCategory.objects.all()
    context = {
        'medicines': medicines,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
    }
    return render(request, 'inventory/medicine_list.html', context)


@admin_required
def medicine_detail(request, pk):
    medicine = get_object_or_404(
        Medicine.objects.select_related('category'), pk=pk
    )
    inventory_batches = medicine.inventory_items.select_related('created_by').all()
    context = {
        'medicine': medicine,
        'inventory_batches': inventory_batches,
    }
    return render(request, 'inventory/medicine_detail.html', context)


@admin_required
def medicine_create(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine created successfully.')
            return redirect('inventory:medicine_list')
    else:
        form = MedicineForm()
    return render(request, 'inventory/medicine_form.html', {'form': form})


@admin_required
def medicine_update(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine updated successfully.')
            return redirect('inventory:medicine_list')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'inventory/medicine_form.html', {'form': form})


@admin_required
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        medicine.delete()
        messages.success(request, 'Medicine deleted successfully.')
        return redirect('inventory:medicine_list')
    return render(request, 'inventory/medicine_confirm_delete.html', {'object': medicine})


@admin_required
def inventory_list(request):
    low_stock = request.GET.get('low_stock', '')
    items = Inventory.objects.select_related('medicine', 'created_by').all()

    if low_stock:
        items = items.filter(quantity__lte=10)

    alerts = StockAlert.objects.filter(status='active').select_related(
        'inventory_item__medicine'
    )[:5]

    context = {
        'items': items,
        'alerts': alerts,
        'filter_low_stock': low_stock,
    }
    return render(request, 'inventory/inventory_list.html', context)


@admin_required
def inventory_create(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()
            messages.success(request, 'Inventory item created successfully.')
            return redirect('inventory:inventory_list')
    else:
        form = InventoryForm()
    return render(request, 'inventory/inventory_form.html', {'form': form})


@admin_required
def inventory_update(request, pk):
    item = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inventory item updated successfully.')
            return redirect('inventory:inventory_list')
    else:
        form = InventoryForm(instance=item)
    return render(request, 'inventory/inventory_form.html', {'form': form})


@admin_required
def inventory_delete(request, pk):
    item = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Inventory item deleted successfully.')
        return redirect('inventory:inventory_list')
    return render(request, 'inventory/inventory_confirm_delete.html', {'object': item})


@admin_required
def low_stock_alerts(request):
    alerts = StockAlert.objects.select_related(
        'inventory_item__medicine'
    ).order_by('-created_at')
    context = {'alerts': alerts}
    return render(request, 'inventory/low_stock_alerts.html', context)


@admin_required
def inventory_dashboard(request):
    today = date.today()
    total_medicines = Medicine.objects.filter(is_active=True).count()
    low_stock_count = Inventory.objects.filter(quantity__lte=10).count()
    expired_count = Inventory.objects.filter(expiry_date__lt=today).count()
    all_items = Inventory.objects.values_list('quantity', 'selling_price')
    total_value = sum(qty * price for qty, price in all_items)

    context = {
        'total_medicines': total_medicines,
        'low_stock_count': low_stock_count,
        'expired_count': expired_count,
        'total_value': total_value,
    }
    return render(request, 'inventory/inventory_dashboard.html', context)
