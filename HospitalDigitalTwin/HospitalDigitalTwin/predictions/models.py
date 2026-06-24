from django.db import models

class Prediction(models.Model):
    PREDICTION_TYPE = [
        ('bed_occupancy', 'Bed Occupancy'),
        ('medicine_shortage', 'Medicine Shortage'),
        ('patient_load', 'Patient Load'),
        ('risk_prediction', 'Risk Prediction'),
    ]

    prediction_type = models.CharField(max_length=50, choices=PREDICTION_TYPE)
    department_name = models.CharField(max_length=100, blank=True)
    predicted_date = models.DateField()
    predicted_value = models.FloatField()
    confidence_score = models.FloatField()
    actual_value = models.FloatField(null=True, blank=True)
    features_used = models.TextField(blank=True)
    model_used = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-predicted_date']

    def __str__(self):
        return f"{self.prediction_type} - {self.predicted_date}: {self.predicted_value}"

class RiskPrediction(models.Model):
    RISK_LEVEL = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')]

    patient_id = models.CharField(max_length=20)
    patient_name = models.CharField(max_length=200)
    age = models.IntegerField()
    GENDER_CHOICES = [('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    diagnosis = models.TextField()
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL)
    risk_score = models.FloatField()
    explanation = models.TextField()
    prevention_tips = models.TextField()
    food_history_notes = models.TextField(blank=True)
    predicted_condition = models.CharField(max_length=200)
    recommendations = models.TextField()
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_name} - {self.risk_level} risk ({self.risk_score:.2f}%)"

class PredictionModel(models.Model):
    name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=50)
    accuracy = models.FloatField()
    trained_on = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    model_path = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - Acc: {self.accuracy:.2f}%"
