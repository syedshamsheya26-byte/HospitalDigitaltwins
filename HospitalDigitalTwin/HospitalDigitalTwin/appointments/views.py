import datetime
import secrets

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import admin_required
from .forms import AppointmentForm
from .models import Appointment


def _generate_appointment_id():
    today = datetime.date.today().strftime('%Y%m%d')
    rand = secrets.token_hex(2).upper()
    return f'APT-{today}-{rand}'


@admin_required
def appointment_list(request):
    appointments = Appointment.objects.all()
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if status:
        appointments = appointments.filter(status=status)
    if date_from:
        appointments = appointments.filter(appointment_date__gte=date_from)
    if date_to:
        appointments = appointments.filter(appointment_date__lte=date_to)

    context = {
        'appointments': appointments,
        'status': status,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'appointments/appointment_list.html', context)


@admin_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'appointments/appointment_detail.html', {'appointment': appointment})


@admin_required
def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        form.fields.pop('appointment_id', None)
        form.fields.pop('created_by', None)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.appointment_id = _generate_appointment_id()
            appointment.created_by = request.user
            appointment.save()
            messages.success(request, f'Appointment {appointment.appointment_id} created successfully.')
            return redirect('appointments:appointment_list')
    else:
        form = AppointmentForm()
        form.fields.pop('appointment_id', None)
        form.fields.pop('created_by', None)
    return render(request, 'appointments/appointment_form.html', {'form': form})


@admin_required
def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, f'Appointment {appointment.appointment_id} updated successfully.')
            return redirect('appointments:appointment_detail', pk=appointment.pk)
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'appointments/appointment_form.html', {'form': form})


@admin_required
def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment_id = appointment.appointment_id
    appointment.delete()
    messages.success(request, f'Appointment {appointment_id} deleted successfully.')
    return redirect('appointments:appointment_list')


@admin_required
def appointment_cancel(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'cancelled'
    appointment.save()
    messages.success(request, f'Appointment {appointment.appointment_id} has been cancelled.')
    return redirect('appointments:appointment_list')


@admin_required
def appointment_complete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'completed'
    appointment.save()
    messages.success(request, f'Appointment {appointment.appointment_id} marked as completed.')
    return redirect('appointments:appointment_list')


@admin_required
def my_appointments(request):
    appointments = Appointment.objects.filter(created_by=request.user)
    return render(request, 'appointments/my_appointments.html', {'appointments': appointments})
