import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import date, datetime

from django.db.models import Count, Q
from accounts.decorators import admin_required, patient_session_required
from patients.models import Patient
from beds.models import Bed
from appointments.models import Appointment
from inventory.models import Inventory
from predictions.models import Prediction, RiskPrediction
from disease_risk.models import DiseaseRiskPrediction


@admin_required
def home(request):
    today = date.today()

    total_patients = Patient.objects.exclude(status='discharged').count()
    total_beds = Bed.objects.count()
    available_beds = Bed.objects.filter(status='available').count()
    occupied_beds = Bed.objects.filter(status='occupied').count()
    icu_beds_available = Bed.objects.filter(bed_type='icu', status='available').count()
    emergency_beds_available = Bed.objects.filter(bed_type='emergency', status='available').count()
    general_beds_available = Bed.objects.filter(bed_type='general', status='available').count()
    today_appointments = Appointment.objects.filter(appointment_date=today).count()
    pending_appointments = Appointment.objects.filter(status='scheduled').count()
    low_stock_medicines = Inventory.objects.filter(quantity__lte=10).count()
    expired_medicines = Inventory.objects.filter(expiry_date__lt=today).count()
    recent_patients = Patient.objects.order_by('-created_at')[:5]
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gte=today
    ).order_by('appointment_date', 'appointment_time')[:5]
    bed_utilization_rate = round((occupied_beds / total_beds) * 100, 1) if total_beds > 0 else 0

    recent_predictions = Prediction.objects.order_by('-created_at')[:5]
    risk_alerts = RiskPrediction.objects.filter(
        risk_level__in=['high', 'critical']
    ).order_by('-created_at')[:5]

    emergency_count = Patient.objects.filter(status='emergency').count()

    total_disease_predictions = DiseaseRiskPrediction.objects.count()
    high_risk_count = DiseaseRiskPrediction.objects.filter(risk_level='high').count()
    medium_risk_count = DiseaseRiskPrediction.objects.filter(risk_level='medium').count()
    low_risk_count = DiseaseRiskPrediction.objects.filter(risk_level='low').count()
    recent_disease_predictions = DiseaseRiskPrediction.objects.order_by('-created_at')[:5]

    disease_stats = DiseaseRiskPrediction.objects.values('disease_type').annotate(
        total=Count('id'),
        high_risk=Count('id', filter=Q(risk_level='high')),
    ).order_by('-total')

    context = {
        'total_patients': total_patients,
        'total_beds': total_beds,
        'available_beds': available_beds,
        'occupied_beds': occupied_beds,
        'icu_beds_available': icu_beds_available,
        'emergency_beds_available': emergency_beds_available,
        'general_beds_available': general_beds_available,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'low_stock_medicines': low_stock_medicines,
        'expired_medicines': expired_medicines,
        'recent_patients': recent_patients,
        'upcoming_appointments': upcoming_appointments,
        'bed_utilization_rate': bed_utilization_rate,
        'recent_predictions': recent_predictions,
        'risk_alerts': risk_alerts,
        'emergency_count': emergency_count,
        'total_disease_predictions': total_disease_predictions,
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'low_risk_count': low_risk_count,
        'recent_disease_predictions': recent_disease_predictions,
        'disease_stats': disease_stats,
    }
    return render(request, 'dashboard/home.html', context)


