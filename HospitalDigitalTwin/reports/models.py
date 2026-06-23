from django.db import models
from django.contrib.auth.models import User

class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('admission', 'Admission Report'),
        ('inventory', 'Inventory Report'),
        ('prediction', 'Prediction Report'),
        ('disease_risk', 'Disease Risk Report'),
        ('patient', 'Patient Report'),
        ('bed_utilization', 'Bed Utilization Report'),
        ('analytics', 'Analytics Report'),
    ]

    report_id = models.CharField(max_length=20, unique=True)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file_path = models.CharField(max_length=500, blank=True)
    format = models.CharField(max_length=10, default='pdf')
    date_range_start = models.DateField(null=True, blank=True)
    date_range_end = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.report_id} - {self.title}"
