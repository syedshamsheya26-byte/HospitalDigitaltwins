from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from accounts.decorators import admin_required
from accounts.models import PatientSessionLog
from .models import Patient, MedicalHistory, FoodHistory
from .forms import PatientForm, MedicalHistoryForm, FoodHistoryForm


@admin_required
def patient_list(request):
    patients = Patient.objects.all()
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    if query:
        patients = patients.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(patient_id__icontains=query)
        )
    if status_filter:
        patients = patients.filter(status=status_filter)

    context = {
        'patients': patients,
        'query': query,
    }
    return render(request, 'patients/patient_list.html', context)


@admin_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    medical_history = MedicalHistory.objects.filter(patient=patient)
    food_history = FoodHistory.objects.filter(patient=patient)
    history_form = MedicalHistoryForm()
    food_form = FoodHistoryForm()
    context = {
        'patient': patient,
        'medical_history': medical_history,
        'food_history': food_history,
        'history_form': history_form,
        'food_form': food_form,
    }
    return render(request, 'patients/patient_detail.html', context)


@admin_required
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient created successfully.')
            return redirect('patients:patient_list')
    else:
        form = PatientForm()
    return render(request, 'patients/patient_form.html', {'form': form})


@admin_required
def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient updated successfully.')
            return redirect('patients:patient_detail', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)
    return render(request, 'patients/patient_form.html', {'form': form})


@admin_required
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, 'Patient deleted successfully.')
        return redirect('patients:patient_list')
    return render(request, 'patients/patient_confirm_delete.html', {'patient': patient})


@admin_required
def add_medical_history(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = MedicalHistoryForm(request.POST)
        if form.is_valid():
            history = form.save(commit=False)
            history.patient = patient
            history.created_by = request.user
            history.save()
            messages.success(request, 'Medical history added successfully.')
            return redirect('patients:patient_detail', pk=patient.pk)
    return redirect('patients:patient_detail', pk=patient.pk)

@admin_required
def patient_session_list(request):
    sessions = PatientSessionLog.objects.all().order_by('-session_start')
    return render(request, 'patients/patient_session_list.html', {'sessions': sessions})

@admin_required
def add_food_history(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = FoodHistoryForm(request.POST)
        if form.is_valid():
            food = form.save(commit=False)
            food.patient = patient
            food.recorded_by = request.user
            food.save()
            messages.success(request, 'Food history added successfully.')
            return redirect('patients:patient_detail', pk=patient.pk)
    return redirect('patients:patient_detail', pk=patient.pk)
