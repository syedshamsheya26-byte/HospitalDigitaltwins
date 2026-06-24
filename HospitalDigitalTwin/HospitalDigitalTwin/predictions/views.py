from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta, date

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from django.db.models import Avg

from accounts.decorators import admin_required
from .models import Prediction, RiskPrediction, PredictionModel
from .forms import RiskPredictionForm


@admin_required
def prediction_dashboard(request):
    today = timezone.now().date()
    thirty_days_from_now = today + timezone.timedelta(days=30)

    bed_predictions = Prediction.objects.filter(
        prediction_type='bed_occupancy',
        predicted_date__gte=today,
        predicted_date__lte=thirty_days_from_now
    ).order_by('predicted_date')

    medicine_predictions = Prediction.objects.filter(
        prediction_type='medicine_shortage'
    ).order_by('-predicted_date')[:20]

    patient_load_predictions = Prediction.objects.filter(
        prediction_type='patient_load'
    ).order_by('-predicted_date')[:20]

    recent_risk_predictions = RiskPrediction.objects.order_by('-created_at')[:10]

    models = PredictionModel.objects.all()

    context = {
        'bed_predictions': bed_predictions,
        'medicine_predictions': medicine_predictions,
        'patient_load_predictions': patient_load_predictions,
        'recent_risk_predictions': recent_risk_predictions,
        'models': models,
    }
    return render(request, 'predictions/prediction_dashboard.html', context)


def _generate_synthetic_bed_data(days=90):
    np.random.seed(42)
    base_occupancy = 200
    data = []
    for i in range(days, 0, -1):
        d = date.today() - timedelta(days=i)
        day_of_week = d.weekday()
        weekly_pattern = 20 if day_of_week < 5 else -30
        noise = np.random.normal(0, 25)
        occupancy = base_occupancy + weekly_pattern + noise
        data.append({
            'date': d,
            'occupancy': max(0, round(occupancy)),
            'day_of_week': day_of_week,
            'day_of_month': d.day,
        })
    return data


@admin_required
def predict_bed_occupancy(request):
    today = date.today()
    existing = Prediction.objects.filter(
        prediction_type='bed_occupancy',
        predicted_date__gte=today
    ).count()

    if existing > 0 and request.method != 'POST':
        predictions = Prediction.objects.filter(
            prediction_type='bed_occupancy',
            predicted_date__gte=today
        ).order_by('predicted_date')
        context = {
            'predictions': predictions,
            'model_trained': True,
        }
        return render(request, 'predictions/predict_bed_occupancy.html', context)

    historical = Prediction.objects.filter(
        prediction_type='bed_occupancy',
        predicted_date__lt=today,
        actual_value__isnull=False
    ).order_by('-predicted_date')

    if historical.count() < 30:
        synthetic_data = _generate_synthetic_bed_data(90)
        df = pd.DataFrame(synthetic_data)
        messages.info(request, 'Using synthetic historical data for training.')
    else:
        df = pd.DataFrame(list(historical.values('predicted_date', 'actual_value')))
        df.rename(columns={
            'predicted_date': 'date',
            'actual_value': 'occupancy'
        }, inplace=True)
        df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
        df['day_of_month'] = pd.to_datetime(df['date']).dt.day

    X = df[['day_of_week', 'day_of_month']].values
    y = df['occupancy'].values

    model = LinearRegression()
    model.fit(X, y)

    r2_score = model.score(X, y)

    future_dates = []
    for days_ahead in [7, 15, 30]:
        for d in range(1, days_ahead + 1):
            future_dates.append(today + timedelta(days=d))

    results = []
    for fd in future_dates:
        features = np.array([[fd.weekday(), fd.day]])
        pred_value = model.predict(features)[0]
        confidence = max(50, min(95, round(r2_score * 100 * (1 - 1 / (len(future_dates) + 1)), 1)))
        results.append((fd, max(0, round(pred_value)), confidence))

    for i, (fd, pv, conf) in enumerate(results):
        existing_pred = Prediction.objects.filter(
            prediction_type='bed_occupancy',
            predicted_date=fd
        ).first()
        if existing_pred:
            existing_pred.predicted_value = pv
            existing_pred.confidence_score = conf
            existing_pred.model_used = 'LinearRegression'
            existing_pred.features_used = 'day_of_week, day_of_month'
            existing_pred.save()
        else:
            Prediction.objects.create(
                prediction_type='bed_occupancy',
                predicted_date=fd,
                predicted_value=pv,
                confidence_score=conf,
                model_used='LinearRegression',
                features_used='day_of_week, day_of_month',
            )

    messages.success(request, f'Bed occupancy predictions generated for {len(results)} days.')
    predictions = Prediction.objects.filter(
        prediction_type='bed_occupancy',
        predicted_date__gte=today
    ).order_by('predicted_date')

    context = {
        'predictions': predictions,
        'model_trained': True,
        'r2_score': round(r2_score * 100, 2),
        'training_samples': len(df),
    }
    return render(request, 'predictions/predict_bed_occupancy.html', context)


