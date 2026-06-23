from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.decorators import admin_required
from .models import TelemedicineSession
from .forms import TelemedicineSessionForm

@admin_required
def session_list(request):
    sessions = TelemedicineSession.objects.all().order_by('-appointment_date')
    status = request.GET.get('status')
    if status:
        sessions = sessions.filter(status=status)
    return render(request, 'telemedicine/session_list.html', {'sessions': sessions, 'status': status})

@admin_required
def session_detail(request, pk):
    session = get_object_or_404(TelemedicineSession, pk=pk)
    return render(request, 'telemedicine/session_detail.html', {'session': session})

@admin_required
def session_create(request):
    if request.method == 'POST':
        form = TelemedicineSessionForm(request.POST)
        if form.is_valid():
            s = form.save(commit=False)
            s.created_by = request.user
            s.save()
            messages.success(request, 'Telemedicine session created.')
            return redirect('telemedicine:session_list')
    else:
        form = TelemedicineSessionForm()
    return render(request, 'telemedicine/session_form.html', {'form': form, 'title': 'Start Telemedicine Session'})

@admin_required
def session_update(request, pk):
    session = get_object_or_404(TelemedicineSession, pk=pk)
    if request.method == 'POST':
        form = TelemedicineSessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, 'Session updated.')
            return redirect('telemedicine:session_detail', pk=session.pk)
    else:
        form = TelemedicineSessionForm(instance=session)
    return render(request, 'telemedicine/session_form.html', {'form': form, 'title': 'Update Session'})
