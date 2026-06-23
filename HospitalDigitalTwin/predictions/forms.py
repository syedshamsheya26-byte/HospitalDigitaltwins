from django import forms
from .models import RiskPrediction

class RiskPredictionForm(forms.ModelForm):
    class Meta:
        model = RiskPrediction
        fields = ['patient_id', 'patient_name', 'age', 'gender', 'diagnosis']
        widgets = {
            'patient_id': forms.TextInput(attrs={'class': 'form-control'}),
            'patient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