@admin_required
def dashboard_new(request):
    today = date.today()

    total_patients = Patient.objects.exclude(status='discharged').count()
    total_beds = Bed.objects.count()
    available_beds = Bed.objects.filter(status='available').count()
    occupied_beds = Bed.objects.filter(status='occupied').count()
    icu_beds_available = Bed.objects.filter(bed_type='icu', status='available').count()
    emergency_beds_available = Bed.objects.filter(bed_type='emergency', status='available').count()
    general_beds_available = Bed.objects.filter(bed_type='general', status='available').count()
    today_appointments = Appointment.objects.filter(appointment_date=today).count()
    pending_appointments = Appointment.objects.filter(status='scheduled').count()
    low_stock_medicines = Inventory.objects.filter(quantity__lte=10).count()
    expired_medicines = Inventory.objects.filter(expiry_date__lt=today).count()
    recent_patients = Patient.objects.order_by('-created_at')[:5]
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gte=today
    ).order_by('appointment_date', 'appointment_time')[:5]
    bed_utilization_rate = round((occupied_beds / total_beds) * 100, 1) if total_beds > 0 else 0
    emergency_count = Patient.objects.filter(status='emergency').count()

    recent_predictions = Prediction.objects.order_by('-created_at')[:5]
    risk_alerts = RiskPrediction.objects.filter(
        risk_level__in=['high', 'critical']
    ).order_by('-created_at')[:5]

    total_disease_predictions = DiseaseRiskPrediction.objects.count()
    high_risk_count = DiseaseRiskPrediction.objects.filter(risk_level='high').count()
    medium_risk_count = DiseaseRiskPrediction.objects.filter(risk_level='medium').count()
    low_risk_count = DiseaseRiskPrediction.objects.filter(risk_level='low').count()
    recent_disease_predictions = DiseaseRiskPrediction.objects.order_by('-created_at')[:5]

    disease_stats = DiseaseRiskPrediction.objects.values('disease_type').annotate(
        total=Count('id'),
        high_risk=Count('id', filter=Q(risk_level='high')),
    ).order_by('-total')

    class SampleObj:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    if not recent_patients:
        recent_patients = [
            SampleObj(patient_id='P-001', first_name='Sarah', last_name='Johnson', gender='Female', status='admitted', get_status_display=lambda: 'Admitted'),
            SampleObj(patient_id='P-002', first_name='Michael', last_name='Chen', gender='Male', status='admitted', get_status_display=lambda: 'Admitted'),
            SampleObj(patient_id='P-003', first_name='Emily', last_name='Rodriguez', gender='Female', status='emergency', get_status_display=lambda: 'Emergency'),
            SampleObj(patient_id='P-004', first_name='James', last_name='Williams', gender='Male', status='outpatient', get_status_display=lambda: 'Outpatient'),
            SampleObj(patient_id='P-005', first_name='Sophia', last_name='Patel', gender='Female', status='admitted', get_status_display=lambda: 'Admitted'),
        ]
    if not upcoming_appointments:
        upcoming_appointments = [
            SampleObj(patient=SampleObj(first_name='Emily', last_name='Clark'), appointment_date=today, get_status_display=lambda: 'Scheduled', status='scheduled'),
            SampleObj(patient=SampleObj(first_name='David', last_name='Kim'), appointment_date=today, get_status_display=lambda: 'Scheduled', status='scheduled'),
            SampleObj(patient=SampleObj(first_name='Anna', last_name='Martinez'), appointment_date=today, get_status_display=lambda: 'Confirmed', status='confirmed'),
            SampleObj(patient=SampleObj(first_name='John', last_name='Davis'), appointment_date=today, get_status_display=lambda: 'Scheduled', status='scheduled'),
            SampleObj(patient=SampleObj(first_name='Maria', last_name='Garcia'), appointment_date=today, get_status_display=lambda: 'Completed', status='completed'),
        ]
    if not recent_predictions:
        recent_predictions = [
            SampleObj(prediction_type='bed_occupancy', get_prediction_type_display=lambda: 'Bed Occupancy', predicted_date=today, predicted_value='152', confidence_score=94),
            SampleObj(prediction_type='patient_load', get_prediction_type_display=lambda: 'Patient Load', predicted_date=today, predicted_value='18', confidence_score=89),
            SampleObj(prediction_type='medicine_shortage', get_prediction_type_display=lambda: 'Medicine Shortage', predicted_date=today, predicted_value='6', confidence_score=87),
            SampleObj(prediction_type='risk', get_prediction_type_display=lambda: 'Risk Assessment', predicted_date=today, predicted_value='92%', confidence_score=96),
            SampleObj(prediction_type='bed_occupancy', get_prediction_type_display=lambda: 'Bed Occupancy', predicted_date=today, predicted_value='138', confidence_score=91),
        ]
    if not risk_alerts:
        risk_alerts = [
            SampleObj(patient_name='Robert Smith', risk_level='critical', risk_score=92.5),
            SampleObj(patient_name='Jennifer Lee', risk_level='high', risk_score=86.3),
            SampleObj(patient_name='William Brown', risk_level='high', risk_score=81.7),
            SampleObj(patient_name='Amanda Taylor', risk_level='medium', risk_score=74.2),
            SampleObj(patient_name='Christopher Doe', risk_level='medium', risk_score=68.9),
        ]

    context = {
        'total_patients': total_patients,
        'total_beds': total_beds,
        'available_beds': available_beds,
        'occupied_beds': occupied_beds,
        'icu_beds_available': icu_beds_available,
        'emergency_beds_available': emergency_beds_available,
        'general_beds_available': general_beds_available,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'low_stock_medicines': low_stock_medicines,
        'expired_medicines': expired_medicines,
        'recent_patients': recent_patients,
        'upcoming_appointments': upcoming_appointments,
        'bed_utilization_rate': bed_utilization_rate,
        'recent_predictions': recent_predictions,
        'risk_alerts': risk_alerts,
        'emergency_count': emergency_count,
        'total_disease_predictions': total_disease_predictions,
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'low_risk_count': low_risk_count,
        'recent_disease_predictions': recent_disease_predictions,
        'disease_stats': disease_stats,
    }
    return render(request, 'dashboard/dashboard.html', context)


