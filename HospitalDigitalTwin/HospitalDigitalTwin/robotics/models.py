from django.db import models
from django.contrib.auth.models import User

class SurgeryRobot(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Maintenance'),
        ('offline', 'Offline'),
    ]
    robot_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    robot_type = models.CharField(max_length=100, help_text='e.g. Da Vinci Xi, Mazor X')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    location = models.CharField(max_length=200)
    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.robot_id}) - {self.status}"

class RoboticProcedure(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    procedure_id = models.CharField(max_length=50, unique=True)
    patient_name = models.CharField(max_length=200)
    robot = models.ForeignKey(SurgeryRobot, on_delete=models.CASCADE, related_name='procedures')
    procedure_type = models.CharField(max_length=200)
    surgeon = models.CharField(max_length=200)
    scheduled_date = models.DateField()
    duration_hours = models.FloatField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.procedure_id} - {self.patient_name} ({self.procedure_type})"