@admin_required
def predict_medicine_shortage(request):
    from inventory.models import Inventory, StockAlert

    today = date.today()
    low_stock_items = Inventory.objects.select_related('medicine').filter(
        quantity__lte=10,
        expiry_date__gte=today
    ).order_by('quantity')

    predictions = []
    for item in low_stock_items:
        consumption_rate = 1
        sales = StockAlert.objects.filter(
            inventory_item=item,
            alert_type='low_stock',
            status='resolved'
        ).count()
        if sales > 0:
            consumption_rate = max(1, sales // 3)

        days_until_empty = item.quantity // consumption_rate if consumption_rate > 0 else 999
        shortage_date = today + timedelta(days=days_until_empty) if days_until_empty < 365 else today + timedelta(days=365)

        confidence = max(50, min(95, 100 - (days_until_empty * 2)))

        pred, created = Prediction.objects.update_or_create(
            prediction_type='medicine_shortage',
            predicted_date=shortage_date,
            defaults={
                'predicted_value': float(item.quantity),
                'confidence_score': float(confidence),
                'model_used': 'ConsumptionRateAnalysis',
                'features_used': 'inventory_quantity, consumption_rate, expiry_date',
            }
        )

        predictions.append({
            'medicine': item.medicine,
            'current_stock': item.quantity,
            'consumption_rate': consumption_rate,
            'days_until_empty': days_until_empty,
            'shortage_date': shortage_date,
            'confidence': confidence,
            'prediction': pred,
        })

    context = {
        'predictions': predictions,
        'total_medicines': len(predictions),
    }
    return render(request, 'predictions/predict_medicine_shortage.html', context)


def _generate_synthetic_patient_load(days=90):
    np.random.seed(42)
    departments = ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'General Medicine', 'Emergency']
    data = []
    base_loads = {'Cardiology': 25, 'Neurology': 15, 'Orthopedics': 20, 'Pediatrics': 30, 'General Medicine': 40, 'Emergency': 35}
    for i in range(days, 0, -1):
        d = date.today() - timedelta(days=i)
        day_of_week = d.weekday()
        weekly_factor = 1.3 if day_of_week < 5 else 0.7
        for dept in departments:
            base = base_loads[dept]
            noise = np.random.normal(0, 8)
            load = max(0, round(base * weekly_factor + noise))
            data.append({'date': d, 'department': dept, 'count': load, 'day_of_week': day_of_week, 'day_of_month': d.day})
    return data


