from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Avg

from accounts.decorators import admin_required
from .models import DailyAdmission, MonthlyReport, DepartmentStat, BedUtilizationReport, MedicineConsumption


@admin_required
def analytics_dashboard(request):
    today = timezone.now().date()
    thirty_days_ago = today - timezone.timedelta(days=30)
    current_year = today.year

    daily_stats = DailyAdmission.objects.filter(date__gte=thirty_days_ago).order_by('-date')
    monthly_stats = MonthlyReport.objects.filter(year=current_year).order_by('month')
    department_stats = DepartmentStat.objects.all().order_by('department_name', '-date')
    bed_utilization = BedUtilizationReport.objects.filter(date__gte=thirty_days_ago).order_by('-date')
    medicine_consumption = MedicineConsumption.objects.filter(year=current_year).order_by('medicine_name', 'month')

    context = {
        'daily_stats': daily_stats,
        'monthly_stats': monthly_stats,
        'department_stats': department_stats,
        'bed_utilization': bed_utilization,
        'medicine_consumption': medicine_consumption,
    }
    return render(request, 'analytics/analytics_dashboard.html', context)


@admin_required
def daily_admissions(request):
    today = timezone.now().date()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    admissions = DailyAdmission.objects.all().order_by('-date')

    if start_date:
        admissions = admissions.filter(date__gte=start_date)
    if end_date:
        admissions = admissions.filter(date__lte=end_date)

    if not start_date and not end_date:
        admissions = admissions.filter(date__gte=today - timezone.timedelta(days=30))

    context = {
        'admissions': admissions,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'analytics/daily_admissions.html', context)


@admin_required
def monthly_admissions(request):
    current_year = timezone.now().year
    year = request.GET.get('year', current_year)

    try:
        year = int(year)
    except (ValueError, TypeError):
        year = current_year

    reports = MonthlyReport.objects.filter(year=year).order_by('month')
    years = MonthlyReport.objects.values_list('year', flat=True).distinct().order_by('-year')

    context = {
        'reports': reports,
        'selected_year': year,
        'years': years,
    }
    return render(request, 'analytics/monthly_admissions.html', context)


@admin_required
def department_analytics(request):
    dept_name = request.GET.get('department')

    stats = DepartmentStat.objects.all().order_by('department_name', '-date')

    if dept_name:
        stats = stats.filter(department_name__icontains=dept_name)

    departments = DepartmentStat.objects.values_list('department_name', flat=True).distinct().order_by('department_name')

    context = {
        'stats': stats,
        'departments': departments,
        'selected_department': dept_name,
    }
    return render(request, 'analytics/department_analytics.html', context)


@admin_required
def bed_utilization_view(request):
    today = timezone.now().date()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    reports = BedUtilizationReport.objects.all().order_by('-date')

    if start_date:
        reports = reports.filter(date__gte=start_date)
    if end_date:
        reports = reports.filter(date__lte=end_date)

    if not start_date and not end_date:
        reports = reports.filter(date__gte=today - timezone.timedelta(days=30))

    context = {
        'reports': reports,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'analytics/bed_utilization.html', context)


@admin_required
def medicine_consumption_view(request):
    current_year = timezone.now().year
    year = request.GET.get('year', current_year)
    medicine = request.GET.get('medicine', '')

    try:
        year = int(year)
    except (ValueError, TypeError):
        year = current_year

    consumption = MedicineConsumption.objects.filter(year=year).order_by('medicine_name', 'month')

    if medicine:
        consumption = consumption.filter(medicine_name__icontains=medicine)

    medicines = MedicineConsumption.objects.values_list('medicine_name', flat=True).distinct().order_by('medicine_name')
    years = MedicineConsumption.objects.values_list('year', flat=True).distinct().order_by('-year')

    context = {
        'consumption': consumption,
        'selected_year': year,
        'years': years,
        'selected_medicine': medicine,
        'medicines': medicines,
    }
    return render(request, 'analytics/medicine_consumption.html', context)
