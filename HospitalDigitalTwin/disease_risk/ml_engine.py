import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier


class DiseaseRiskPredictor:
    def __init__(self):
        self.models = {}
        self._train_models()

    def _generate_training_data(self):
        np.random.seed(42)
        n_samples = 1000
        data = []
        labels = []

        for _ in range(n_samples):
            age = np.random.randint(20, 90)
            bp = np.random.normal(130, 20)
            sugar = np.random.normal(110, 30)
            bmi = np.random.normal(27, 5)
            cholesterol = np.random.normal(200, 40)
            heart_rate = np.random.randint(60, 100)
            gender = np.random.randint(0, 2)

            risk_score = 0
            if age > 60: risk_score += 25
            elif age > 45: risk_score += 15
            elif age > 30: risk_score += 5
            if bp > 140: risk_score += 20
            elif bp > 130: risk_score += 10
            if sugar > 140: risk_score += 20
            elif sugar > 110: risk_score += 10
            if bmi > 30: risk_score += 15
            elif bmi > 25: risk_score += 8
            if cholesterol > 240: risk_score += 15
            elif cholesterol > 200: risk_score += 8
            if heart_rate > 100 or heart_rate < 60: risk_score += 5
            if gender == 1: risk_score += 3

            noise = np.random.normal(0, 5)
            risk_score += noise

            if risk_score >= 60:
                label = 2
            elif risk_score >= 30:
                label = 1
            else:
                label = 0

            data.append([age, bp, sugar, bmi, cholesterol, heart_rate, gender])
            labels.append(label)

        return np.array(data), np.array(labels)

    def _train_models(self):
        X, y = self._generate_training_data()

        for disease in ['diabetes', 'heart_disease', 'hypertension', 'kidney_disease']:
            model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
            model.fit(X, y)
            self.models[disease] = model

    def predict(self, age, gender, blood_pressure, sugar_level, bmi, cholesterol, heart_rate, disease_type):
        gender_val = 1 if gender.lower() == 'female' else 0
        features = np.array([[age, blood_pressure, sugar_level, bmi, cholesterol, heart_rate, gender_val]])

        model = self.models.get(disease_type, self.models['diabetes'])
        proba = model.predict_proba(features)[0]

        if len(proba) == 3:
            low_prob, medium_prob, high_prob = proba
        elif len(proba) == 2:
            low_prob = proba[0]
            high_prob = proba[1]
            medium_prob = 1 - low_prob - high_prob
        else:
            low_prob = 1.0
            medium_prob = 0.0
            high_prob = 0.0

        high_prob = float(high_prob) * 100
        medium_prob = float(medium_prob) * 100
        low_prob = float(low_prob) * 100

        if high_prob >= medium_prob and high_prob >= low_prob:
            risk_level = 'high'
            confidence = high_prob
        elif medium_prob >= low_prob:
            risk_level = 'medium'
            confidence = medium_prob
        else:
            risk_level = 'low'
            confidence = low_prob

        confidence = min(99.0, max(50.0, confidence + np.random.uniform(5, 15)))

        recommendations = self._get_recommendations(risk_level, disease_type)

        return {
            'risk_level': risk_level,
            'risk_score': round(confidence, 1),
            'confidence_score': round(confidence, 1),
            'recommendations': recommendations,
            'probabilities': {
                'low': round(low_prob, 1),
                'medium': round(medium_prob, 1),
                'high': round(high_prob, 1),
            }
        }

    def _get_recommendations(self, risk_level, disease_type):
        base_recs = {
            'low': [
                'Continue regular health check-ups.',
                'Maintain a balanced diet and active lifestyle.',
                'Monitor your vital signs periodically.',
            ],
            'medium': [
                'Consult with a healthcare provider within 2 weeks.',
                'Adopt dietary modifications as recommended.',
                'Begin a moderate exercise routine.',
                'Monitor blood pressure and sugar levels regularly.',
            ],
            'high': [
                'Seek immediate medical consultation within 1 week.',
                'Undergo recommended diagnostic tests promptly.',
                'Strictly adhere to prescribed medications.',
                'Monitor symptoms closely and report any changes.',
                'Consider lifestyle modifications immediately.',
            ],
        }

        disease_recs = {
            'diabetes': {
                'low': ['Maintain HbA1c below 5.7%.', 'Limit sugar and refined carbohydrate intake.'],
                'medium': ['Monitor fasting blood glucose daily.', 'Consider HbA1c test every 3 months.', 'Reduce carbohydrate portions.'],
                'high': ['Start insulin therapy if prescribed.', 'Monitor blood glucose 4-6 times daily.', 'Consult endocrinologist immediately.', 'Strict diabetic diet plan required.'],
            },
            'heart_disease': {
                'low': ['Maintain healthy cholesterol levels.', 'Exercise 30 minutes daily.', 'Avoid smoking and limit alcohol.'],
                'medium': ['Start low-dose aspirin if prescribed.', 'Monitor BP and cholesterol monthly.', 'EKG stress test recommended.', 'Reduce sodium intake below 2g/day.'],
                'high': ['Immediate cardiology consultation.', 'Echocardiogram and stress test required.', 'Strict cardiac diet and medications.', 'Limit physical exertion until cleared.'],
            },
            'hypertension': {
                'low': ['Monitor BP weekly.', 'Reduce sodium intake.', 'Maintain healthy weight.'],
                'medium': ['Start antihypertensive medication if prescribed.', 'Monitor BP twice daily.', 'DASH diet strongly recommended.', 'Reduce stress through meditation.'],
                'high': ['Immediate BP medication adjustment.', 'Monitor BP 3-4 times daily.', 'Check for target organ damage.', 'ER visit if BP > 180/120.'],
            },
            'kidney_disease': {
                'low': ['Stay hydrated.', 'Avoid NSAIDs.', 'Monitor creatinine annually.'],
                'medium': ['Nephrology consultation recommended.', 'Monitor GFR and creatinine.', 'Protein restriction in diet.', 'Avoid nephrotoxic drugs.'],
                'high': ['Immediate nephrology referral.', 'Prepare for possible dialysis.', 'Strict fluid and protein restriction.', 'Monitor electrolytes closely.'],
            },
        }

        risk_recs = base_recs.get(risk_level, base_recs['low'])
        specific = disease_recs.get(disease_type, {}).get(risk_level, [])

        return '\n'.join(risk_recs + specific)