@admin_required
def predict_patient_load(request):
    today = date.today()
    end_date = today + timedelta(days=30)

    existing_predictions = Prediction.objects.filter(
        prediction_type='patient_load',
        predicted_date__gte=today,
        predicted_date__lte=end_date
    ).order_by('predicted_date')

    if existing_predictions.count() < 30 or request.method == 'POST':
        synthetic = _generate_synthetic_patient_load(90)
        df = pd.DataFrame(synthetic)
        messages.info(request, 'Using synthetic historical data for patient load predictions.')

        for dept_name in df['department'].unique():
            dept_df = df[df['department'] == dept_name]
            X = dept_df[['day_of_week', 'day_of_month']].values
            y = dept_df['count'].values

            lr = LinearRegression()
            lr.fit(X, y)

            for d in range((end_date - today).days + 1):
                fd = today + timedelta(days=d)
                features = np.array([[fd.weekday(), fd.day]])
                pred_val = max(0, round(lr.predict(features)[0]))

                existing_pred = Prediction.objects.filter(
                    prediction_type='patient_load',
                    department_name=dept_name,
                    predicted_date=fd
                ).first()

                if existing_pred:
                    existing_pred.predicted_value = float(pred_val)
                    existing_pred.confidence_score = 75.0
                    existing_pred.model_used = 'LinearRegression'
                    existing_pred.save()
                else:
                    Prediction.objects.create(
                        prediction_type='patient_load',
                        department_name=dept_name,
                        predicted_date=fd,
                        predicted_value=float(pred_val),
                        confidence_score=75.0,
                        model_used='LinearRegression',
                        features_used='synthetic_historical, day_of_week, day_of_month',
                    )

        messages.success(request, f'Patient load predictions generated for {len(df["department"].unique())} departments.')
        existing_predictions = Prediction.objects.filter(
            prediction_type='patient_load',
            predicted_date__gte=today,
            predicted_date__lte=end_date
        ).order_by('predicted_date')

    load_by_department = {}
    for pred in existing_predictions:
        dept_name = pred.department_name if pred.department_name else 'General'
        if dept_name not in load_by_department:
            load_by_department[dept_name] = {'predictions': []}
        load_by_department[dept_name]['predictions'].append(pred)

    context = {
        'load_by_department': load_by_department,
        'predictions': existing_predictions,
    }
    return render(request, 'predictions/predict_patient_load.html', context)


RISK_KEYWORDS = {
    'heart': {'level': 'high', 'condition': 'Cardiovascular Disease'},
    'cardiac': {'level': 'high', 'condition': 'Cardiovascular Disease'},
    'diabetes': {'level': 'high', 'condition': 'Diabetes Mellitus'},
    'diabetic': {'level': 'high', 'condition': 'Diabetes Mellitus'},
    'cancer': {'level': 'critical', 'condition': 'Malignancy'},
    'malignancy': {'level': 'critical', 'condition': 'Malignancy'},
    'tumor': {'level': 'critical', 'condition': 'Neoplasm'},
    'tumour': {'level': 'critical', 'condition': 'Neoplasm'},
    'stroke': {'level': 'high', 'condition': 'Cerebrovascular Accident'},
    'hypertension': {'level': 'medium', 'condition': 'Hypertensive Disease'},
    'bp': {'level': 'medium', 'condition': 'Blood Pressure Disorder'},
    'respiratory': {'level': 'medium', 'condition': 'Respiratory Disorder'},
    'asthma': {'level': 'medium', 'condition': 'Asthma'},
    'infection': {'level': 'medium', 'condition': 'Infectious Disease'},
    'pneumonia': {'level': 'high', 'condition': 'Pneumonia'},
    'kidney': {'level': 'high', 'condition': 'Renal Disease'},
    'renal': {'level': 'high', 'condition': 'Renal Disease'},
    'liver': {'level': 'high', 'condition': 'Hepatic Disease'},
    'hepatic': {'level': 'high', 'condition': 'Hepatic Disease'},
    'fracture': {'level': 'medium', 'condition': 'Orthopedic Injury'},
    'covid': {'level': 'critical', 'condition': 'COVID-19 Infection'},
    'dementia': {'level': 'high', 'condition': 'Neurodegenerative Disease'},
    'alzheimer': {'level': 'high', 'condition': 'Alzheimer\'s Disease'},
    'parkinson': {'level': 'high', 'condition': 'Parkinson\'s Disease'},
}

