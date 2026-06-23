# Hospital Digital Twin System - Setup Guide

## Prerequisites
- Python 3.10+
- MySQL 8.0+ (optional, SQLite used by default)
- pip package manager

## Quick Setup

### 1. Clone and Navigate
```bash
cd HospitalDigitalTwin
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Option A: SQLite (Default - Quick Start)
No configuration needed. The project uses SQLite by default.

#### Option B: MySQL (Production)
1. Create a MySQL database:
```sql
CREATE DATABASE hospital_digital_twin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
2. Update `HospitalDigitalTwin/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hospital_digital_twin',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```
3. Run the schema script: `mysql -u root -p hospital_digital_twin < database_schema.sql`

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```
Default test credentials: admin / admin123

### 7. Load Sample Data (Optional)
```bash
python scripts/sample_data.py
```

### 8. Start Development Server
```bash
python manage.py runserver
```

### 9. Access the Application
- Main App: http://127.0.0.1:8000/
- Admin Panel: http://127.0.0.1:8000/admin/
- Login: admin / admin123

## Project Structure
```
HospitalDigitalTwin/
├── accounts/          # Authentication and user roles
├── patients/          # Patient management
├── doctors/           # Doctor management
├── appointments/      # Appointment scheduling
├── beds/              # Bed management
├── inventory/         # Medicine inventory
├── analytics/         # Analytics and reports
├── predictions/       # ML prediction engine
│   └── ml_engine.py   # Machine learning models
├── reports/           # PDF and Excel reports
├── dashboard/         # Main dashboard views
├── templates/         # HTML templates
├── static/            # CSS, JS files
├── scripts/           # Utility scripts
├── sample_data/       # Sample CSV datasets
└── media/reports/     # Generated PDF reports
```

## Features Overview

### Authentication
- Admin, Doctor, Staff login with role-based redirects

### Patient Management
- CRUD operations, medical history, food history tracking

### Doctor Management
- Department allocation, availability schedules

### Appointments
- Booking, status tracking, history

### Bed Management
- ICU, General, Emergency beds with real-time occupancy

### Medicine Inventory
- Stock tracking, expiry monitoring, low-stock alerts

### Digital Twin Dashboard
- Real-time hospital overview with Charts.js visualizations

### Prediction Engine (ML)
- Bed occupancy prediction (7/15/30 days)
- Medicine shortage prediction
- Patient load forecasting
- **Risk Prediction** with:
  - Risk level assessment (low/medium/high/critical)
  - Detailed risk explanation
  - Prevention tips
  - Food & nutrition recommendations

### Analytics
- Daily/monthly admissions, department stats, bed utilization

### Reports
- PDF generation using ReportLab
- Excel export using OpenPyXL

## Default Login Credentials
- Admin: admin / admin123
- Create additional users via the Register page or admin panel
