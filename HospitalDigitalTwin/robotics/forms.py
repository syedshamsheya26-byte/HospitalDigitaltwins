from django import forms
from .models import SurgeryRobot, RoboticProcedure

class SurgeryRobotForm(forms.ModelForm):
    class Meta:
        model = SurgeryRobot
        fields = ['robot_id', 'name', 'robot_type', 'status', 'location', 'last_maintenance', 'next_maintenance']
        widgets = {
            'robot_id': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'robot_type': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'last_maintenance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'next_maintenance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class RoboticProcedureForm(forms.ModelForm):
    class Meta:
        model = RoboticProcedure
        fields = ['patient_name', 'robot', 'procedure_type', 'surgeon', 'scheduled_date', 'duration_hours', 'status', 'notes']
        widgets = {
            'patient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'robot': forms.Select(attrs={'class': 'form-select'}),
            'procedure_type': forms.TextInput(attrs={'class': 'form-control'}),
            'surgeon': forms.TextInput(attrs={'class': 'form-control'}),
            'scheduled_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
