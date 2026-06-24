from django.db import models

class DailyAdmission(models.Model):
    date = models.DateField(unique=True)
    total_admissions = models.IntegerField(default=0)
    total_discharges = models.IntegerField(default=0)
    emergency_cases = models.IntegerField(default=0)
    outpatient_visits = models.IntegerField(default=0)

    def __str__(self):
        return f"Daily Admission - {self.date}"

class MonthlyReport(models.Model):
    month = models.IntegerField()
    year = models.IntegerField()
    total_patients = models.IntegerField(default=0)
    total_admissions = models.IntegerField(default=0)
    total_discharges = models.IntegerField(default=0)
    total_appointments = models.IntegerField(default=0)
    bed_utilization_rate = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['month', 'year']

    def __str__(self):
        return f"Monthly Report - {self.month}/{self.year}"

class DepartmentStat(models.Model):
    department_name = models.CharField(max_length=100)
    date = models.DateField()
    patient_count = models.IntegerField(default=0)
    appointment_count = models.IntegerField(default=0)
    bed_utilization = models.FloatField(default=0)

    class Meta:
        unique_together = ['department_name', 'date']

    def __str__(self):
        return f"{self.department_name} - {self.date}"

class BedUtilizationReport(models.Model):
    date = models.DateField()
    icu_occupied = models.IntegerField(default=0)
    general_occupied = models.IntegerField(default=0)
    emergency_occupied = models.IntegerField(default=0)
    total_beds = models.IntegerField(default=0)
    occupied_beds = models.IntegerField(default=0)
    utilization_rate = models.FloatField(default=0)

    class Meta:
        unique_together = ['date']

    def __str__(self):
        return f"Bed Utilization - {self.date}"

class MedicineConsumption(models.Model):
    medicine_name = models.CharField(max_length=200)
    month = models.IntegerField()
    year = models.IntegerField()
    quantity_consumed = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.medicine_name} - {self.month}/{self.year}"
