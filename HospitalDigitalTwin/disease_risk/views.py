from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from datetime import date

from accounts.decorators import admin_required
from .models import DiseaseRiskPrediction
from .forms import DiseaseRiskForm
from .ml_engine import DiseaseRiskPredictor

predictor = DiseaseRiskPredictor()


@admin_required
def risk_assessment(request):
    saved_prediction = None
    form = DiseaseRiskForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        prediction = form.save(commit=False)
        result = predictor.predict(
            age=prediction.age,
            gender=prediction.gender,
            blood_pressure=prediction.blood_pressure,
            sugar_level=prediction.sugar_level,
            bmi=prediction.bmi,
            cholesterol=prediction.cholesterol,
            heart_rate=prediction.heart_rate,
            disease_type=prediction.disease_type,
        )

        prediction.risk_level = result['risk_level']
        prediction.risk_score = result['risk_score']
        prediction.confidence_score = result['confidence_score']
        prediction.recommendations = result['recommendations']
        prediction.created_by = request.user
        prediction.save()
        saved_prediction = prediction

        messages.success(
            request,
            f'Risk assessment completed for {prediction.patient_name}. '
            f'Risk level: {result["risk_level"].upper()} '
            f'(Confidence: {result["confidence_score"]:.1f}%)'
        )

        form = DiseaseRiskForm()

    total_predictions = DiseaseRiskPrediction.objects.count()
    high_risk_count = DiseaseRiskPrediction.objects.filter(risk_level='high').count()

    context = {
        'form': form,
        'prediction': saved_prediction,
        'total_predictions': total_predictions,
        'high_risk_count': high_risk_count,
    }
    return render(request, 'disease_risk/risk_assessment.html', context)


@admin_required
def prediction_history(request):
    predictions = DiseaseRiskPrediction.objects.select_related('created_by').order_by('-created_at')
    disease = request.GET.get('disease')
    risk = request.GET.get('risk')
    search = request.GET.get('q')

    if disease:
        predictions = predictions.filter(disease_type=disease)
    if risk:
        predictions = predictions.filter(risk_level=risk)
    if search:
        predictions = predictions.filter(patient_name__icontains=search)

    disease_stats = DiseaseRiskPrediction.objects.values('disease_type').annotate(
        count=Count('id'),
        avg_risk=Avg('risk_score'),
    ).order_by('-count')

    risk_distribution = DiseaseRiskPrediction.objects.values('risk_level').annotate(
        count=Count('id'),
    ).order_by('risk_level')

    context = {
        'predictions': predictions,
        'disease_stats': disease_stats,
        'risk_distribution': risk_distribution,
        'selected_disease': disease,
        'selected_risk': risk,
        'search_query': search,
    }
    return render(request, 'disease_risk/prediction_history.html', context)


@admin_required
def prediction_detail(request, pk):
    prediction = get_object_or_404(DiseaseRiskPrediction, pk=pk)
    context = {
        'prediction': prediction,
    }
    return render(request, 'disease_risk/prediction_detail.html', context)


@admin_required
def disease_analytics(request):
    disease_type = request.GET.get('disease')

    disease_stats = DiseaseRiskPrediction.objects.values('disease_type').annotate(
        total=Count('id'),
        high_risk=Count('id', filter=Q(risk_level='high')),
        medium_risk=Count('id', filter=Q(risk_level='medium')),
        low_risk=Count('id', filter=Q(risk_level='low')),
        avg_risk_score=Avg('risk_score'),
        avg_confidence=Avg('confidence_score'),
    ).order_by('-total')

    if disease_type:
        disease_stats = disease_stats.filter(disease_type=disease_type)

    monthly_stats = DiseaseRiskPrediction.objects.extra(
        select={'year': "strftime('%%Y', created_at)", 'month': "strftime('%%m', created_at)"}
    ).values('year', 'month').annotate(
        total=Count('id'),
        high_risk=Count('id', filter=Q(risk_level='high')),
    ).order_by('year', 'month')

    total = DiseaseRiskPrediction.objects.count()
    high = DiseaseRiskPrediction.objects.filter(risk_level='high').count()
    medium = DiseaseRiskPrediction.objects.filter(risk_level='medium').count()
    low = DiseaseRiskPrediction.objects.filter(risk_level='low').count()

    context = {
        'disease_stats': disease_stats,
        'monthly_stats': monthly_stats,
        'total_predictions': total,
        'high_risk_count': high,
        'medium_risk_count': medium,
        'low_risk_count': low,
        'selected_disease': disease_type,
    }
    return render(request, 'disease_risk/disease_analytics.html', context)
