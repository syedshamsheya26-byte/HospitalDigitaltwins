-- Hospital Digital Twin System - MySQL Database Schema
-- Run this script to create the MySQL database

CREATE DATABASE IF NOT EXISTS hospital_digital_twin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hospital_digital_twin;

-- Users and Authentication
CREATE TABLE auth_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME(6) NULL,
    is_superuser TINYINT(1) NOT NULL DEFAULT 0,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff TINYINT(1) NOT NULL DEFAULT 0,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    date_joined DATETIME(6) NOT NULL
);

-- User Roles
CREATE TABLE accounts_userrole (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    role VARCHAR(20) NOT NULL,
    phone VARCHAR(15) DEFAULT '',
    address TEXT,
    created_at DATETIME(6) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- Login History
CREATE TABLE accounts_loginhistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    login_time DATETIME(6) NOT NULL,
    ip_address VARCHAR(39) NULL,
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- Patients
CREATE TABLE patients_patient (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(1) NOT NULL,
    blood_group VARCHAR(3) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(254) DEFAULT '',
    address TEXT NOT NULL,
    emergency_contact VARCHAR(15) NOT NULL,
    emergency_relation VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'outpatient',
    admission_date DATETIME(6) NULL,
    discharge_date DATETIME(6) NULL,
    created_by_id INT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    FOREIGN KEY (created_by_id) REFERENCES auth_user(id) ON DELETE SET NULL
);

-- Medical History
CREATE TABLE patients_medicalhistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    diagnosis TEXT NOT NULL,
    treatment TEXT NOT NULL,
    prescription TEXT,
    notes TEXT,
    record_date DATETIME(6) NOT NULL,
    created_by_id INT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients_patient(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by_id) REFERENCES auth_user(id) ON DELETE SET NULL
);

-- Food History
CREATE TABLE patients_foodhistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    food_item VARCHAR(200) NOT NULL,
    quantity VARCHAR(100) NOT NULL,
    meal_type VARCHAR(50) NOT NULL,
    consumed_at DATETIME(6) NOT NULL,
    notes TEXT,
    recorded_by_id INT NULL,
    created_at DATETIME(6) NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients_patient(id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by_id) REFERENCES auth_user(id) ON DELETE SET NULL
);

-- Appointments
CREATE TABLE appointments_appointment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id VARCHAR(20) NOT NULL UNIQUE,
    patient_id INT NOT NULL,
    doctor_name VARCHAR(200) DEFAULT '',
    doctor_specialization VARCHAR(200) DEFAULT '',
    appointment_date DATE NOT NULL,
    appointment_time TIME(6) NOT NULL,
    end_time TIME(6) NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    notes TEXT,
    created_by_id INT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients_patient(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by_id) REFERENCES auth_user(id) ON DELETE SET NULL
);

-- Wards
CREATE TABLE beds_ward (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    floor INT NOT NULL,
    description TEXT
);

-- Beds
CREATE TABLE beds_bed (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bed_number VARCHAR(20) NOT NULL UNIQUE,
    ward_id INT NULL,
    bed_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'available',
    patient_id INT NULL,
    assigned_date DATETIME(6) NULL,
    discharge_date DATETIME(6) NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    FOREIGN KEY (ward_id) REFERENCES beds_ward(id) ON DELETE SET NULL,
    FOREIGN KEY (patient_id) REFERENCES patients_patient(id) ON DELETE SET NULL
);

-- Medicine Categories
CREATE TABLE inventory_medicinecategory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- Medicines
CREATE TABLE inventory_medicine (
    id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_id VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    generic_name VARCHAR(200) DEFAULT '',
    category_id INT NULL,
    dosage_form VARCHAR(20) NOT NULL,
    strength VARCHAR(100) DEFAULT '',
    manufacturer VARCHAR(200) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    FOREIGN KEY (category_id) REFERENCES inventory_medicinecategory(id) ON DELETE SET NULL
);

-- Inventory
CREATE TABLE inventory_inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_id INT NOT NULL,
    batch_number VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    unit VARCHAR(20) DEFAULT 'units',
    expiry_date DATE NOT NULL,
    manufacturing_date DATE NULL,
    purchase_price DECIMAL(10,2) DEFAULT 0,
    selling_price DECIMAL(10,2) DEFAULT 0,
    created_by_id INT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    FOREIGN KEY (medicine_id) REFERENCES inventory_medicine(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by_id) REFERENCES auth_user(id) ON DELETE SET NULL
);

-- Stock Alerts
CREATE TABLE inventory_stockalert (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inventory_item_id INT NOT NULL,
    alert_type VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at DATETIME(6) NOT NULL,
    resolved_at DATETIME(6) NULL,
    FOREIGN KEY (inventory_item_id) REFERENCES inventory_inventory(id) ON DELETE CASCADE
);