@admin_required
def staff_dashboard(request):
    today = date.today()

    today_admissions = Patient.objects.filter(
        admission_date__date=today
    ).count()

    today_discharges = Patient.objects.filter(
        discharge_date__date=today
    ).count()

    pending_admissions = Patient.objects.filter(
        status='admitted', discharge_date__isnull=True
    ).count()

    pending_appointments = Appointment.objects.filter(status='scheduled').count()
    low_stock_count = Inventory.objects.filter(quantity__lte=10).count()
    beds_in_maintenance = Bed.objects.filter(status='maintenance').count()

    pending_tasks = {
        'pending_admissions': pending_admissions,
        'pending_appointments': pending_appointments,
        'low_stock_count': low_stock_count,
        'beds_in_maintenance': beds_in_maintenance,
    }

    context = {
        'today_admissions': today_admissions,
        'today_discharges': today_discharges,
        'pending_tasks': pending_tasks,
    }
    return render(request, 'dashboard/staff_dashboard.html', context)


def patient_dashboard(request):
    if 'patient_name' not in request.session:
        return render(request, 'accounts/login.html', {
            'active_tab': 'patient',
            'redirect_to': '/',
        })

    patient_name = request.session.get('patient_name', 'Patient')
    patient_age = request.session.get('patient_age', '')
    patient_gender = request.session.get('patient_gender', '')

    import json
    risk_data = json.loads(request.session.get('patient_risk_assessments', '[]'))
    vitals_data = json.loads(request.session.get('patient_vitals', '[]'))

    context = {
        'patient_name': patient_name,
        'patient_age': patient_age,
        'patient_gender': patient_gender,
        'patient_blood_type': request.session.get('patient_blood_type', ''),
        'patient_height': request.session.get('patient_height', ''),
        'patient_weight': request.session.get('patient_weight', ''),
        'risk_assessments': risk_data[-5:],
        'vitals': vitals_data[-5:],
        'risk_count': len(risk_data),
        'vitals_count': len(vitals_data),
    }
    return render(request, 'patient/dashboard.html', context)


@patient_session_required
def patient_profile(request):
    fields = [
        ('Name', request.session.get('patient_name', '—')),
        ('Age', request.session.get('patient_age', '—')),
        ('Gender', request.session.get('patient_gender', '—').title()),
        ('Height', f"{request.session.get('patient_height', '—')} cm" if request.session.get('patient_height') else '—'),
        ('Weight', f"{request.session.get('patient_weight', '—')} kg" if request.session.get('patient_weight') else '—'),
        ('Blood Type', request.session.get('patient_blood_type', '—')),
    ]
    return render(request, 'patient/profile.html', {'profile_fields': fields})


@patient_session_required
def patient_appointments(request):
    return render(request, 'patient/appointments.html', {
        'patient_name': request.session.get('patient_name', 'Patient'),
    })


@patient_session_required
def patient_medical_history(request):
    return render(request, 'patient/medical_history.html', {
        'patient_name': request.session.get('patient_name', 'Patient'),
    })


@patient_session_required
def patient_disease_risk(request):
    import json
    risk_data = json.loads(request.session.get('patient_risk_assessments', '[]'))
    return render(request, 'patient/disease_risk_results.html', {
        'risks': risk_data,
        'patient_name': request.session.get('patient_name', 'Patient'),
    })


@patient_session_required
def patient_reports(request):
    return render(request, 'patient/reports.html', {
        'patient_name': request.session.get('patient_name', 'Patient'),
    })


@patient_session_required
def patient_health_analytics(request):
    import json
    risk_data = json.loads(request.session.get('patient_risk_assessments', '[]'))
    return render(request, 'patient/health_analytics.html', {
        'risks': risk_data,
        'patient_name': request.session.get('patient_name', 'Patient'),
    })


import re

FOOD_IMG = 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=600&h=200&fit=crop'
MED_IMG = 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600&h=200&fit=crop'

