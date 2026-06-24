from django.db import models
from patients.models import Patient

class Ward(models.Model):
    name = models.CharField(max_length=100)
    floor = models.IntegerField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} (Floor {self.floor})"

class Bed(models.Model):
    BED_TYPE_CHOICES = [
        ('general', 'General'),
        ('icu', 'ICU'),
        ('emergency', 'Emergency'),
        ('private', 'Private'),
        ('semi_private', 'Semi-Private'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
    ]

    bed_number = models.CharField(max_length=20, unique=True)
    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, related_name='beds')
    bed_type = models.CharField(max_length=20, choices=BED_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_date = models.DateTimeField(null=True, blank=True)
    discharge_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bed {self.bed_number} ({self.bed_type}) - {self.status}"
