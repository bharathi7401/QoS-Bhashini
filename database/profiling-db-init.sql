-- Customer Profiling Database Initialization Script
-- Bhashini Business Intelligence System
-- 
-- This script creates the database schema for customer profiling, value estimation,
-- and recommendation tracking. It integrates with the existing tenant configuration
-- system and provides a foundation for business intelligence features.
--
-- Author: Bhashini BI Team
-- Date: 2024

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS bhashini_profiling;
USE bhashini_profiling;

-- Customer Profiles Table
-- Stores comprehensive customer information including sector, use cases, and business context
CREATE TABLE IF NOT EXISTS customer_profiles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL UNIQUE,
    organization_name VARCHAR(255) NOT NULL,
    sector ENUM('government', 'healthcare', 'education', 'private', 'ngo') NOT NULL,
    use_case_category VARCHAR(100) NOT NULL,
    specific_use_cases JSON,
    target_user_base INT NOT NULL,
    geographical_coverage JSON,
    languages_required JSON,
    business_objectives JSON,
    success_metrics JSON,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    industry VARCHAR(100),
    annual_revenue DECIMAL(15,2),
    employee_count INT,
    sla_tier ENUM('premium', 'standard', 'basic') NOT NULL,
    profile_status ENUM('active', 'inactive', 'pending', 'suspended') DEFAULT 'active',
    profile_created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    profile_updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for efficient querying
    INDEX idx_sector (sector),
    INDEX idx_use_case_category (use_case_category),
    INDEX idx_sla_tier (sla_tier),
    INDEX idx_profile_status (profile_status),
    INDEX idx_created_date (profile_created_date)
);