SYMPTOM_ADVICE = {
    'headache': {
        'cause': 'Tension headaches, dehydration, eye strain, sinus issues, or migraines.',
        'eat': 'Magnesium-rich foods (almonds, spinach, bananas), ginger, and berries.',
        'drink': 'Water with lemon, peppermint tea, or chamomile tea (8-10 glasses of water daily).',
        'avoid': 'Caffeine (if overused), alcohol, processed foods with MSG, and bright screens.',
        'medicines': 'Paracetamol (500mg) or Ibuprofen (200mg) for mild headaches. Do not exceed recommended dosage.',
        'lifestyle': 'Maintain regular sleep schedule, reduce screen time, practice neck stretches, stay hydrated, and manage stress.',
        'home_remedies': 'Apply a cold or warm compress to forehead. Massage temples with peppermint oil. Rest in a dark, quiet room.',
        'warning': 'Sudden severe headache (thunderclap), headache after head injury, or accompanied by stiff neck, slurred speech, or vision loss.',
        'summary': 'Rest in a dark room, apply cold compress, stay hydrated, take paracetamol if needed. See a doctor if severe or persistent beyond 48 hours.',
        'doctor': 'If headache is severe, sudden, accompanied by fever, stiff neck, or lasts more than 48 hours.',
        'img_food': 'https://images.unsplash.com/photo-1508061253366-f7da158b6d46?w=600&h=200&fit=crop',
        'img_medicine': 'https://images.unsplash.com/photo-1550572017-edd951b55104?w=600&h=200&fit=crop',
    },
    'fever': {
        'cause': 'Viral or bacterial infection, heat exhaustion, inflammatory conditions, or post-vaccination.',
        'eat': 'Light, easily digestible foods like khichdi, soup, boiled vegetables, and fruits rich in vitamin C.',
        'drink': 'Warm water, herbal teas, coconut water, ORS solution, and fresh fruit juices (stay well hydrated).',
        'avoid': 'Spicy, oily, or heavy foods, cold drinks, dairy (if congested), and caffeine.',
        'medicines': 'Paracetamol (650mg) every 6 hours for fever above 100°F. Monitor temperature regularly.',
        'lifestyle': 'Take complete rest, use a damp cloth on forehead, keep the room ventilated, and monitor temperature every 4 hours.',
        'home_remedies': 'Sponge bath with lukewarm water. Apply cool compress to forehead, armpits, and groin. Drink ORS to prevent dehydration.',
        'warning': 'Fever above 103°F, severe headache, stiff neck, rash that does not blanch, difficulty breathing, or confusion.',
        'summary': 'Rest, stay hydrated with ORS and warm fluids, take paracetamol for high fever, monitor temperature. Seek medical help if fever persists beyond 3 days or exceeds 103°F.',
        'doctor': 'If fever exceeds 103°F, lasts more than 3 days, or is accompanied by severe headache, rash, or difficulty breathing.',
        'img_food': 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=600&h=200&fit=crop',
        'img_medicine': 'https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=600&h=200&fit=crop',
    },
    'cough': {
        'cause': 'Common cold, allergies, asthma, GERD, bronchitis, or post-nasal drip.',
        'eat': 'Warm foods like soups, honey with warm water, turmeric milk, and steamed vegetables.',
        'drink': 'Warm water with honey and lemon, ginger tea, tulsi tea, and broths.',
        'avoid': 'Cold foods and drinks, dairy (may increase mucus), fried foods, and sugary snacks.',
        'medicines': 'Honey (1 tsp) for soothing. For dry cough — Dextromethorphan. For wet cough — Guaifenesin.',
        'lifestyle': 'Use a humidifier, elevate pillows while sleeping, gargle with warm salt water, and avoid smoke.',
        'home_remedies': 'Gargle with warm salt water (1 tsp salt in 1 cup water). Steam inhalation with eucalyptus oil. Honey and ginger juice mixture.',
        'warning': 'Cough producing blood, chest pain, difficulty breathing, high fever, or cough lasting more than 3 weeks.',
        'summary': 'Gargle with salt water, use honey for soothing, steam inhalation, stay warm. Consult doctor if cough persists beyond 2 weeks or produces blood.',
        'doctor': 'If cough persists beyond 3 weeks, produces blood, causes chest pain, or is accompanied by high fever.',
        'img_food': 'https://images.unsplash.com/photo-1571934811356-5cc061b6821f?w=600&h=200&fit=crop',
        'img_medicine': 'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=600&h=200&fit=crop',
    },
    'cold': {
        'cause': 'Viral infection (rhinovirus), seasonal allergies, or weakened immune system.',
        'eat': 'Warm soups, chicken soup, garlic, ginger, turmeric milk, and vitamin C rich fruits (oranges, amla).',
        'drink': 'Warm water, herbal teas (tulsi, ginger, peppermint), honey lemon water, and broths.',
        'avoid': 'Cold beverages, dairy products (may thicken mucus), sugary foods, and alcohol.',
        'medicines': 'Antihistamines (Cetirizine) for runny nose, Paracetamol for fever. Decongestants for blocked nose.',
        'lifestyle': 'Steam inhalation, salt water gargling, rest, keep warm, use saline nasal spray.',
        'home_remedies': 'Steam inhalation with menthol or eucalyptus. Salt water gargle. Turmeric milk before bed. Ginger tea with honey.',
        'warning': 'High fever, difficulty breathing, symptoms worsening after 7 days, or severe sinus pain.',
        'summary': 'Steam inhalation, warm fluids, rest, and vitamin C. Most colds resolve in 5-7 days. See a doctor if symptoms worsen or fever develops.',
        'doctor': 'If symptoms worsen after 7 days, high fever develops, or breathing becomes difficult.',
        'img_food': 'https://images.unsplash.com/photo-1607532941433-304659e8198a?w=600&h=200&fit=crop',
        'img_medicine': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600&h=200&fit=crop',
    },
    'stomach': {
        'cause': 'Indigestion, food poisoning, gas, gastritis, IBS, or viral gastroenteritis.',
        'eat': 'BRAT diet (Bananas, Rice, Applesauce, Toast), plain yogurt with probiotics, and boiled potatoes.',
        'drink': 'ORS solution, clear broths, chamomile tea, ginger tea, and coconut water.',
        'avoid': 'Spicy, oily, or fried foods, dairy (if lactose intolerant), carbonated drinks, and raw vegetables.',
        'medicines': 'Antacids for indigestion, ORS for rehydration. Probiotics for gut health.',
        'lifestyle': 'Eat small frequent meals, avoid lying down after eating, manage stress, and wash hands regularly.',
        'home_remedies': 'Ginger tea or grated ginger with honey. Fennel seeds after meals. Peppermint tea for gas. Warm compress on abdomen.',
        'warning': 'Severe abdominal pain, blood in stool or vomit, persistent vomiting, signs of dehydration (dry mouth, no urination), high fever.',
        'summary': 'Follow BRAT diet, stay hydrated with ORS, rest your stomach. Avoid solid foods for a few hours. Seek immediate care if severe pain or blood.',
        'doctor': 'If severe abdominal pain, blood in stool, persistent vomiting, or symptoms last more than 48 hours.',
        'img_food': 'https://images.unsplash.com/photo-1571771894821-ce9b6ba11a94?w=600&h=200&fit=crop',
        'img_medicine': 'https://images.unsplash.com/photo-1550572017-edd951b55104?w=600&h=200&fit=crop',
    },
    'bp': {
        'cause': 'High salt intake, stress, lack of exercise, obesity, genetics, or underlying kidney issues.',
        'eat': 'Leafy greens, berries, bananas, oats, fatty fish (salmon), garlic, and dark chocolate (70%+ cocoa).',
        'drink': 'Beetroot juice, hibiscus tea, pomegranate juice, and plenty of water. Limit coffee to 1 cup.',
        'avoid': 'Processed foods, excess salt (keep under 5g/day), alcohol, tobacco, and trans fats.',
        'medicines': 'Consult a doctor for prescription. Common options include Amlodipine, Losartan, or Enalapril. Never self-prescribe.',
        'lifestyle': 'Walk 30 min daily, practice deep breathing, reduce sodium, monitor BP weekly, maintain healthy weight.',
        'home_remedies': 'Deep breathing exercises (5 min, 3x daily). Hibiscus tea twice daily. Garlic consumption. Stress reduction through meditation.',
        'warning': 'BP reading above 180/120 (hypertensive crisis), chest pain, severe headache, shortness of breath, vision changes, or nosebleeds.',
        'summary': 'Reduce sodium intake, exercise daily, monitor BP at home, manage stress. See a doctor if BP consistently above 140/90 or if you experience chest pain.',
        'doctor': 'If BP consistently above 140/90, or if you experience chest pain, severe headache, or vision changes.',
        'img_food': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&h=200&fit=crop',
        'img_medicine': 'https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=600&h=200&fit=crop',
    },
    'sugar': {
        'cause': 'High carbohydrate intake, insulin resistance, lack of physical activity, genetics, or stress.',
        'eat': 'Fiber-rich foods (oats, dal, vegetables), bitter gourd, fenugreek seeds, nuts, and whole grains.',
        'drink': 'Water (8-10 glasses), cinnamon tea, methi water, green tea, and bitter gourd juice.',
        'avoid': 'Sugary drinks, white rice/bread, sweets, packaged juices, fried foods, and refined flour.',
        'medicines': 'Consult a doctor. Common medications include Metformin. Monitor blood sugar regularly. Never adjust medication without medical advice.',
        'lifestyle': 'Walk after meals, maintain meal timing, practice portion control, exercise 30 min daily, manage stress.',
        'home_remedies': 'Fenugreek seed water (soak overnight, drink in morning). Cinnamon powder (1/2 tsp daily). Bitter gourd juice. Curry leaves.',
        'warning': 'Blood sugar above 250 mg/dL with ketones, extreme thirst, frequent urination, fruity breath odor, confusion, or loss of consciousness.',
        'summary': 'Monitor blood sugar regularly, follow a low-GI diet, exercise daily, stay hydrated. Seek immediate care if blood sugar is very high or you feel confused.',
        'doctor': 'If fasting sugar > 126 mg/dL, random sugar > 200 mg/dL, or symptoms of extreme thirst/frequent urination.',
        'img_food': 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=600&h=200&fit=crop',
        'img_medicine': 'https://images.unsplash.com/photo-1571771894821-ce9b6ba11a94?w=600&h=200&fit=crop',
    },
    'body': {
        'cause': 'Viral infection (dengue, flu), overexertion, vitamin D deficiency, fibromyalgia, or autoimmune conditions.',
        'eat': 'Protein-rich foods (eggs, lentils, chicken), leafy greens, nuts, seeds, and fruits rich in antioxidants.',
        'drink': 'Warm turmeric milk, ginger tea, bone broth, coconut water, and plenty of water.',
        'avoid': 'Processed foods, excessive sugar, alcohol, and fried foods that increase inflammation.',
        'medicines': 'Paracetamol or Ibuprofen for pain relief. Apply topical pain relief gels. Vitamin D supplements if deficient.',
        'lifestyle': 'Gentle stretching, warm compress on sore areas, Epsom salt baths, adequate sleep, and stress reduction.',
        'home_remedies': 'Epsom salt bath for muscle relaxation. Warm compress on sore areas. Turmeric milk before bed. Gentle yoga or stretching.',
        'warning': 'Severe pain that limits movement, pain accompanied by high fever, swelling or redness in joints, numbness or tingling.',
        'summary': 'Rest, apply warm compress, take over-the-counter pain relief if needed, gentle stretching. See a doctor if severe or persists beyond a week.',
        'doctor': 'If pain is severe, persists more than a week, or is accompanied by fever, swelling, or redness.',
        'img_food': 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=600&h=200&fit=crop',
        'img_medicine': 'https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=600&h=200&fit=crop',
    },
    'throat': {
        'cause': 'Viral pharyngitis, strep throat, allergies, dry air, or vocal strain.',
        'eat': 'Warm soups, mashed potatoes, scrambled eggs, honey, smoothies, and soft fruits.',
        'drink': 'Warm water with honey and lemon, ginger tea, tulsi tea, chamomile tea, and broths.',
        'avoid': 'Spicy foods, acidic foods (citrus, tomatoes), hard/crunchy foods, cold drinks, and smoking.',
        'medicines': 'Salt water gargle (1 tsp salt in warm water). Lozenges for relief. Paracetamol for pain.',
        'lifestyle': 'Rest your voice, use a humidifier, avoid clearing throat aggressively, and gargle regularly.',
        'home_remedies': 'Salt water gargle every 3-4 hours. Honey and lemon mixture. Ginger tea with honey. Steam inhalation. Marshmallow root tea.',
        'warning': 'Difficulty breathing or swallowing, drooling, muffled voice, fever above 101°F, white patches on tonsils, or swollen neck glands.',
        'summary': 'Gargle with salt water, drink warm honey-lemon water, rest your voice, use lozenges. See a doctor if severe pain or white patches on tonsils.',
        'doctor': 'If severe pain, difficulty swallowing, fever above 101°F, or white patches on tonsils.',
        'img_food': 'https://images.unsplash.com/photo-1604329760661-e71dc83f8f26?w=600&h=200&fit=crop',
        'img_medicine': 'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=600&h=200&fit=crop',
    },
}

