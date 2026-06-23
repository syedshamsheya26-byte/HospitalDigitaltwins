from django import forms
from .models import DiseaseRiskPrediction


class DiseaseRiskForm(forms.ModelForm):
    class Meta:
        model = DiseaseRiskPrediction
        fields = ['patient_name', 'age', 'gender', 'blood_pressure', 'sugar_level', 'bmi', 'cholesterol', 'heart_rate', 'disease_type']
        widgets = {
            'patient_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter patient name'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter age'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'blood_pressure': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 120', 'step': '0.1'}),
            'sugar_level': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 100', 'step': '0.1'}),
            'bmi': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 24.5', 'step': '0.1'}),
            'cholesterol': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 200', 'step': '0.1'}),
            'heart_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 72'}),
            'disease_type': forms.Select(attrs={'class': 'form-control'}),
        }