PREVENTION_TIPS = {
    'low': [
        'Maintain a balanced diet rich in fruits and vegetables.',
        'Engage in regular physical activity (at least 30 minutes daily).',
        'Schedule annual health check-ups and screenings.',
        'Stay hydrated and maintain adequate sleep (7-8 hours).',
        'Practice stress management through meditation or yoga.',
    ],
    'medium': [
        'Schedule a follow-up appointment with your primary care physician within 2 weeks.',
        'Monitor your vital signs regularly (blood pressure, heart rate).',
        'Adopt a heart-healthy diet low in sodium and saturated fats.',
        'Begin a moderate exercise program as recommended by your doctor.',
        'Keep a symptom diary to track any changes in your condition.',
        'Review your current medications with your healthcare provider.',
    ],
    'high': [
        'Seek immediate consultation with a specialist within 1 week.',
        'Undergo recommended diagnostic tests and screenings promptly.',
        'Strictly adhere to prescribed medication regimens.',
        'Avoid strenuous physical activities without medical clearance.',
        'Monitor for warning signs and seek emergency care if symptoms worsen.',
        'Arrange for a family member or caregiver to assist with daily activities.',
        'Keep all medical appointments and follow-up visits.',
    ],
    'critical': [
        'Seek emergency medical attention immediately if symptoms worsen.',
        'Hospitalization may be required for close monitoring and treatment.',
        'Follow all instructions from your emergency care team strictly.',
        'Ensure 24/7 supervision by a caregiver or family member.',
        'Prepare advance medical directives and discuss with family.',
        'Keep emergency contact numbers readily accessible at all times.',
        'Do not delay any recommended medical procedures or interventions.',
        'Maintain a detailed record of all symptoms, medications, and vital signs.',
    ],
}

EXPLANATIONS = {
    'low': 'Based on the patient data, the overall risk level is LOW. The patient\'s age and current diagnosis indicate minimal immediate health concerns. Regular preventive care and healthy lifestyle choices should help maintain this low-risk status.',
    'medium': 'Based on the patient data, the overall risk level is MEDIUM. The patient\'s age combined with the current diagnosis suggests moderate health concerns that require attention. Early intervention and lifestyle modifications can help prevent progression to a higher risk category.',
    'high': 'Based on the patient data, the overall risk level is HIGH. Significant risk factors including age and diagnosis indicate a elevated risk of complications. Immediate medical attention and specialist consultation are strongly recommended.',
    'critical': 'Based on the patient data, the overall risk level is CRITICAL. The combination of patient factors indicates a severe health risk requiring emergency medical intervention. Immediate hospitalization and intensive care may be necessary.',
}

