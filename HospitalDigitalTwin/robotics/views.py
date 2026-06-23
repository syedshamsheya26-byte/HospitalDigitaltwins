from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.decorators import admin_required
from .models import SurgeryRobot, RoboticProcedure
from .forms import SurgeryRobotForm, RoboticProcedureForm

@admin_required
def robot_list(request):
    robots = SurgeryRobot.objects.all()
    status = request.GET.get('status')
    if status:
        robots = robots.filter(status=status)
    return render(request, 'robotics/robot_list.html', {'robots': robots, 'status': status})

@admin_required
def robot_detail(request, pk):
    robot = get_object_or_404(SurgeryRobot, pk=pk)
    procedures = robot.procedures.all().order_by('-scheduled_date')[:10]
    return render(request, 'robotics/robot_detail.html', {'robot': robot, 'procedures': procedures})

@admin_required
def robot_create(request):
    if request.method == 'POST':
        form = SurgeryRobotForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Robot registered.')
            return redirect('robotics:robot_list')
    else:
        form = SurgeryRobotForm()
    return render(request, 'robotics/robot_form.html', {'form': form, 'title': 'Register Surgical Robot'})

@admin_required
def robot_update(request, pk):
    robot = get_object_or_404(SurgeryRobot, pk=pk)
    if request.method == 'POST':
        form = SurgeryRobotForm(request.POST, instance=robot)
        if form.is_valid():
            form.save()
            messages.success(request, 'Robot updated.')
            return redirect('robotics:robot_detail', pk=robot.pk)
    else:
        form = SurgeryRobotForm(instance=robot)
    return render(request, 'robotics/robot_form.html', {'form': form, 'title': 'Update Robot'})

@admin_required
def procedure_list(request):
    procedures = RoboticProcedure.objects.select_related('robot').all().order_by('-scheduled_date')
    status = request.GET.get('status')
    if status:
        procedures = procedures.filter(status=status)
    return render(request, 'robotics/procedure_list.html', {'procedures': procedures, 'status': status})

@admin_required
def procedure_create(request):
    if request.method == 'POST':
        form = RoboticProcedureForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            import secrets
            p.procedure_id = f'RBP-{secrets.token_hex(3).upper()}'
            p.created_by = request.user
            p.save()
            messages.success(request, 'Procedure scheduled.')
            return redirect('robotics:procedure_list')
    else:
        form = RoboticProcedureForm()
    return render(request, 'robotics/procedure_form.html', {'form': form, 'title': 'Schedule Robotic Procedure'})
