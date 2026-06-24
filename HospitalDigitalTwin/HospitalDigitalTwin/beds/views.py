from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone

from accounts.decorators import admin_required
from .models import Bed, Ward
from .forms import BedForm, WardForm
from patients.models import Patient


@admin_required
def bed_list(request):
    beds = Bed.objects.all()
    bed_type = request.GET.get('bed_type')
    status = request.GET.get('status')
    ward = request.GET.get('ward')

    if bed_type:
        beds = beds.filter(bed_type=bed_type)
    if status:
        beds = beds.filter(status=status)
    if ward:
        beds = beds.filter(ward_id=ward)

    total = beds.count()
    available = beds.filter(status='available').count()
    occupied = beds.filter(status='occupied').count()
    maintenance = beds.filter(status='maintenance').count()

    context = {
        'beds': beds,
        'total': total,
        'available': available,
        'occupied': occupied,
        'maintenance': maintenance,
    }
    return render(request, 'beds/bed_list.html', context)


@admin_required
def bed_detail(request, pk):
    bed = get_object_or_404(Bed, pk=pk)
    return render(request, 'beds/bed_detail.html', {'bed': bed})


@admin_required
def bed_create(request):
    form = BedForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Bed created successfully.')
        return redirect('beds:bed_list')
    return render(request, 'beds/bed_form.html', {'form': form})


@admin_required
def bed_update(request, pk):
    bed = get_object_or_404(Bed, pk=pk)
    form = BedForm(request.POST or None, instance=bed)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Bed updated successfully.')
        return redirect('beds:bed_detail', pk=bed.pk)
    return render(request, 'beds/bed_form.html', {'form': form})


@admin_required
def bed_delete(request, pk):
    bed = get_object_or_404(Bed, pk=pk)
    if request.method == 'POST':
        bed.delete()
        messages.success(request, 'Bed deleted successfully.')
        return redirect('beds:bed_list')
    return render(request, 'beds/bed_confirm_delete.html', {'bed': bed})


@admin_required
def assign_bed(request, pk):
    bed = get_object_or_404(Bed, pk=pk)
    patients = Patient.objects.all()
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        if patient_id:
            patient = get_object_or_404(Patient, pk=patient_id)
            bed.patient = patient
            bed.status = 'occupied'
            bed.assigned_date = timezone.now()
            bed.save()
            messages.success(request, f'Bed assigned to {patient}.')
            return redirect('beds:bed_detail', pk=bed.pk)
    return render(request, 'beds/assign_bed.html', {'bed': bed, 'patients': patients})


@admin_required
def discharge_bed(request, pk):
    bed = get_object_or_404(Bed, pk=pk)
    if request.method == 'POST':
        bed.patient = None
        bed.status = 'available'
        bed.discharge_date = timezone.now()
        bed.assigned_date = None
        bed.save()
        messages.success(request, 'Patient discharged from bed.')
        return redirect('beds:bed_list')
    return render(request, 'beds/bed_confirm_discharge.html', {'bed': bed})


@admin_required
def ward_list(request):
    wards = Ward.objects.annotate(
        total_beds=Count('beds'),
        available_beds=Count('beds', filter=Q(beds__status='available')),
        occupied_beds=Count('beds', filter=Q(beds__status='occupied')),
    )
    return render(request, 'beds/ward_list.html', {'wards': wards})


@admin_required
def ward_create(request):
    form = WardForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Ward created successfully.')
        return redirect('beds:ward_list')
    return render(request, 'beds/ward_form.html', {'form': form})


@admin_required
def occupancy_dashboard(request):
    stats = Bed.objects.values('bed_type').annotate(
        total=Count('pk'),
        available=Count('pk', filter=Q(status='available')),
        occupied=Count('pk', filter=Q(status='occupied')),
        maintenance=Count('pk', filter=Q(status='maintenance')),
        reserved=Count('pk', filter=Q(status='reserved')),
    ).order_by('bed_type')
    return render(request, 'beds/occupancy_dashboard.html', {'stats': stats})
