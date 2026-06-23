import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from .forms import LoginForm
from .models import UserRole, LoginHistory, PatientSessionLog


def login_page(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'userrole') and request.user.userrole.role == 'admin':
            return redirect('dashboard:home')
    if 'patient_name' in request.session:
        return redirect('dashboard:patient_dashboard')
    return render(request, 'accounts/login.html', {
        'active_tab': request.GET.get('tab', 'admin')
    })


def admin_login_submit(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if hasattr(user, 'userrole') and user.userrole.role == 'admin':
                login(request, user)
                request.session['_fresh_login'] = True
                LoginHistory.objects.create(
                    user=user,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                )
                messages.success(request, 'Welcome back, Admin!')
                return redirect('dashboard:home')
            else:
                return render(request, 'accounts/login.html', {
                    'admin_error': 'Access denied. Only administrators can log in.',
                    'active_tab': 'admin',
                })
        return render(request, 'accounts/login.html', {
            'admin_error': 'Invalid username or password.',
            'active_tab': 'admin',
        })
    return redirect('accounts:login')


def patient_login_submit(request):
    if request.method == 'POST':
        name = request.POST.get('patient_name', '').strip()
        age = request.POST.get('age')
        gender = request.POST.get('gender', 'male')

        if not name:
            return render(request, 'accounts/login.html', {
                'patient_error': 'Please enter your name.',
                'active_tab': 'patient',
            })
        if not age or not age.isdigit():
            return render(request, 'accounts/login.html', {
                'patient_error': 'Please enter a valid age.',
                'active_tab': 'patient',
            })

        request.session['patient_name'] = name
        request.session['patient_age'] = int(age)
        request.session['patient_gender'] = gender
        request.session['patient_height'] = request.POST.get('height', '')
        request.session['patient_weight'] = request.POST.get('weight', '')
        request.session['patient_blood_type'] = request.POST.get('blood_type', '')
        request.session['patient_session_start'] = datetime.now().isoformat()
        request.session['patient_vitals'] = json.dumps([])
        request.session['patient_risk_assessments'] = json.dumps([])
        request.session['_fresh_login'] = True
        request.session.set_expiry(86400)

        msg = f'Welcome, {name}!'
        try:
            messages.success(request, msg)
        except Exception:
            pass
        return redirect('dashboard:patient_dashboard')

    return redirect('accounts:login')


def logout_view(request):
    if 'patient_name' in request.session:
        try:
            PatientSessionLog.objects.create(
                patient_name=request.session.get('patient_name', 'Unknown'),
                age=request.session.get('patient_age', 0),
                gender=request.session.get('patient_gender', 'male'),
                risk_assessments=request.session.get('patient_risk_assessments', '[]'),
                vitals_history=request.session.get('patient_vitals', '[]'),
            )
        except Exception:
            pass
        for key in ['patient_name', 'patient_age', 'patient_gender',
                     'patient_height', 'patient_weight', 'patient_blood_type',
                     'patient_session_start', 'patient_vitals',
                     'patient_risk_assessments']:
            request.session.pop(key, None)

    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def admin_dashboard_redirect(request):
    if hasattr(request.user, 'userrole') and request.user.userrole.role == 'admin':
        return redirect('dashboard:home')
    return redirect('accounts:login')