MEDICINE_SUGGESTIONS = {
    'Cardiovascular Disease': {
        'medicines': ['Aspirin', 'Atorvastatin', 'Metoprolol', 'Lisinopril', 'Clopidogrel'],
        'advice': 'Antihypertensives, statins, and antiplatelet therapy as prescribed. Monitor BP regularly.',
    },
    'Diabetes Mellitus': {
        'medicines': ['Metformin', 'Insulin', 'Glipizide', 'Sitagliptin', 'Empagliflozin'],
        'advice': 'Blood sugar monitoring, oral hypoglycemics or insulin therapy based on HbA1c levels.',
    },
    'Malignancy': {
        'medicines': [
            'Chemotherapy (Cisplatin, Paclitaxel, Doxorubicin)',
            'Immunotherapy (Pembrolizumab, Nivolumab)',
            'Targeted therapy (Imatinib, Trastuzumab)',
            'Pain management (Morphine, Fentanyl patch)',
            'Antiemetics (Ondansetron, Metoclopramide)',
            'Corticosteroids (Dexamethasone)',
            'Bisphosphonates (Zoledronic acid)',
            'Growth factors (Filgrastim, Erythropoietin)',
        ],
        'advice': 'Urgent oncology referral. Treatment depends on cancer type, stage, and genetic markers. Palliative care if advanced. Manage pain, nausea, and fatigue aggressively.',
    },
    'Neoplasm': {
        'medicines': [
            'Dexamethasone (cerebral edema)',
            'Mannitol (raised ICP)',
            'Levetiracetam (seizure prophylaxis)',
            'Ondansetron (nausea/vomiting)',
            'Pantoprazole (stress ulcer prophylaxis)',
            'Phenytoin (seizure control)',
            'Furosemide (diuresis)',
            'Enoxaparin (DVT prophylaxis)',
        ],
        'advice': 'Urgent neurosurgery consultation. CT/MRI brain immediately. Manage cerebral edema, seizures, and raised intracranial pressure. Monitor GCS closely.',
    },
    'Cerebrovascular Accident': {
        'medicines': ['Alteplase (tPA)', 'Aspirin', 'Clopidogrel', 'Atorvastatin', 'Amlodipine'],
        'advice': 'Emergency stroke protocol. Thrombolysis within window period. Rehabilitation therapy.',
    },
    'Hypertensive Disease': {
        'medicines': ['Amlodipine', 'Losartan', 'Hydrochlorothiazide', 'Enalapril', 'Atenolol'],
        'advice': 'Lifestyle modifications and antihypertensive therapy. Monitor BP twice daily.',
    },
    'Blood Pressure Disorder': {
        'medicines': ['Amlodipine', 'Losartan', 'Metoprolol'],
        'advice': 'Regular BP monitoring. Low-sodium diet and stress management.',
    },
    'Respiratory Disorder': {
        'medicines': ['Salbutamol inhaler', 'Fluticasone', 'Montelukast', 'Prednisolone', 'Oxygen therapy'],
        'advice': 'Pulmonary function tests. Bronchodilators and inhaled corticosteroids as needed.',
    },
    'Asthma': {
        'medicines': ['Salbutamol', 'Budesonide', 'Montelukast', 'Fluticasone/salmeterol', 'Prednisolone'],
        'advice': 'Step-up therapy based on symptom control. Avoid triggers and maintain peak flow diary.',
    },
    'Infectious Disease': {
        'medicines': ['Amoxicillin', 'Azithromycin', 'Ceftriaxone', 'Paracetamol', 'IV fluids'],
        'advice': 'Antibiotics based on culture sensitivity. Complete full course. Hydration and rest.',
    },
    'Pneumonia': {
        'medicines': ['Amoxicillin-clavulanate', 'Azithromycin', 'Ceftriaxone', 'Doxycycline', 'Oxygen therapy'],
        'advice': 'Chest X-ray and blood cultures. Antibiotics as per guidelines. Hospitalize if severe.',
    },
    'Renal Disease': {
        'medicines': ['Furosemide', 'Erythropoietin', 'Calcium carbonate', 'Sodium bicarbonate', 'LOSARTAN'],
        'advice': 'Nephrology referral. Monitor creatinine and electrolytes. Fluid restriction if needed.',
    },
    'Hepatic Disease': {
        'medicines': ['Lactulose', 'Spironolactone', 'Rifaximin', 'Vitamin K', 'Albumin'],
        'advice': 'Hepatology referral. Avoid alcohol and hepatotoxic drugs. Monitor LFTs and INR.',
    },
    'Orthopedic Injury': {
        'medicines': ['Ibuprofen', 'Paracetamol', 'Tramadol', 'Calcium supplements', 'Vitamin D'],
        'advice': 'Orthopedic consultation. RICE protocol (Rest, Ice, Compression, Elevation). Physiotherapy.',
    },
    'COVID-19 Infection': {
        'medicines': ['Remdesivir', 'Dexamethasone', 'Tocilizumab', 'Enoxaparin', 'Oxygen therapy'],
        'advice': 'Isolation protocol. Monitor SpO2. Antivirals and supportive care based on severity.',
    },
    'Neurodegenerative Disease': {
        'medicines': ['Donepezil', 'Memantine', 'Rivastigmine', 'Sertraline', 'Quetiapine'],
        'advice': 'Neurology referral. Symptomatic management. Cognitive therapy and caregiver support.',
    },
    "Alzheimer's Disease": {
        'medicines': ['Donepezil', 'Memantine', 'Rivastigmine', 'Galantamine', 'Sertraline'],
        'advice': 'Cognitive assessment scales. Cholinesterase inhibitors. Safety measures at home.',
    },
    "Parkinson's Disease": {
        'medicines': ['Levodopa/carbidopa', 'Pramipexole', 'Ropinirole', 'Entacapone', 'Benztropine'],
        'advice': 'Neurology follow-up. Motor symptom management. Physical and occupational therapy.',
    },
}

