import os, sys, django
from datetime import datetime, timedelta, date
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HospitalDigitalTwin.settings')
django.setup()

from django.contrib.auth.models import User
from patients.models import Patient, MedicalHistory, FoodHistory
from appointments.models import Appointment
from beds.models import Ward, Bed
from inventory.models import MedicineCategory, Medicine, Inventory, StockAlert
from analytics.models import DailyAdmission
from predictions.models import PredictionModel, Prediction, RiskPrediction
from disease_risk.models import DiseaseRiskPrediction
from reports.models import Report
from analytics.models import MonthlyReport, DepartmentStat, BedUtilizationReport, MedicineConsumption

def create_sample_data():
    print("Creating sample data...")

    admin = User.objects.filter(username='admin').first()
    if not admin:
        admin = User.objects.create_superuser('admin', 'admin@hospital.com', 'admin123')

    first_names = ['Rajesh', 'Priya', 'Amit', 'Sunita', 'Vikram', 'Ananya', 'Deepak', 'Kavita',
                   'Suresh', 'Meera', 'Arun', 'Neha', 'Manoj', 'Pooja', 'Rahul', 'Divya',
                   'Sarah', 'Michael', 'Emily', 'James', 'Sophia', 'David', 'Anna', 'John',
                   'Maria', 'Robert', 'Jennifer', 'William', 'Amanda', 'Christopher']
    last_names = ['Sharma', 'Patel', 'Singh', 'Verma', 'Gupta', 'Kumar', 'Joshi', 'Reddy',
                  'Johnson', 'Chen', 'Rodriguez', 'Williams', 'Taylor', 'Brown', 'Lee', 'Smith']

    patients_list = []
    for i in range(1, 51):
        pid = f"PAT-{i:04d}"
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        gender = 'M' if random.random() > 0.5 else 'F'
        dob = date.today() - timedelta(days=random.randint(365*5, 365*80))
        status = random.choice(['admitted', 'discharged', 'outpatient', 'emergency'])
        adm = date.today() - timedelta(days=random.randint(0, 30)) if status == 'admitted' else None
        patient, _ = Patient.objects.get_or_create(
            patient_id=pid,
            defaults={
                'first_name': fn, 'last_name': ln, 'date_of_birth': dob,
                'gender': gender, 'blood_group': random.choice(['A+', 'B+', 'O+', 'AB+', 'A-']),
                'phone': f'+91-{random.randint(9000000000, 9999999999)}',
                'email': f'{fn.lower()}.{ln.lower()}@email.com',
                'address': f'{random.randint(1, 999)} Main Street, City',
                'emergency_contact': f'+91-{random.randint(9000000000, 9999999999)}',
                'emergency_relation': random.choice(['Spouse', 'Parent', 'Sibling', 'Child']),
                'status': status, 'admission_date': adm,
            }
        )
        patients_list.append(patient)
    print(f"Created {len(patients_list)} patients")

    for i, p in enumerate(patients_list[:20]):
        MedicalHistory.objects.get_or_create(
            patient=p,
            defaults={
                'diagnosis': random.choice(['Hypertension', 'Diabetes Type 2', 'Asthma', 'Fracture', 'Pneumonia', 'Chest Pain']),
                'treatment': random.choice(['Medication', 'Surgery', 'Therapy', 'Observation']),
                'notes': f'Routine follow-up for {p.first_name}',
                'created_by': admin,
            }
        )
    print("Created medical histories")

    wards_data = [
        ('Ward A', 1, 'General Medicine Ward'), ('Ward B', 2, 'Surgery Ward'),
        ('Ward C', 3, 'Cardiology Ward'), ('Ward D', 4, 'Neurology Ward'),
        ('ICU', 2, 'Intensive Care Unit'), ('Emergency Wing', 0, 'Emergency Services'),
    ]
    wards = []
    for name, floor, desc in wards_data:
        w, _ = Ward.objects.get_or_create(name=name, floor=floor, defaults={'description': desc})
        wards.append(w)

    bed_types = ['general']*5 + ['icu']*3 + ['emergency']*2
    for i in range(1, 61):
        bn = f"BED-{i:03d}"
        ward = random.choice(wards)
        bt = random.choice(bed_types)
        status = random.choice(['available', 'occupied', 'available', 'available', 'occupied', 'maintenance'])
        patient = random.choice(patients_list) if status == 'occupied' else None
        Bed.objects.get_or_create(
            bed_number=bn,
            defaults={
                'ward': ward, 'bed_type': bt, 'status': status,
                'patient': patient,
                'assigned_date': date.today() - timedelta(days=random.randint(1, 10)) if patient else None,
            }
        )
    print("Created 60 beds")

    cat_names = ['Antibiotics', 'Pain Management', 'Cardiovascular', 'Diabetes Care',
                 'Respiratory', 'Gastrointestinal', 'Vitamins', 'Emergency Drugs']
    categories = []
    for cn in cat_names:
        c, _ = MedicineCategory.objects.get_or_create(name=cn, defaults={'description': f'{cn} category'})
        categories.append(c)

    medicine_data = [
        ('MED-001', 'Amoxicillin', 'Antibiotics', 'tablet', '500mg', 'Cipla'),
        ('MED-002', 'Paracetamol', 'Pain Management', 'tablet', '500mg', 'Sun Pharma'),
        ('MED-003', 'Metformin', 'Diabetes Care', 'tablet', '850mg', 'Dr Reddys'),
        ('MED-004', 'Atorvastatin', 'Cardiovascular', 'tablet', '10mg', 'AstraZeneca'),
        ('MED-005', 'Omeprazole', 'Gastrointestinal', 'capsule', '20mg', 'GSK'),
        ('MED-006', 'Salbutamol', 'Respiratory', 'inhaler', '100mcg', 'Cipla'),
        ('MED-007', 'Vitamin D3', 'Vitamins', 'capsule', '60K IU', 'Abbott'),
        ('MED-008', 'Aspirin', 'Pain Management', 'tablet', '75mg', 'Bayer'),
        ('MED-009', 'Insulin', 'Diabetes Care', 'injection', '100IU/ml', 'Novo Nordisk'),
        ('MED-010', 'Amiodarone', 'Cardiovascular', 'tablet', '200mg', 'Sanofi'),
    ]

    for mid, name, cat_name, form, strength, mfr in medicine_data:
        cat = next((c for c in categories if c.name == cat_name), categories[0])
        medicine, _ = Medicine.objects.get_or_create(
            medicine_id=mid,
            defaults={
                'name': name, 'generic_name': name, 'category': cat,
                'dosage_form': form, 'strength': strength, 'manufacturer': mfr,
                'unit_price': round(random.uniform(10, 500), 2),
            }
        )
        for batch in range(1, 4):
            qty = random.choice([5, 15, 25, 50, 100, 200])
            expiry = date.today() + timedelta(days=random.randint(-30, 365))
            inv, _ = Inventory.objects.get_or_create(
                medicine=medicine,
                batch_number=f'{mid}-B{batch:03d}',
                defaults={
                    'quantity': qty, 'expiry_date': expiry,
                    'purchase_price': round(random.uniform(5, 300), 2),
                    'selling_price': round(random.uniform(10, 500), 2),
                }
            )
            if qty <= 10:
                StockAlert.objects.get_or_create(
                    inventory_item=inv,
                    defaults={
                        'alert_type': 'low_stock',
                        'message': f'Low stock: {name} batch {inv.batch_number} has only {qty} units remaining',
                        'status': 'active',
                    }
                )
    print("Created medicines and inventory")

    doctor_names_pool = ['Dr. Sharma', 'Dr. Patel', 'Dr. Verma', 'Dr. Gupta',
                         'Dr. Johnson', 'Dr. Chen', 'Dr. Taylor', 'Dr. Brown']
    for i in range(40):
        apt_date = date.today() + timedelta(days=random.randint(-15, 30))
        apt_time = f"{random.randint(9, 16)}:{random.choice(['00','30'])}:00"
        patient = random.choice(patients_list)
        Appointment.objects.get_or_create(
            appointment_id=f"APT-{apt_date.strftime('%Y%m%d')}-{i+1:04d}",
            defaults={
                'patient': patient,
                'doctor_name': random.choice(doctor_names_pool),
                'doctor_specialization': random.choice(['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'General']),
                'appointment_date': apt_date,
                'appointment_time': datetime.strptime(apt_time, '%H:%M:%S').time(),
                'reason': random.choice(['Routine checkup', 'Follow-up', 'Consultation', 'Emergency']),
                'status': random.choice(['scheduled', 'completed', 'cancelled', 'scheduled', 'scheduled']),
                'created_by': admin,
            }
        )
    print("Created 40 appointments")

    for i in range(90):
        d = date.today() - timedelta(days=i)
        DailyAdmission.objects.get_or_create(
            date=d,
            defaults={
                'total_admissions': random.randint(5, 25),
                'total_discharges': random.randint(3, 20),
                'emergency_cases': random.randint(1, 10),
                'outpatient_visits': random.randint(20, 80),
            }
        )
    print("Created 90 days of admission data")

    for name, mtype, acc in [
        ('Bed Occupancy Predictor', 'LinearRegression', 85.5),
        ('Risk Assessment Model', 'DecisionTree', 78.3),
    ]:
        PredictionModel.objects.get_or_create(
            name=name,
            defaults={
                'model_type': mtype, 'accuracy': acc,
                'trained_on': datetime.now(), 'is_active': True,
            }
        )
    print("Created ML models")

    pred_types = ['bed_occupancy', 'patient_load', 'medicine_shortage']
    for pt in pred_types:
        for days_ahead in [7, 15, 30]:
            fd = date.today() + timedelta(days=days_ahead)
            Prediction.objects.get_or_create(
                prediction_type=pt,
                predicted_date=fd,
                defaults={
                    'predicted_value': round(random.uniform(50, 300), 1),
                    'confidence_score': round(random.uniform(70, 96), 1),
                    'model_used': 'LinearRegression',
                    'features_used': 'historical_data',
                }
            )
    print("Created prediction records")

    diseases = ['Diabetes', 'Heart Disease', 'Hypertension', 'Kidney Disease']
    symptoms_map = {
        'Diabetes': 'Frequent urination, excessive thirst, blurred vision',
        'Heart Disease': 'Chest pain, shortness of breath, fatigue',
        'Hypertension': 'Headaches, dizziness, nosebleeds',
        'Kidney Disease': 'Swelling, fatigue, changes in urination',
    }
    for i in range(30):
        p = random.choice(patients_list)
        disease = random.choice(diseases)
        age = random.randint(25, 85)
        gender = 'male' if p.gender == 'M' else 'female'
        bp = random.randint(110, 180)
        sugar = random.randint(80, 200)
        bmi = round(random.uniform(18, 40), 1)
        chol = random.randint(150, 280)
        hr = random.randint(60, 110)

        risk_score = 0
        if age > 60: risk_score += 25
        elif age > 45: risk_score += 15
        if bp > 140: risk_score += 20
        elif bp > 130: risk_score += 10
        if sugar > 140: risk_score += 20
        elif sugar > 110: risk_score += 10
        if bmi > 30: risk_score += 15
        elif bmi > 25: risk_score += 8
        if chol > 240: risk_score += 15
        elif chol > 200: risk_score += 8
        if hr > 100 or hr < 60: risk_score += 5

        if risk_score >= 55: rl = 'high'
        elif risk_score >= 30: rl = 'medium'
        else: rl = 'low'

        DiseaseRiskPrediction.objects.create(
            patient_name=f"{p.first_name} {p.last_name}",
            age=age, gender=gender,
            blood_pressure=float(bp), sugar_level=float(sugar),
            bmi=bmi, cholesterol=float(chol), heart_rate=hr,
            disease_type=disease.lower().replace(' ', '_'),
            risk_level=rl,
            risk_score=min(100, risk_score),
            confidence_score=round(random.uniform(75, 98), 1),
            recommendations=f'Risk assessment completed. Patient shows {rl} risk for {disease}.',
            created_by=admin,
        )
    print("Created 30 disease risk predictions")

    for i in range(20):
        p = random.choice(patients_list)
        levels = ['low', 'medium', 'high', 'critical']
        weights = [0.3, 0.4, 0.2, 0.1]
        rl = random.choices(levels, weights=weights, k=1)[0]
        RiskPrediction.objects.create(
            patient_id=p.patient_id,
            patient_name=f"{p.first_name} {p.last_name}",
            age=random.randint(25, 85),
            gender=random.choice(['Male', 'Female']),
            diagnosis=random.choice(list(symptoms_map.values())),
            risk_level=rl,
            risk_score=random.uniform(20, 95),
            explanation=f'Risk assessment shows {rl} risk level.',
            prevention_tips='Maintain regular health check-ups.',
            predicted_condition=random.choice(['Diabetes', 'Hypertension', 'Cardiovascular Disease']),
            recommendations='Follow prescribed treatment plan.',
            created_by=admin,
        )
    print("Created 20 risk predictions")

    for rt, title in [
        ('admission', 'Monthly Admission Report'),
        ('inventory', 'Quarterly Inventory Stock Report'),
        ('prediction', 'Prediction Accuracy Analysis'),
        ('disease_risk', 'Disease Risk Assessment Summary'),
        ('patient', 'Patient Census Report'),
        ('bed_utilization', 'Bed Utilization Monthly Report'),
        ('analytics', 'Hospital Analytics Overview'),
    ]:
        Report.objects.get_or_create(
            report_id=f"RPT-{rt[:3].upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            defaults={
                'report_type': rt, 'title': title,
                'description': f'Auto-generated {title.lower()} covering hospital operations.',
                'generated_by': admin, 'format': 'pdf',
                'date_range_start': date.today() - timedelta(days=30),
                'date_range_end': date.today(),
            }
        )
    print("Created 7 report records")

    for m in range(1, 7):
        month_date = date(2026, m, 1)
        MonthlyReport.objects.get_or_create(
            month=m, year=2026,
            defaults={
                'total_patients': random.randint(100, 500),
                'total_admissions': random.randint(50, 200),
                'total_discharges': random.randint(40, 180),
                'total_appointments': random.randint(200, 600),
                'bed_utilization_rate': round(random.uniform(55, 95), 1),
            }
        )
    print("Created 6 monthly reports")

    dept_names = ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Emergency', 'Oncology', 'Gynecology', 'Radiology']
    for dn in dept_names:
        for day_offset in range(0, 14):
            d = date.today() - timedelta(days=day_offset)
            DepartmentStat.objects.get_or_create(
                department_name=dn, date=d,
                defaults={
                    'patient_count': random.randint(5, 40),
                    'appointment_count': random.randint(3, 25),
                    'bed_utilization': round(random.uniform(40, 98), 1),
                }
            )
    print("Created department stats")

    for i in range(14):
        d = date.today() - timedelta(days=i)
        total = 60
        occupied = random.randint(20, 55)
        BedUtilizationReport.objects.get_or_create(
            date=d,
            defaults={
                'icu_occupied': random.randint(2, 10),
                'general_occupied': random.randint(10, 35),
                'emergency_occupied': random.randint(1, 8),
                'total_beds': total,
                'occupied_beds': occupied,
                'utilization_rate': round(occupied / total * 100, 1),
            }
        )
    print("Created 14 bed utilization reports")

    medicine_names = ['Amoxicillin', 'Paracetamol', 'Metformin', 'Atorvastatin', 'Omeprazole', 'Salbutamol']
    for mn in medicine_names:
        for m in [4, 5, 6]:
            MedicineConsumption.objects.get_or_create(
                medicine_name=mn, month=m, year=2026,
                defaults={
                    'quantity_consumed': random.randint(50, 500),
                    'total_cost': round(random.uniform(500, 5000), 2),
                }
            )
    print("Created medicine consumption records")

    print("\n=== Sample Data Creation Complete! ===")
    print(f"  Patients: {Patient.objects.count()}")
    print(f"  Beds: {Bed.objects.count()}")
    print(f"  Medicines: {Medicine.objects.count()}")
    print(f"  Appointments: {Appointment.objects.count()}")
    print(f"  Daily Records: {DailyAdmission.objects.count()}")
    print(f"  Disease Risk Predictions: {DiseaseRiskPrediction.objects.count()}")
    print(f"  Risk Predictions: {RiskPrediction.objects.count()}")
    print(f"  Predictions: {Prediction.objects.count()}")
    print(f"  ML Models: {PredictionModel.objects.count()}")
    print(f"  Reports: {Report.objects.count()}")
    print(f"  Monthly Reports: {MonthlyReport.objects.count()}")
    print(f"  Department Stats: {DepartmentStat.objects.count()}")
    print(f"  Bed Utilization Reports: {BedUtilizationReport.objects.count()}")
    print(f"  Medicine Consumption: {MedicineConsumption.objects.count()}")

if __name__ == '__main__':
    create_sample_data()