def _format_advice(key, data):
    return (
        f"**🩺 Possible Cause**\n{data['cause']}\n\n"
        f"**🥗 What to Eat**\n{data['eat']}\n"
        f"<img src=\"{data['img_food']}\" alt=\"Recommended Foods\" style=\"width:100%;max-width:500px;border-radius:10px;margin:8px 0;\">\n\n"
        f"**🥤 What to Drink**\n{data['drink']}\n\n"
        f"**🚫 What to Avoid**\n{data['avoid']}\n\n"
        f"**🏠 Home Remedies**\n{data['home_remedies']}\n\n"
        f"**💊 Recommended Medicines**\n{data['medicines']}\n"
        f"<img src=\"{data['img_medicine']}\" alt=\"Recommended Medicines\" style=\"width:100%;max-width:500px;border-radius:10px;margin:8px 0;\">\n\n"
        f"**🧘 Lifestyle Advice**\n{data['lifestyle']}\n\n"
        f"**⚠️ Warning Signs**\n{data['warning']}\n\n"
        f"**📞 When to See Doctor**\n{data['doctor']}\n\n"
        f"**📋 Summary**\n{data['summary']}"
    )


@patient_session_required
def patient_chat_respond(request):
    if request.method != 'POST':
        return JsonResponse({'response': 'Invalid request.'})
    message = request.POST.get('message', '').lower().strip()

    if not message:
        return JsonResponse({'response': 'Please describe your symptom or health concern.'})

    name = request.session.get('patient_name', '')
    age = request.session.get('patient_age', '')
    height = request.session.get('patient_height', '')
    weight = request.session.get('patient_weight', '')
    risk_data = json.loads(request.session.get('patient_risk_assessments', '[]'))
    vitals = json.loads(request.session.get('patient_vitals', '[]'))

    age_group = 'child (<12)' if age and int(age) < 12 else 'teen (12-19)' if age and int(age) < 20 else 'adult (20-60)' if age and int(age) < 60 else 'senior (60+)'

    if any(w in message for w in ['hi', 'hello', 'hey']):
        return JsonResponse({'response': f"Hello {name}! I'm your health assistant. Tell me how you're feeling or describe your symptom — for example: \"I have a headache\", \"my stomach hurts\", \"I have a fever\", or \"my blood pressure is high\". I'll give you immediate guidance."})

    if any(w in message for w in ['bmi', 'bmi?']):
        if height and weight:
            h = float(height) / 100
            w = float(weight)
            bmi_val = round(w / (h * h), 1)
            cat = 'underweight' if bmi_val < 18.5 else 'normal weight' if bmi_val < 25 else 'overweight' if bmi_val < 30 else 'obese'
            return JsonResponse({'response': (
                f"**Your BMI Result**\n\n"
                f"Your BMI is **{bmi_val}** — classified as **{cat}**.\n\n"
                f"**What this means:**\n"
                f"{'You may need to gain some weight through a balanced diet.' if bmi_val < 18.5 else 'You are at a healthy weight. Maintain your current lifestyle.' if bmi_val < 25 else 'Consider a balanced diet and regular exercise to reduce health risks.' if bmi_val < 30 else 'It is recommended to consult a doctor for a personalized weight management plan.'}\n\n"
                f"*For a more accurate assessment, additional factors like muscle mass and body composition matter.*"
            )})
        return JsonResponse({'response': (
            f"**BMI Information**\n\n"
            f"BMI (Body Mass Index) is a measure based on height and weight.\n\n"
            f"Since you haven't entered your height and weight during login, I can't calculate your exact BMI. "
            f"For now, general advice:\n"
            f"- **Healthy BMI range**: 18.5 – 24.9\n"
            f"- Maintain a balanced diet with fruits, vegetables, and protein\n"
            f"- Exercise at least 30 minutes daily\n\n"
            f"*To get your exact BMI, log out and re-enter with your height and weight.*"
        )})

    matched_key = None
    if any(w in message for w in ['headache', 'migraine', 'head']):
        matched_key = 'headache'
    elif any(w in message for w in ['fever', 'temperature', 'high temp']):
        matched_key = 'fever'
    elif any(w in message for w in ['cough', 'dry cough', 'wet cough']):
        matched_key = 'cough'
    elif any(w in message for w in ['cold', 'runny nose', 'sneezing', 'blocked nose']):
        matched_key = 'cold'
    elif any(w in message for w in ['stomach', 'vomiting', 'nausea', 'diarrhea', 'gas', 'acidity', 'indigestion']):
        matched_key = 'stomach'
    elif any(w in message for w in ['bp', 'blood pressure', 'high bp', 'hypertension']):
        matched_key = 'bp'
    elif any(w in message for w in ['sugar', 'diabetes', 'blood sugar', 'high sugar']):
        matched_key = 'sugar'
    elif any(w in message for w in ['body pain', 'body ache', 'muscle pain', 'joint pain']):
        matched_key = 'body'
    elif any(w in message for w in ['sore throat', 'throat pain', 'throat infection']):
        matched_key = 'throat'

    if matched_key:
        advice = SYMPTOM_ADVICE[matched_key]
        header = f"**Health Guidance for {message.title()}**\n\n*Based on: {age_group} · {'Height: ' + height + 'cm' if height else 'Height: N/A'} · {'Weight: ' + weight + 'kg' if weight else 'Weight: N/A'}*\n\n---\n\n"
        return JsonResponse({'response': header + _format_advice(matched_key, advice)})

    if any(w in message for w in ['risk', 'assessment']):
        if risk_data:
            last = risk_data[-1]
            high_risks = [r for r in risk_data if r['level'] == 'high']
            body = (
                f"**Your Risk Assessment Summary**\n\n"
                f"Latest: **{last['disease'].title()}** — **{last['level'].title()} Risk** ({last['score']}%)\n\n"
            )
            if high_risks:
                body += f"⚠️ You have **{len(high_risks)} high-risk** result(s). It's advisable to consult a doctor.\n\n"
            body += f"Total assessments done: {len(risk_data)}\n\n**Next step:** Take a new assessment from the Disease Risk tool for updated results."
            return JsonResponse({'response': body})
        return JsonResponse({'response': (
            f"**Disease Risk Assessment**\n\n"
            f"You haven't done any risk assessments yet.\n\n"
            f"**Based on your profile ({age_group}):**\n"
            f"- If you're experiencing any symptoms, I've provided guidance above\n"
            f"- For a detailed AI-based risk assessment for diabetes, heart disease, hypertension, or kidney disease, "
            f"use the disease risk tool\n\n"
            f"**General prevention tips:**\n"
            f"✅ Regular exercise (30 min/day)\n"
            f"✅ Balanced diet with fruits and vegetables\n"
            f"✅ Annual health check-ups\n"
            f"✅ Stay hydrated (8-10 glasses of water)"
        )})

    if any(w in message for w in ['vitals', 'bp reading', 'sugar level']):
        if vitals:
            v = vitals[-1]
            return JsonResponse({'response': (
                f"**Your Last Recorded Vitals**\n\n"
                f"🩸 **Blood Pressure:** {v['bp']} mmHg\n"
                f"🍬 **Sugar Level:** {v['sugar']} mg/dL\n"
                f"📏 **BMI:** {v['bmi']}\n"
                f"🧪 **Cholesterol:** {v['cholesterol']} mg/dL\n\n"
                f"*Normal ranges: BP <120/80, Fasting Sugar <100 mg/dL, Cholesterol <200 mg/dL*"
            )})
        return JsonResponse({'response': (
            f"**Health Vitals**\n\n"
            f"No vitals recorded yet. But here are general healthy ranges for someone in the **{age_group}** age group:\n\n"
            f"- **Blood Pressure:** <120/80 mmHg\n"
            f"- **Fasting Blood Sugar:** 70-100 mg/dL\n"
            f"- **Total Cholesterol:** <200 mg/dL\n"
            f"- **BMI:** 18.5-24.9\n\n"
            f"🩺 Get regular health check-ups to track your numbers."
        )})

    return JsonResponse({'response': (
        f"**Health Guidance**\n\n"
        f"I understand you're asking about \"{message.title()}\". While I don't have specific details, here's general advice:\n\n"
        f"**🩺 Possible Cause**\n"
        f"This could be related to diet, stress, lack of sleep, or an underlying condition. {age_group} individuals are commonly affected by lifestyle-related issues.\n\n"
        f"**🥗 What to Eat**\n"
        f"Focus on whole foods: fruits, vegetables, lean proteins, whole grains, and healthy fats.\n\n"
        f"**🥤 What to Drink**\n"
        f"Water (8-10 glasses daily), herbal teas, fresh fruit juices without added sugar.\n\n"
        f"**🚫 What to Avoid**\n"
        f"Processed foods, excessive sugar, smoking, alcohol, and sedentary lifestyle.\n\n"
        f"**💊 Recommended Medicines**\n"
        f"Please consult a doctor for proper diagnosis before taking any medication.\n\n"
        f"**🧘 Lifestyle Advice**\n"
        f"Exercise 30 min/day, sleep 7-8 hours, manage stress through meditation or deep breathing.\n\n"
        f"**📞 When to See Doctor**\n"
        f"If symptoms persist for more than 3-5 days, worsen, or significantly affect daily activities.\n\n"
        f"---\n*For more specific advice, try describing your symptom (e.g., \"I have a headache\", \"my stomach hurts\", \"I have fever\").*"
    )})