GENERAL_MEDICINES = {
    'headache': {
        'medicines': ['Paracetamol', 'Ibuprofen', 'Aspirin', 'Sumatriptan (for migraines)'],
        'advice': 'Rest in a quiet dark room. Stay hydrated. If severe or persistent, consult a neurologist.',
    },
    'migraine': {
        'medicines': ['Sumatriptan', 'Rizatriptan', 'Naproxen', 'Propranolol (preventive)', 'Amitriptyline'],
        'advice': 'Avoid triggers (bright lights, loud noises). Maintain regular sleep schedule.',
    },
    'back pain': {
        'medicines': ['Ibuprofen', 'Diclofenac gel', 'Paracetamol', 'Muscle relaxants (Thiocolchicoside)', 'Gabapentin (nerve pain)'],
        'advice': 'Apply hot/cold packs. Avoid heavy lifting. Physical therapy if chronic.',
    },
    'backpain': {
        'medicines': ['Ibuprofen', 'Diclofenac gel', 'Paracetamol', 'Muscle relaxants (Thiocolchicoside)', 'Gabapentin (nerve pain)'],
        'advice': 'Apply hot/cold packs. Avoid heavy lifting. Physical therapy if chronic.',
    },
    'fever': {
        'medicines': ['Paracetamol', 'Ibuprofen', 'Mefenamic acid', 'Sponging with lukewarm water'],
        'advice': 'Monitor temperature every 4 hours. Stay hydrated. If fever > 103°F or persists > 3 days, see a doctor.',
    },
    'cold': {
        'medicines': ['Cetirizine', 'Pseudoephedrine', 'Paracetamol', 'Vitamin C', 'Zinc lozenges'],
        'advice': 'Warm fluids, steam inhalation, and rest. Most colds resolve in 7-10 days.',
    },
    'cough': {
        'medicines': ['Dextromethorphan', 'Guaifenesin', 'Bromhexine', 'Salbutamol (if wheezing)', 'Honey with warm water'],
        'advice': 'If productive cough, use expectorants. If dry cough, use suppressants. See doctor if > 2 weeks.',
    },
    'nausea': {
        'medicines': ['Ondansetron', 'Metoclopramide', 'Domperidone', 'Ginger capsules'],
        'advice': 'Eat small frequent meals. Avoid spicy/greasy foods. Stay hydrated with ORS.',
    },
    'vomiting': {
        'medicines': ['Ondansetron', 'Metoclopramide', 'Domperidone', 'ORS solution', 'IV fluids (if severe)'],
        'advice': 'Prevent dehydration with ORS. Seek medical attention if persistent > 24 hours.',
    },
    'dizziness': {
        'medicines': ['Betahistine', 'Meclizine', 'Prochlorperazine', 'Ginger'],
        'advice': 'Sit or lie down immediately. Avoid sudden head movements. Check BP. Consult ENT if recurrent.',
    },
    'fatigue': {
        'medicines': ['Multivitamins', 'Iron supplements', 'Vitamin B12', 'Coenzyme Q10'],
        'advice': 'Ensure adequate sleep (7-8 hours). Balanced diet. Check Hb and thyroid function.',
    },
    'drowsiness': {
        'medicines': ['Modafinil (if prescribed)', 'Caffeine (temporary)', 'Vitamin B12'],
        'advice': 'Avoid driving. Check for medication side effects. Rule out sleep apnea or thyroid issues.',
    },
    'memory loss': {
        'medicines': ['Donepezil', 'Memantine', 'Ginkgo biloba', 'Vitamin E', 'Omega-3 supplements'],
        'advice': 'Neurology referral. Cognitive exercises. Rule out dementia or vitamin B12 deficiency.',
    },
    'memory problems': {
        'medicines': ['Donepezil', 'Memantine', 'Ginkgo biloba', 'Vitamin E', 'Omega-3 supplements'],
        'advice': 'Neurology referral. Cognitive exercises. Rule out dementia or vitamin B12 deficiency.',
    },
}