-- Predictions
CREATE TABLE predictions_prediction (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prediction_type VARCHAR(50) NOT NULL,
    department_name VARCHAR(100) DEFAULT '',
    predicted_date DATE NOT NULL,
    predicted_value DOUBLE NOT NULL,
    confidence_score DOUBLE NOT NULL,
    actual_value DOUBLE NULL,
    features_used TEXT,
    model_used VARCHAR(100) DEFAULT '',
    created_at DATETIME(6) NOT NULL
);

-- Risk Predictions
CREATE TABLE predictions_riskprediction (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    patient_name VARCHAR(200) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(10) NOT NULL,
    diagnosis TEXT NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    risk_score DOUBLE NOT NULL,
    explanation TEXT NOT NULL,
    prevention_tips TEXT NOT NULL,
    food_history_notes TEXT,
    predicted_condition VARCHAR(200) NOT NULL,
    recommendations TEXT NOT NULL,
    created_by_id INT NULL,
    created_at DATETIME(6) NOT NULL,
    FOREIGN KEY (created_by_id) REFERENCES auth_user(id) ON DELETE SET NULL
);

-- Prediction Models
CREATE TABLE predictions_predictionmodel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    accuracy DOUBLE NOT NULL,
    trained_on DATETIME(6) NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 0,
    model_path VARCHAR(255) DEFAULT '',
    created_at DATETIME(6) NOT NULL
);

-- Disease Risk Predictions
CREATE TABLE disease_risk_diseaseriskprediction (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_name VARCHAR(200) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(10) NOT NULL,
    blood_pressure DOUBLE NOT NULL,
    sugar_level DOUBLE NOT NULL,
    bmi DOUBLE NOT NULL,
    cholesterol DOUBLE NOT NULL,
    heart_rate INT NOT NULL,
    disease_type VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    risk_score DOUBLE NOT NULL,
    confidence_score DOUBLE NOT NULL,
    recommendations TEXT,
    created_by_id INT NULL,
    created_at DATETIME(6) NOT NULL,
    FOREIGN KEY (created_by_id) REFERENCES auth_user(id) ON DELETE SET NULL
);

-- Analytics: Daily Admissions
CREATE TABLE analytics_dailyadmission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_admissions INT NOT NULL DEFAULT 0,
    total_discharges INT NOT NULL DEFAULT 0,
    emergency_cases INT NOT NULL DEFAULT 0,
    outpatient_visits INT NOT NULL DEFAULT 0
);

-- Analytics: Monthly Reports
CREATE TABLE analytics_monthlyreport (
    id INT AUTO_INCREMENT PRIMARY KEY,
    month INT NOT NULL,
    year INT NOT NULL,
    total_patients INT DEFAULT 0,
    total_admissions INT DEFAULT 0,
    total_discharges INT DEFAULT 0,
    total_appointments INT DEFAULT 0,
    bed_utilization_rate DOUBLE DEFAULT 0,
    created_at DATETIME(6) NOT NULL
);

-- Analytics: Department Stats
CREATE TABLE analytics_departmentstat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    patient_count INT DEFAULT 0,
    appointment_count INT DEFAULT 0,
    bed_utilization DOUBLE DEFAULT 0
);

-- Analytics: Bed Utilization
CREATE TABLE analytics_bedutilizationreport (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    icu_occupied INT DEFAULT 0,
    general_occupied INT DEFAULT 0,
    emergency_occupied INT DEFAULT 0,
    total_beds INT DEFAULT 0,
    occupied_beds INT DEFAULT 0,
    utilization_rate DOUBLE DEFAULT 0
);

-- Analytics: Medicine Consumption
CREATE TABLE analytics_medicineconsumption (
    id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_name VARCHAR(200) NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    quantity_consumed INT DEFAULT 0,
    total_cost DECIMAL(12,2) DEFAULT 0
);

-- Reports
CREATE TABLE reports_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_id VARCHAR(20) NOT NULL UNIQUE,
    report_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    generated_by_id INT NULL,
    file_path VARCHAR(500) DEFAULT '',
    format VARCHAR(10) DEFAULT 'pdf',
    date_range_start DATE NULL,
    date_range_end DATE NULL,
    created_at DATETIME(6) NOT NULL,
    FOREIGN KEY (generated_by_id) REFERENCES auth_user(id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX idx_patient_status ON patients_patient(status);
CREATE INDEX idx_appointment_date ON appointments_appointment(appointment_date);
CREATE INDEX idx_appointment_status ON appointments_appointment(status);
CREATE INDEX idx_bed_status ON beds_bed(status);
CREATE INDEX idx_bed_type ON beds_bed(bed_type);
CREATE INDEX idx_inventory_expiry ON inventory_inventory(expiry_date);
CREATE INDEX idx_prediction_date ON predictions_prediction(predicted_date);
CREATE INDEX idx_prediction_type ON predictions_prediction(prediction_type);
CREATE INDEX idx_risk_level ON predictions_riskprediction(risk_level);
CREATE INDEX idx_disease_risk_level ON disease_risk_diseaseriskprediction(risk_level);
CREATE INDEX idx_disease_risk_type ON disease_risk_diseaseriskprediction(disease_type);
CREATE INDEX idx_daily_admission_date ON analytics_dailyadmission(date);
