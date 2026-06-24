import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from datetime import date, timedelta, datetime
import joblib
import os

class BedOccupancyPredictor:
    def __init__(self):
        self.model = LinearRegression()
        self.feature_columns = ['day_of_week', 'day_of_month', 'month', 'is_weekend']

    def prepare_features(self, dates):
        df = pd.DataFrame({'date': pd.to_datetime(dates)})
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        return df[self.feature_columns].values

    def train(self, historical_data):
        if len(historical_data) < 10:
            historical_data = self._generate_synthetic_data(90)
        df = pd.DataFrame(historical_data)
        X = self.prepare_features(df['date'])
        y = df['occupancy'].values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        return {
            'r2_score': round(r2_score(y_test, y_pred), 4),
            'mae': round(mean_absolute_error(y_test, y_pred), 2),
        }

    def predict(self, days=30):
        future_dates = [date.today() + timedelta(days=i) for i in range(1, days + 1)]
        X = self.prepare_features(future_dates)
        predictions = self.model.predict(X)
        return [
            {'date': d, 'predicted_occupancy': max(0, round(float(p)))}
            for d, p in zip(future_dates, predictions)
        ]

    def _generate_synthetic_data(self, days=90):
        np.random.seed(42)
        data = []
        base_occupancy = 200
        for i in range(days, 0, -1):
            d = date.today() - timedelta(days=i)
            weekday = d.weekday()
            weekly_pattern = 30 if weekday < 5 else -20
            noise = np.random.normal(0, 20)
            occupancy = base_occupancy + weekly_pattern + noise
            data.append({'date': d, 'occupancy': max(0, round(occupancy))})
        return data


class MedicineShortagePredictor:
    def predict_shortages(self, inventory_items, consumption_history):
        predictions = []
        for item in inventory_items:
            daily_consumption = self._estimate_consumption(item, consumption_history)
            if daily_consumption > 0:
                days_until_empty = item.quantity / daily_consumption
                shortage_date = date.today() + timedelta(days=int(days_until_empty))
            else:
                shortage_date = date.today() + timedelta(days=365)
            predictions.append({
                'medicine': item.medicine.name,
                'current_stock': item.quantity,
                'daily_consumption': round(daily_consumption, 2),
                'estimated_shortage_date': shortage_date,
                'risk_level': 'high' if days_until_empty < 30 else 'medium' if days_until_empty < 90 else 'low',
            })
        return predictions

    def _estimate_consumption(self, item, history):
        relevant = [h for h in history if h.get('medicine_id') == item.medicine_id]
        if len(relevant) >= 30:
            return sum(h['quantity'] for h in relevant[-30:]) / 30
        return 0


class RiskPredictor:
    RISK_KEYWORDS = {
        'heart': ('high', 'Cardiovascular Disease'), 'cardiac': ('high', 'Cardiovascular Disease'),
        'diabetes': ('high', 'Diabetes Mellitus'), 'cancer': ('critical', 'Malignancy'),
        'stroke': ('high', 'Cerebrovascular Accident'), 'hypertension': ('medium', 'Hypertension'),
        'infection': ('medium', 'Infectious Disease'), 'pneumonia': ('high', 'Pneumonia'),
        'kidney': ('high', 'Renal Disease'), 'liver': ('high', 'Hepatic Disease'),
        'fracture': ('medium', 'Orthopedic Injury'), 'asthma': ('medium', 'Asthma'),
        'covid': ('critical', 'COVID-19'), 'dementia': ('high', 'Neurodegenerative Disease'),
    }

    def predict_risk(self, age, diagnosis, food_history=None):
        score = 0.0
        if age > 60: score += 35
        elif age > 45: score += 20
        elif age > 30: score += 10

        diagnosis_lower = diagnosis.lower()
        matched = None
        for keyword, (level, condition) in self.RISK_KEYWORDS.items():
            if keyword in diagnosis_lower:
                level_scores = {'low': 5, 'medium': 20, 'high': 35, 'critical': 50}
                score += level_scores.get(level, 10)
                if matched is None or level_scores.get(level, 0) > level_scores.get(matched[0], 0):
                    matched = (level, condition)

        if matched:
            risk_level = matched[0]
            condition = matched[1]
        else:
            risk_level = 'low' if score < 20 else 'medium'
            condition = 'General Health Monitoring'

        if score >= 70: risk_level = 'critical'
        elif score >= 45: risk_level = 'high'
        elif score >= 20: risk_level = 'medium'

        return {
            'risk_level': risk_level,
            'risk_score': min(100, score),
            'predicted_condition': condition,
        }


def generate_prediction_summary(predictions):
    summary = {
        'total_predictions': len(predictions),
        'avg_confidence': 0,
        'by_type': {},
    }
    if not predictions:
        return summary
    confidences = [p.confidence_score for p in predictions if hasattr(p, 'confidence_score')]
    if confidences:
        summary['avg_confidence'] = round(sum(confidences) / len(confidences), 2)
    for p in predictions:
        ptype = p.prediction_type if hasattr(p, 'prediction_type') else 'unknown'
        if ptype not in summary['by_type']:
            summary['by_type'][ptype] = 0
        summary['by_type'][ptype] += 1
    return summary


def train_and_save_model(model, filename):
    model_path = os.path.join(os.path.dirname(__file__), '..', 'models', filename)
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    return model_path


def load_model(filename):
    model_path = os.path.join(os.path.dirname(__file__), '..', 'models', filename)
    return joblib.load(model_path)