FOOD_RISK_RELATIONS = {
    'heart': {
        'risk_increasing': ['High sodium foods', 'Fried foods', 'Processed meats', 'Sugary beverages', 'Trans fats'],
        'risk_decreasing': ['Leafy greens', 'Omega-3 rich fish', 'Oats', 'Berries', 'Nuts', 'Olive oil'],
        'advice': 'A heart-healthy diet low in sodium and rich in omega-3 fatty acids is recommended. Avoid processed and fried foods.',
    },
    'diabetes': {
        'risk_increasing': ['Sugary foods', 'Refined carbohydrates', 'Sweetened beverages', 'White bread', 'Pastries'],
        'risk_decreasing': ['Whole grains', 'Fiber-rich vegetables', 'Lean proteins', 'Legumes', 'Cinnamon'],
        'advice': 'Monitor carbohydrate intake and choose low-glycemic foods. Include fiber-rich vegetables with every meal.',
    },
    'cancer': {
        'risk_increasing': ['Processed meats', 'Alcohol', 'Smoked foods', 'Fried foods', 'Artificial sweeteners'],
        'risk_decreasing': ['Cruciferous vegetables', 'Berries', 'Green tea', 'Turmeric', 'Garlic', 'Tomatoes'],
        'advice': 'An antioxidant-rich diet with plenty of fruits and vegetables may help support treatment and recovery.',
    },
    'default': {
        'risk_increasing': ['Processed foods', 'Sugary snacks', 'Excessive alcohol', 'High-fat fast food'],
        'risk_decreasing': ['Fresh fruits', 'Vegetables', 'Whole grains', 'Lean proteins', 'Water'],
        'advice': 'A balanced diet with plenty of whole foods and limited processed items is recommended for overall health.',
    },
}


def _compute_risk_score(age, diagnosis):
    diagnosis_lower = diagnosis.lower()
    score = 0.0
    risk_level = 'low'
    predicted_condition = 'General Health Monitoring'

    if age > 60:
        score += 40
    elif age > 45:
        score += 25
    elif age > 30:
        score += 10

    matched_keywords = []
    for keyword, info in RISK_KEYWORDS.items():
        if keyword in diagnosis_lower:
            keyword_scores = {'low': 5, 'medium': 20, 'high': 35, 'critical': 50}
            score += keyword_scores[info['level']]
            matched_keywords.append(info)

    if matched_keywords:
        highest = max(matched_keywords, key=lambda x: {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}[x['level']])
        predicted_condition = highest['condition']

    if len(diagnosis.split()) > 5:
        score += 5

    if score >= 70:
        risk_level = 'critical'
    elif score >= 45:
        risk_level = 'high'
    elif score >= 20:
        risk_level = 'medium'

    food_info = FOOD_RISK_RELATIONS['default']
    for keyword, info in RISK_KEYWORDS.items():
        if keyword in diagnosis_lower:
            if info['condition'].lower().split()[0] in ['cardiovascular', 'diabetes', 'malignancy']:
                key_map = {'cardiovascular': 'heart', 'diabetes': 'diabetes', 'malignancy': 'cancer'}
                mapped = key_map.get(info['condition'].lower().split()[0], 'default')
                if mapped in FOOD_RISK_RELATIONS:
                    food_info = FOOD_RISK_RELATIONS[mapped]
            break

    general_matches = {}
    for symptom, info in GENERAL_MEDICINES.items():
        if symptom in diagnosis_lower:
            general_matches[symptom] = info

    return risk_level, min(100.0, score), predicted_condition, food_info, general_matches