-- Value Estimates Table
-- Stores calculated business value metrics and impact analysis
CREATE TABLE IF NOT EXISTS value_estimates (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cost_savings DECIMAL(15,2),
    user_reach_impact INT,
    efficiency_gains DECIMAL(5,2), -- Percentage
    quality_improvements DECIMAL(5,2), -- Percentage
    total_value_score DECIMAL(5,2), -- 0-100 scale
    confidence_score DECIMAL(5,2), -- 0-100 scale
    roi_ratio DECIMAL(10,2),
    payback_period_months DECIMAL(5,2),
    calculation_methodology TEXT,
    qos_metrics_summary JSON,
    sector_analysis JSON,
    
    -- Foreign key constraint
    FOREIGN KEY (tenant_id) REFERENCES customer_profiles(tenant_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_calculation_date (calculation_date),
    INDEX idx_total_value_score (total_value_score)
);

-- Recommendations Table
-- Stores generated optimization recommendations and their status
CREATE TABLE IF NOT EXISTS recommendations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    recommendation_id VARCHAR(100) NOT NULL UNIQUE,
    tenant_id VARCHAR(50) NOT NULL,
    recommendation_type ENUM('performance', 'reliability', 'capacity', 'feature_adoption') NOT NULL,
    priority ENUM('critical', 'high', 'medium', 'low') NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    expected_impact ENUM('high', 'medium', 'low') NOT NULL,
    implementation_effort ENUM('high', 'medium', 'low') NOT NULL,
    business_value DECIMAL(5,2), -- 0-100 scale
    technical_details TEXT,
    sector_context TEXT,
    use_case_context TEXT,
    confidence_score DECIMAL(5,2), -- 0-100 scale
    status ENUM('new', 'in_progress', 'implemented', 'rejected', 'deferred') DEFAULT 'new',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    implemented_date TIMESTAMP NULL,
    
    -- Foreign key constraint
    FOREIGN KEY (tenant_id) REFERENCES customer_profiles(tenant_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_recommendation_type (recommendation_type),
    INDEX idx_priority (priority),
    INDEX idx_status (status),
    INDEX idx_created_date (created_date)
);

-- Profile History Table
-- Tracks changes to customer profiles for audit and compliance
CREATE TABLE IF NOT EXISTS profile_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    change_type ENUM('created', 'updated', 'status_changed', 'deleted') NOT NULL,
    field_name VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(100),
    change_reason TEXT,
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    FOREIGN KEY (tenant_id) REFERENCES customer_profiles(tenant_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_change_type (change_type),
    INDEX idx_change_timestamp (change_timestamp)
);

-- QoS Metrics Cache Table
-- Caches QoS metrics for faster value calculation and analysis
CREATE TABLE IF NOT EXISTS qos_metrics_cache (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    service_type ENUM('Translation', 'TTS', 'ASR') NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    metric_unit VARCHAR(50),
    timestamp TIMESTAMP NOT NULL,
    cache_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    FOREIGN KEY (tenant_id) REFERENCES customer_profiles(tenant_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_service_type (service_type),
    INDEX idx_metric_name (metric_name),
    INDEX idx_timestamp (timestamp),
    UNIQUE KEY unique_metric (tenant_id, service_type, metric_name, timestamp)
);

-- Sector KPI Templates Table
-- Stores sector-specific KPI configurations for dashboard generation
CREATE TABLE IF NOT EXISTS sector_kpi_templates (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sector VARCHAR(50) NOT NULL,
    kpi_category VARCHAR(100) NOT NULL,
    kpi_name VARCHAR(255) NOT NULL,
    kpi_description TEXT,
    metric_unit VARCHAR(50),
    target_value DECIMAL(15,4),
    critical_threshold DECIMAL(15,4),
    query_template TEXT,
    panel_type VARCHAR(50),
    refresh_interval VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_sector (sector),
    INDEX idx_kpi_category (kpi_category),
    INDEX idx_is_active (is_active)
);

-- Use Case Templates Table
-- Stores use case specific configurations and requirements
CREATE TABLE IF NOT EXISTS use_case_templates (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sector VARCHAR(50) NOT NULL,
    use_case_category VARCHAR(100) NOT NULL,
    use_case_name VARCHAR(255) NOT NULL,
    description TEXT,
    service_types JSON,
    languages JSON,
    technical_requirements JSON,
    success_metrics JSON,
    implementation_guidelines TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_sector (sector),
    INDEX idx_use_case_category (use_case_category),
    INDEX idx_is_active (is_active)
);

-- Insert initial sector KPI templates
INSERT INTO sector_kpi_templates (sector, kpi_category, kpi_name, kpi_description, metric_unit, target_value, critical_threshold, query_template, panel_type, refresh_interval) VALUES
-- Government Sector KPIs
('government', 'citizen_service_efficiency', 'Average Service Completion Time', 'Average time to complete citizen service requests', 'ms', 2000, 5000, 'from(bucket: "qos_metrics") |> range(start: v.timeRangeStart, stop: v.timeRangeStop) |> filter(fn: (r) => r["_measurement"] == "service_metrics" and r["tenant_id"] == "${tenant_id}" and r["service_type"] == "Translation") |> filter(fn: (r) => r["_field"] == "response_time_p95") |> mean()', 'stat', '1m'),

('government', 'citizen_service_efficiency', 'Citizen Satisfaction Score', 'Overall satisfaction rating from citizen feedback', 'score', 85, 70, 'from(bucket: "qos_metrics") |> range(start: v.timeRangeStart, stop: v.timeRangeStop) |> filter(fn: (r) => r["_measurement"] == "customer_satisfaction" and r["tenant_id"] == "${tenant_id}") |> filter(fn: (r) => r["_field"] == "satisfaction_score") |> mean()', 'gauge', '5m'),

('government', 'compliance_monitoring', 'Data Privacy Adherence', 'Compliance score for data privacy regulations', 'score', 95, 80, 'from(bucket: "qos_metrics") |> range(start: v.timeRangeStart, stop: v.timeRangeStop) |> filter(fn: (r) => r["_measurement"] == "compliance_metrics" and r["tenant_id"] == "${tenant_id}") |> filter(fn: (r) => r["_field"] == "privacy_compliance_score") |> mean()', 'stat', '1h'),

-- Healthcare Sector KPIs
('healthcare', 'patient_communication_quality', 'Translation Accuracy for Medical Terms', 'Accuracy score for medical terminology translations', 'score', 98, 95, 'from(bucket: "qos_metrics") |> range(start: v.timeRangeStart, stop: v.timeRangeStop) |> filter(fn: (r) => r["_measurement"] == "translation_quality" and r["tenant_id"] == "${tenant_id}" and r["service_type"] == "Translation") |> filter(fn: (r) => r["_field"] == "medical_accuracy_score") |> mean()', 'gauge', '1m'),

('healthcare', 'safety_monitoring', 'Critical Communication Delivery Success', 'Success rate for critical healthcare communications', 'percent', 99.9, 99.0, 'from(bucket: "qos_metrics") |> range(start: v.timeRangeStart, stop: v.timeRangeStop) |> filter(fn: (r) => r["_measurement"] == "communication_delivery" and r["tenant_id"] == "${tenant_id}") |> filter(fn: (r) => r["_field"] == "delivery_success_rate") |> mean()', 'stat', '1m'),

-- Education Sector KPIs
('education', 'content_localization', 'Curriculum Translation Coverage', 'Percentage of curriculum content available in local languages', 'percent', 90, 75, 'from(bucket: "qos_metrics") |> range(start: v.timeRangeStart, stop: v.timeRangeStop) |> filter(fn: (r) => r["_measurement"] == "content_coverage" and r["tenant_id"] == "${tenant_id}") |> filter(fn: (r) => r["_field"] == "translation_coverage_percent") |> mean()', 'gauge', '1h'),

('education', 'student_engagement', 'Learning Platform Usage Across Languages', 'Usage statistics across different language interfaces', 'users', 1000, 500, 'from(bucket: "qos_metrics") |> range(start: v.timeRangeStart, stop: v.timeRangeStop) |> filter(fn: (r) => r["_measurement"] == "platform_usage" and r["tenant_id"] == "${tenant_id}") |> filter(fn: (r) => r["_field"] == "active_users") |> sum()', 'stat', '5m');

-- Insert initial use case templates
INSERT INTO use_case_templates (sector, use_case_category, use_case_name, description, service_types, languages, technical_requirements, success_metrics, implementation_guidelines) VALUES
-- Government Use Cases
('government', 'citizen_services', 'Multilingual Government Portal', 'Government website with multilingual support for citizen services', '["Translation", "TTS", "ASR"]', '["Hindi", "English", "Regional Languages"]', '{"availability": 99.9, "response_time": 2000, "accuracy": 95, "security": "high"}', '["citizen_satisfaction", "service_completion_rate", "accessibility_score"]', 'Implement progressive web app with offline capabilities and accessibility features'),

('government', 'public_communication', 'Emergency Alert System', 'Multilingual emergency communication system for public safety', '["Translation", "TTS"]', '["Hindi", "English", "Local Languages"]', '{"availability": 99.99, "response_time": 1000, "reliability": "critical"}', '["alert_delivery_success", "response_time", "coverage_area"]', 'Ensure redundant systems and multiple delivery channels for critical communications'),

-- Healthcare Use Cases
('healthcare', 'patient_communication', 'Medical Record Translation', 'Translation services for patient medical records and documents', '["Translation"]', '["English", "Local Languages"]', '{"accuracy": 98, "security": "hipaa_compliant", "privacy": "high"}', '["translation_accuracy", "patient_satisfaction", "compliance_score"]', 'Implement secure translation workflow with audit trails and data encryption'),

('healthcare', 'telemedicine', 'Real-time Medical Interpretation', 'Live interpretation services for medical consultations', '["ASR", "Translation", "TTS"]', '["English", "Local Languages"]', '{"latency": 500, "accuracy": 95, "reliability": "high"}', '["interpretation_quality", "consultation_success", "patient_outcomes"]', 'Use low-latency streaming with fallback mechanisms for critical communications'),

-- Education Use Cases
('education', 'content_localization', 'Curriculum Translation', 'Localization of educational content and curriculum materials', '["Translation"]', '["English", "Local Languages"]', '{"quality": "high", "accessibility": "standards_compliant", "cost_efficiency": "medium"}', '["translation_quality", "student_comprehension", "accessibility_score"]', 'Implement quality assurance workflow with educator review and student feedback'),

('education', 'e_learning', 'Multilingual Learning Platform', 'E-learning platform with multilingual course delivery', '["Translation", "TTS", "ASR"]', '["English", "Local Languages"]', '{"availability": 99.5, "user_experience": "excellent", "scalability": "high"}', '["platform_usage", "learning_outcomes", "student_engagement"]', 'Design responsive interface with accessibility features and offline learning capabilities');

-- Insert sample customer profiles based on existing tenant configuration
-- These profiles are inferred from the existing tenant-config.yml data
INSERT INTO customer_profiles (tenant_id, organization_name, sector, use_case_category, specific_use_cases, target_user_base, geographical_coverage, languages_required, business_objectives, success_metrics, sla_tier, profile_status) VALUES
('gov-department-001', 'Ministry of Digital Services', 'government', 'citizen_services', '["government_portal", "document_translation", "citizen_feedback"]', 1000000, '["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata"]', '["Hindi", "English", "Marathi", "Tamil", "Bengali"]', '["improve_citizen_access", "reduce_processing_time", "increase_satisfaction"]', '["service_completion_rate", "citizen_satisfaction", "accessibility_score"]', 'premium', 'active'),

('healthcare-provider-001', 'City General Hospital', 'healthcare', 'patient_communication', '["medical_records", "appointment_scheduling", "patient_education"]', 50000, '["Mumbai", "Pune"]', '["English", "Marathi", "Hindi"]', '["improve_patient_communication", "reduce_errors", "increase_accessibility"]', '["translation_accuracy", "patient_satisfaction", "error_reduction"]', 'premium', 'active'),

('education-institute-001', 'National University', 'education', 'content_localization', '["curriculum_translation", "student_portal", "research_papers"]', 25000, '["Delhi", "NCR"]', '["English", "Hindi", "Sanskrit"]', '["improve_learning_access", "preserve_cultural_heritage", "increase_enrollment"]', '["translation_coverage", "student_engagement", "learning_outcomes"]', 'standard', 'active');

-- Create views for common queries
CREATE VIEW customer_profile_summary AS
SELECT 
    cp.tenant_id,
    cp.organization_name,
    cp.sector,
    cp.use_case_category,
    cp.target_user_base,
    cp.sla_tier,
    cp.profile_status,
    COUNT(ve.id) as value_estimates_count,
    COUNT(r.id) as recommendations_count,
    MAX(ve.calculation_date) as last_value_calculation,
    MAX(r.created_date) as last_recommendation_date
FROM customer_profiles cp
LEFT JOIN value_estimates ve ON cp.tenant_id = ve.tenant_id
LEFT JOIN recommendations r ON cp.tenant_id = r.tenant_id
GROUP BY cp.tenant_id, cp.organization_name, cp.sector, cp.use_case_category, cp.target_user_base, cp.sla_tier, cp.profile_status;

CREATE VIEW sector_performance_summary AS
SELECT 
    cp.sector,
    COUNT(cp.id) as customer_count,
    AVG(ve.total_value_score) as avg_value_score,
    AVG(ve.roi_ratio) as avg_roi_ratio,
    COUNT(r.id) as total_recommendations,
    SUM(CASE WHEN r.priority = 'critical' THEN 1 ELSE 0 END) as critical_recommendations
FROM customer_profiles cp
LEFT JOIN value_estimates ve ON cp.tenant_id = ve.tenant_id
LEFT JOIN recommendations r ON cp.tenant_id = r.tenant_id
GROUP BY cp.sector;

-- Create stored procedures for common operations
DELIMITER //

CREATE PROCEDURE GetCustomerRecommendations(IN p_tenant_id VARCHAR(50))
BEGIN
    SELECT 
        r.*,
        cp.organization_name,
        cp.sector,
        cp.use_case_category
    FROM recommendations r
    JOIN customer_profiles cp ON r.tenant_id = cp.tenant_id
    WHERE r.tenant_id = p_tenant_id
    ORDER BY r.priority ASC, r.business_value DESC;
END //

CREATE PROCEDURE GetSectorKPIs(IN p_sector VARCHAR(50))
BEGIN
    SELECT 
        kpi_category,
        kpi_name,
        kpi_description,
        target_value,
        critical_threshold,
        query_template
    FROM sector_kpi_templates
    WHERE sector = p_sector AND is_active = TRUE
    ORDER BY kpi_category, kpi_name;
END //

CREATE PROCEDURE UpdateCustomerProfile(
    IN p_tenant_id VARCHAR(50),
    IN p_field_name VARCHAR(100),
    IN p_new_value TEXT,
    IN p_changed_by VARCHAR(100),
    IN p_change_reason TEXT
)
BEGIN
    DECLARE v_old_value TEXT;
    
    -- Get old value
    SET v_old_value = (SELECT 
        CASE 
            WHEN p_field_name = 'organization_name' THEN organization_name
            WHEN p_field_name = 'sector' THEN sector
            WHEN p_field_name = 'use_case_category' THEN use_case_category
            WHEN p_field_name = 'target_user_base' THEN target_user_base
            WHEN p_field_name = 'sla_tier' THEN sla_tier
            WHEN p_field_name = 'profile_status' THEN profile_status
            ELSE NULL
        END
    FROM customer_profiles WHERE tenant_id = p_tenant_id);
    
    -- Update the profile
    UPDATE customer_profiles 
    SET 
        CASE 
            WHEN p_field_name = 'organization_name' THEN organization_name = p_new_value
            WHEN p_field_name = 'sector' THEN sector = p_new_value
            WHEN p_field_name = 'use_case_category' THEN use_case_category = p_new_value
            WHEN p_field_name = 'target_user_base' THEN target_user_base = CAST(p_new_value AS UNSIGNED)
            WHEN p_field_name = 'sla_tier' THEN sla_tier = p_new_value
            WHEN p_field_name = 'profile_status' THEN profile_status = p_new_value
        END,
        profile_updated_date = CURRENT_TIMESTAMP
    WHERE tenant_id = p_tenant_id;
    
    -- Log the change
    INSERT INTO profile_history (tenant_id, change_type, field_name, old_value, new_value, changed_by, change_reason)
    VALUES (p_tenant_id, 'updated', p_field_name, v_old_value, p_new_value, p_changed_by, p_change_reason);
END //

DELIMITER ;

-- Grant permissions (adjust as needed for your environment)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON bhashini_profiling.* TO 'bhashini_user'@'%';
-- GRANT EXECUTE ON PROCEDURE bhashini_profiling.* TO 'bhashini_user'@'%';

-- Insert sample data for testing
INSERT INTO value_estimates (tenant_id, cost_savings, user_reach_impact, efficiency_gains, quality_improvements, total_value_score, confidence_score, roi_ratio, payback_period_months, calculation_methodology) VALUES
('gov-department-001', 500000.00, 1000000, 40.5, 35.2, 85.7, 88.3, 3.2, 8.5, 'AI-powered value estimation with sector-specific multipliers'),
('healthcare-provider-001', 250000.00, 50000, 45.8, 42.1, 92.3, 91.7, 4.1, 6.2, 'Healthcare-specific value calculation with patient safety weighting'),
('education-institute-001', 150000.00, 25000, 38.2, 41.5, 78.9, 82.1, 2.8, 12.1, 'Education-focused value analysis with learning outcome metrics');

INSERT INTO recommendations (recommendation_id, tenant_id, recommendation_type, priority, title, description, expected_impact, implementation_effort, business_value, technical_details, sector_context, use_case_context, confidence_score) VALUES
('gov-department-001-perf-1', 'gov-department-001', 'performance', 'high', 'Optimize Response Time for Peak Hours', 'Implement caching and load balancing to handle peak citizen service demand', 'high', 'medium', 85.5, 'Add Redis cache layer, implement CDN, optimize database queries', 'Government sector requires high compliance and accessibility standards', 'Citizen services require high availability and multilingual support', 88.3),
('healthcare-provider-001-rel-1', 'healthcare-provider-001', 'reliability', 'critical', 'Improve Medical Translation Accuracy', 'Enhance translation quality for critical medical communications', 'high', 'medium', 92.1, 'Implement quality assurance workflow, add medical terminology validation', 'Healthcare sector prioritizes patient safety and accuracy', 'Healthcare communication needs high accuracy and reliability', 91.7),
('education-institute-001-cap-1', 'education-institute-001', 'capacity', 'medium', 'Scale Content Delivery Infrastructure', 'Add capacity for handling increased student load during peak periods', 'medium', 'low', 72.8, 'Increase ECS task count, add auto-scaling policies', 'Education sector focuses on content quality and accessibility', 'Educational content requires quality and accessibility', 82.1);

-- Create indexes for performance optimization
CREATE INDEX idx_customer_profiles_sector_use_case ON customer_profiles(sector, use_case_category);
CREATE INDEX idx_value_estimates_tenant_date ON value_estimates(tenant_id, calculation_date);
CREATE INDEX idx_recommendations_tenant_type ON recommendations(tenant_id, recommendation_type);
CREATE INDEX idx_qos_metrics_cache_tenant_service ON qos_metrics_cache(tenant_id, service_type);

-- Final verification
SELECT 'Database initialization completed successfully' as status;
SELECT COUNT(*) as customer_profiles_count FROM customer_profiles;
SELECT COUNT(*) as value_estimates_count FROM value_estimates;
SELECT COUNT(*) as recommendations_count FROM recommendations;
SELECT COUNT(*) as sector_kpi_templates_count FROM sector_kpi_templates;
SELECT COUNT(*) as use_case_templates_count FROM use_case_templates;
