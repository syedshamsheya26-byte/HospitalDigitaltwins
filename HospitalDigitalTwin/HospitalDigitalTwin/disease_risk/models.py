from django.db import models
from django.contrib.auth.models import User


class DiseaseRiskPrediction(models.Model):
    DISEASE_CHOICES = [
        ('diabetes', 'Diabetes'),
        ('heart_disease', 'Heart Disease'),
        ('hypertension', 'Hypertension'),
        ('kidney_disease', 'Kidney Disease'),
    ]

    RISK_LEVEL_CHOICES = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    patient_name = models.CharField(max_length=200)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_pressure = models.FloatField(help_text='Systolic BP in mmHg')
    sugar_level = models.FloatField(help_text='Blood sugar level in mg/dL')
    bmi = models.FloatField(help_text='Body Mass Index')
    cholesterol = models.FloatField(help_text='Total cholesterol in mg/dL')
    heart_rate = models.IntegerField(help_text='Heart rate in bpm')

    disease_type = models.CharField(max_length=50, choices=DISEASE_CHOICES)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES)
    risk_score = models.FloatField()
    confidence_score = models.FloatField()
    recommendations = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient_name} - {self.disease_type}: {self.risk_level} ({self.confidence_score:.1f}%)"