@admin_required
def risk_prediction(request):
    result = None
    form = RiskPredictionForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        patient_data = form.save(commit=False)

        risk_level, risk_score, predicted_condition, food_info, general_matches = _compute_risk_score(
            patient_data.age, patient_data.diagnosis
        )

        explanation = EXPLANATIONS.get(risk_level, EXPLANATIONS['low'])
        tips = PREVENTION_TIPS.get(risk_level, PREVENTION_TIPS['low'])

        patient_data.risk_level = risk_level
        patient_data.risk_score = risk_score
        patient_data.explanation = explanation
        patient_data.prevention_tips = '\n'.join(tips)
        patient_data.predicted_condition = predicted_condition

        food_history = request.POST.get('food_history', '')
        if food_history:
            patient_data.food_history_notes = food_history

        recommendations = [
            f'Risk Level: {risk_level.upper()}',
            f'Risk Score: {risk_score:.1f}%',
            f'Predicted Condition: {predicted_condition}',
            '',
            'Prevention Tips:',
        ]
        recommendations.extend(f'- {tip}' for tip in tips)
        recommendations.extend([
            '',
            'Dietary Recommendations:',
            f'- Foods to avoid: {", ".join(food_info["risk_increasing"])}',
            f'- Recommended foods: {", ".join(food_info["risk_decreasing"])}',
            f'- {food_info["advice"]}',
        ])
        patient_data.recommendations = '\n'.join(recommendations)

        patient_data.created_by = request.user
        patient_data.save()

        medicine_info = MEDICINE_SUGGESTIONS.get(predicted_condition, {
            'medicines': ['Consult physician for appropriate medication'],
            'advice': 'Clinical evaluation recommended for accurate prescription.',
        })

        general_medicines_list = []
        for symptom, info in general_matches.items():
            general_medicines_list.append({
                'symptom': symptom.replace('_', ' ').title(),
                'medicines': info['medicines'],
                'advice': info['advice'],
            })

        result = {
            'patient': patient_data,
            'risk_level': risk_level,
            'risk_score': risk_score,
            'explanation': explanation,
            'prevention_tips': tips,
            'food_info': food_info,
            'predicted_condition': predicted_condition,
            'medicine_info': medicine_info,
            'general_medicines': general_medicines_list,
        }

        messages.success(request, f'Risk prediction completed for {patient_data.patient_name}.')

    context = {
        'form': form,
        'result': result,
    }
    return render(request, 'predictions/risk_prediction.html', context)


@admin_required
def risk_prediction_detail(request, pk):
    prediction = get_object_or_404(RiskPrediction, pk=pk)
    context = {
        'prediction': prediction,
    }
    return render(request, 'predictions/risk_prediction_detail.html', context)


@admin_required
def risk_prediction_list(request):
    predictions = RiskPrediction.objects.select_related('created_by').order_by('-created_at')
    context = {
        'predictions': predictions,
    }
    return render(request, 'predictions/risk_prediction_list.html', context)


@admin_required
def model_performance(request):
    models = PredictionModel.objects.all().order_by('-trained_on')

    model_metrics = []
    for mdl in models:
        pred_count = Prediction.objects.filter(model_used__icontains=mdl.name).count()
        avg_confidence = Prediction.objects.filter(
            model_used__icontains=mdl.name
        ).aggregate(avg_conf=models.Avg('confidence_score'))['avg_conf'] or 0

        model_metrics.append({
            'model': mdl,
            'prediction_count': pred_count,
            'avg_confidence': round(avg_confidence, 2),
        })

    total_predictions = Prediction.objects.count()
    risk_predictions = RiskPrediction.objects.count()
    avg_risk_score = RiskPrediction.objects.aggregate(avg_score=models.Avg('risk_score'))['avg_score'] or 0

    risk_distribution = {
        'low': RiskPrediction.objects.filter(risk_level='low').count(),
        'medium': RiskPrediction.objects.filter(risk_level='medium').count(),
        'high': RiskPrediction.objects.filter(risk_level='high').count(),
        'critical': RiskPrediction.objects.filter(risk_level='critical').count(),
    }

    context = {
        'models': models,
        'model_metrics': model_metrics,
        'total_predictions': total_predictions,
        'risk_predictions': risk_predictions,
        'avg_risk_score': round(avg_risk_score, 2),
        'risk_distribution': risk_distribution,
    }
    return render(request, 'predictions/model_performance.html', context)
