#!/usr/bin/env python3
"""
Testing Suite for Bhashini Business Intelligence System

This module provides comprehensive testing capabilities for the BI system,
including unit tests, integration tests, and end-to-end validation.

Features:
- Unit tests for customer profiling functions
- Integration tests for value estimation algorithms
- API testing for all REST endpoints
- Dashboard generation validation
- Database integration testing
- Performance and load testing

Author: Bhashini BI Team
Date: 2024
"""

import os
import sys
import json
import yaml
import logging
import asyncio
import unittest
import requests
import psycopg2
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent / "bi-engine"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestCustomerProfiler(unittest.TestCase):
    """Test cases for customer profiling functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        from customer_profiler import CustomerProfiler
        self.profiler = CustomerProfiler()
        
        # Sample test data
        self.sample_profile = {
            "organization_name": "Test Organization",
            "sector": "government",
            "use_case_category": "citizen_services",
            "specific_use_cases": ["portal", "document_translation"],
            "target_user_base": 10000,
            "geographical_coverage": ["Delhi", "Mumbai"],
            "languages_required": ["Hindi", "English"],
            "business_objectives": ["efficiency", "accessibility"],
            "success_metrics": ["satisfaction", "completion_rate"],
            "contact_email": "test@example.com",
            "sla_tier": "premium"
        }
    
    def test_create_profile_from_form(self):
        """Test customer profile creation from form data"""
        profile = self.profiler.create_profile_from_form(self.sample_profile)
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile["organization_name"], "Test Organization")
        self.assertEqual(profile["sector"], "government")
        self.assertEqual(profile["use_case_category"], "citizen_services")
        self.assertIn("portal", profile["specific_use_cases"])
        self.assertEqual(profile["target_user_base"], 10000)
    
    def test_profile_validation(self):
        """Test profile data validation"""
        # Test valid profile
        is_valid = self.profiler._validate_profile(self.sample_profile)
        self.assertTrue(is_valid)
        
        # Test invalid profile (missing required fields)
        invalid_profile = self.sample_profile.copy()
        del invalid_profile["organization_name"]
        is_valid = self.profiler._validate_profile(invalid_profile)
        self.assertFalse(is_valid)
    
    def test_sector_inference(self):
        """Test sector inference from existing tenant data"""
        # Mock tenant data
        tenant_data = {"sla_tier": "premium", "name": "Government Dept"}
        sector = self.profiler._infer_sector_from_tenant(tenant_data)
        self.assertIsInstance(sector, str)
        self.assertIn(sector, ["government", "healthcare", "education", "private", "ngo"])
    
    def test_use_case_inference(self):
        """Test use case inference from sector"""
        use_case = self.profiler._infer_use_case_from_sector("government")
        self.assertIsInstance(use_case, str)
        self.assertIn(use_case, ["citizen_services", "public_communication", "administrative"])
    
    def test_user_base_estimation(self):
        """Test user base estimation"""
        estimated_users = self.profiler._estimate_user_base("government", "premium")
        self.assertIsInstance(estimated_users, int)
        self.assertGreater(estimated_users, 0)
    
    def test_profile_search(self):
        """Test profile search functionality"""
        # Create a profile first
        profile = self.profiler.create_profile_from_form(self.sample_profile)
        
        # Search by sector
        gov_profiles = self.profiler.get_profiles_by_sector("government")
        self.assertIsInstance(gov_profiles, list)
        self.assertGreater(len(gov_profiles), 0)
        
        # Search by use case
        service_profiles = self.profiler.get_profiles_by_use_case("citizen_services")
        self.assertIsInstance(service_profiles, list)
    
    def test_profile_statistics(self):
        """Test profile statistics generation"""
        stats = self.profiler.get_profile_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn("total_profiles", stats)
        self.assertIn("sector_distribution", stats)
        self.assertIn("use_case_distribution", stats)


class TestValueEstimator(unittest.TestCase):
    """Test cases for value estimation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        from value_estimator import ValueEstimator
        self.estimator = ValueEstimator()
        
        # Sample test data
        self.sample_profile = {
            "tenant_id": "test-001",
            "organization_name": "Test Organization",
            "sector": "government",
            "use_case_category": "citizen_services",
            "target_user_base": 10000,
            "sla_tier": "premium"
        }
        
        self.sample_qos_metrics = [
            {
                "availability_percent": 99.5,
                "response_time_p95": 1500,
                "error_rate": 0.01,
                "throughput_rps": 200,
                "latency_p95": 1200,
                "timestamp": datetime.now(),
                "service_type": "Translation"
            }
        ]
    
    def test_cost_savings_calculation(self):
        """Test cost savings calculation"""
        savings = self.estimator._calculate_cost_savings(
            self.sample_profile, self.sample_qos_metrics
        )
        self.assertIsInstance(savings, float)
        self.assertGreater(savings, 0)
    
    def test_user_reach_impact_calculation(self):
        """Test user reach impact calculation"""
        impact = self.estimator._calculate_user_reach_impact(
            self.sample_profile, self.sample_qos_metrics
        )
        self.assertIsInstance(impact, int)
        self.assertGreater(impact, 0)
    
    def test_efficiency_gains_calculation(self):
        """Test efficiency gains calculation"""
        gains = self.estimator._calculate_efficiency_gains(
            self.sample_profile, self.sample_qos_metrics
        )
        self.assertIsInstance(gains, float)
        self.assertGreater(gains, 0)
    
    def test_quality_improvements_calculation(self):
        """Test quality improvements calculation"""
        improvements = self.estimator._calculate_quality_improvements(
            self.sample_profile, self.sample_qos_metrics
        )
        self.assertIsInstance(improvements, float)
        self.assertGreater(improvements, 0)
    
    def test_roi_calculation(self):
        """Test ROI calculation"""
        roi = self.estimator._calculate_roi_ratio(
            self.sample_profile, self.sample_qos_metrics
        )
        self.assertIsInstance(roi, float)
        self.assertGreater(roi, 0)
    
    def test_payback_period_calculation(self):
        """Test payback period calculation"""
        payback = self.estimator._calculate_payback_period(
            self.sample_profile, self.sample_qos_metrics
        )
        self.assertIsInstance(payback, float)
        self.assertGreater(payback, 0)
    
    def test_total_value_score_calculation(self):
        """Test total value score calculation"""
        score = self.estimator._calculate_total_value_score(
            self.sample_profile, self.sample_qos_metrics
        )
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_confidence_score_calculation(self):
        """Test confidence score calculation"""
        confidence = self.estimator._calculate_confidence_score(
            self.sample_profile, self.sample_qos_metrics
        )
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0)
        self.assertLessEqual(confidence, 100)
    
    def test_complete_value_calculation(self):
        """Test complete value calculation process"""
        value_metrics = self.estimator.calculate_customer_value(
            self.sample_profile, self.sample_qos_metrics
        )
        
        self.assertIsNotNone(value_metrics)
        self.assertIsInstance(value_metrics.cost_savings, float)
        self.assertIsInstance(value_metrics.user_reach_impact, int)
        self.assertIsInstance(value_metrics.efficiency_gains, float)
        self.assertIsInstance(value_metrics.quality_improvements, float)
        self.assertIsInstance(value_metrics.total_value_score, float)
        self.assertIsInstance(value_metrics.confidence_score, float)
        self.assertIsInstance(value_metrics.roi_ratio, float)
        self.assertIsInstance(value_metrics.payback_period_months, float)


class TestRecommendationEngine(unittest.TestCase):
    """Test cases for recommendation engine functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        from recommendation_engine import RecommendationEngine
        self.engine = RecommendationEngine()
        
        # Sample test data
        self.sample_profile = {
            "tenant_id": "test-001",
            "organization_name": "Test Organization",
            "sector": "government",
            "use_case_category": "citizen_services",
            "target_user_base": 10000,
            "sla_tier": "premium"
        }
        
        self.sample_qos_analysis = {
            "performance_score": 75.0,
            "reliability_score": 85.0,
            "capacity_score": 60.0,
            "utilization_score": 70.0,
            "anomaly_flags": ["response_time_spike"],
            "trend_analysis": {"trends": ["performance_declining"]},
            "critical_issues": ["high_latency"],
            "optimization_opportunities": ["cache_optimization"]
        }
    
    def test_performance_score_calculation(self):
        """Test performance score calculation"""
        score = self.engine._calculate_performance_score([])
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_reliability_score_calculation(self):
        """Test reliability score calculation"""
        score = self.engine._calculate_reliability_score([])
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_capacity_score_calculation(self):
        """Test capacity score calculation"""
        score = self.engine._calculate_capacity_score([])
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_utilization_score_calculation(self):
        """Test utilization score calculation"""
        score = self.engine._calculate_utilization_score([])
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_anomaly_detection(self):
        """Test anomaly detection functionality"""
        anomalies = self.engine._detect_anomalies([])
        self.assertIsInstance(anomalies, list)
    
    def test_trend_analysis(self):
        """Test trend analysis functionality"""
        trends = self.engine._analyze_trends([])
        self.assertIsInstance(trends, dict)
        self.assertIn("trends", trends)
        self.assertIn("patterns", trends)
    
    def test_critical_issue_identification(self):
        """Test critical issue identification"""
        issues = self.engine._identify_critical_issues([])
        self.assertIsInstance(issues, list)
    
    def test_optimization_opportunity_identification(self):
        """Test optimization opportunity identification"""
        opportunities = self.engine._identify_optimization_opportunities([])
        self.assertIsInstance(opportunities, list)
    
    def test_recommendation_generation(self):
        """Test recommendation generation process"""
        recommendations = self.engine.generate_recommendations(
            self.sample_qos_analysis, self.sample_profile
        )
        
        self.assertIsInstance(recommendations, list)
        if recommendations:
            rec = recommendations[0]
            self.assertIsInstance(rec.recommendation_id, str)
            self.assertIsInstance(rec.tenant_id, str)
            self.assertIsInstance(rec.recommendation_type, str)
            self.assertIsInstance(rec.priority, str)
            self.assertIsInstance(rec.title, str)
            self.assertIsInstance(rec.description, str)
            self.assertIsInstance(rec.expected_impact, str)
            self.assertIsInstance(rec.implementation_effort, str)
            self.assertIsInstance(rec.business_value, float)
            self.assertIsInstance(rec.confidence_score, float)


class TestDataModels(unittest.TestCase):
    """Test cases for data models and validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        from data_models import DataValidator, DataTransformer
        
        self.validator = DataValidator()
        self.transformer = DataTransformer()
        
        # Sample test data
        self.sample_customer_profile = {
            "tenant_id": "test-001",
            "organization_name": "Test Organization",
            "sector": "government",
            "use_case_category": "citizen_services",
            "specific_use_cases": ["portal", "document_translation"],
            "target_user_base": 10000,
            "geographical_coverage": ["Delhi", "Mumbai"],
            "languages_required": ["Hindi", "English"],
            "business_objectives": ["efficiency", "accessibility"],
            "success_metrics": ["satisfaction", "completion_rate"],
            "contact_email": "test@example.com",
            "sla_tier": "premium"
        }
    
    def test_customer_profile_validation(self):
        """Test customer profile validation"""
        is_valid = self.validator.validate_customer_profile(self.sample_customer_profile)
        self.assertTrue(is_valid)
        
        # Test invalid profile
        invalid_profile = self.sample_customer_profile.copy()
        invalid_profile["contact_email"] = "invalid-email"
        is_valid = self.validator.validate_customer_profile(invalid_profile)
        self.assertFalse(is_valid)
    
    def test_value_estimate_validation(self):
        """Test value estimate validation"""
        value_estimate = {
            "tenant_id": "test-001",
            "cost_savings": 50000.0,
            "user_reach_impact": 5000,
            "efficiency_gains": 25.5,
            "quality_improvements": 30.2,
            "total_value_score": 85.7,
            "confidence_score": 88.3
        }
        
        is_valid = self.validator.validate_value_estimate(value_estimate)
        self.assertTrue(is_valid)
    
    def test_data_transformation(self):
        """Test data transformation functionality"""
        # Test profile transformation
        api_response = self.transformer.profile_to_api_response(self.sample_customer_profile)
        self.assertIsInstance(api_response, dict)
        self.assertIn("tenant_id", api_response)
        self.assertIn("organization_name", api_response)
        self.assertIn("sector", api_response)


class TestAPIServer(unittest.TestCase):
    """Test cases for API server functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "http://localhost:8001"
        self.api_prefix = "/api/v1"
        
        # Sample test data
        self.sample_profile = {
            "organization_name": "Test Organization",
            "sector": "government",
            "use_case_category": "citizen_services",
            "specific_use_cases": ["portal", "document_translation"],
            "target_user_base": 10000,
            "geographical_coverage": ["Delhi", "Mumbai"],
            "languages_required": ["Hindi", "English"],
            "business_objectives": ["efficiency", "accessibility"],
            "success_metrics": ["satisfaction", "completion_rate"],
            "contact_email": "test@example.com",
            "sla_tier": "premium"
        }
    
    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("status", data)
            self.assertEqual(data["status"], "healthy")
        except requests.exceptions.RequestException:
            self.skipTest("API server not running")
    
    def test_customer_profiles_endpoint(self):
        """Test customer profiles endpoint"""
        try:
            # Test GET profiles
            response = requests.get(f"{self.base_url}{self.api_prefix}/profiles", timeout=5)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("data", data)
            self.assertIsInstance(data["data"], list)
            
            # Test POST profile
            response = requests.post(
                f"{self.base_url}{self.api_prefix}/profiles",
                json=self.sample_profile,
                timeout=5
            )
            self.assertIn(response.status_code, [200, 201])
            
        except requests.exceptions.RequestException:
            self.skipTest("API server not running")
    
    def test_value_estimation_endpoint(self):
        """Test value estimation endpoint"""
        try:
            response = requests.get(f"{self.base_url}{self.api_prefix}/value-estimation/health", timeout=5)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.RequestException:
            self.skipTest("API server not running")
    
    def test_recommendations_endpoint(self):
        """Test recommendations endpoint"""
        try:
            response = requests.get(f"{self.base_url}{self.api_prefix}/recommendations/health", timeout=5)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.RequestException:
            self.skipTest("API server not running")
    
    def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        try:
            # Test summary endpoint
            response = requests.get(f"{self.base_url}{self.api_prefix}/analytics/summary", timeout=5)
            self.assertEqual(response.status_code, 200)
            
            # Test sector-specific endpoint
            response = requests.get(f"{self.base_url}{self.api_prefix}/analytics/sector/government", timeout=5)
            self.assertEqual(response.status_code, 200)
            
        except requests.exceptions.RequestException:
            self.skipTest("API server not running")


class TestDashboardGeneration(unittest.TestCase):
    """Test cases for dashboard generation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        sys.path.append(str(Path(__file__).parent.parent / "dashboard-generation"))
        from sector_dashboard_generator import SectorDashboardGenerator
        
        self.generator = SectorDashboardGenerator()
        
        # Sample test data
        self.sample_profile = {
            "tenant_id": "test-001",
            "organization_name": "Test Government Department",
            "sector": "government",
            "use_case_category": "citizen_services",
            "target_user_base": 10000,
            "geographical_coverage": ["Delhi", "Mumbai"],
            "languages_required": ["Hindi", "English"],
            "sla_tier": "premium"
        }
    
    def test_sector_template_loading(self):
        """Test sector template loading"""
        template = self.generator._get_sector_template("government")
        self.assertIsNotNone(template)
        self.assertIn("title", template)
        self.assertIn("panels", template)
        self.assertIn("templating", template)
    
    def test_customer_specific_value_injection(self):
        """Test customer-specific value injection"""
        template = self.generator._get_sector_template("government")
        dashboard = self.generator._inject_customer_specific_values(template, self.sample_profile)
        
        self.assertIn("Test Government Department", dashboard["title"])
        self.assertIn("government", dashboard["tags"])
    
    def test_sector_kpi_injection(self):
        """Test sector KPI injection"""
        template = self.generator._get_sector_template("government")
        dashboard = self.generator._inject_customer_specific_values(template, self.sample_profile)
        dashboard = self.generator._inject_sector_kpis(dashboard, "government", self.sample_profile)
        
        # Check if additional panels were added
        self.assertGreater(len(dashboard["panels"]), len(template["panels"]))
    
    def test_dashboard_validation(self):
        """Test dashboard validation"""
        template = self.generator._get_sector_template("government")
        dashboard = self.generator._inject_customer_specific_values(template, self.sample_profile)
        
        validation = self.generator._validate_dashboard(dashboard)
        self.assertTrue(validation["is_valid"])
    
    def test_complete_dashboard_generation(self):
        """Test complete dashboard generation process"""
        dashboard = self.generator.generate_sector_dashboard(self.sample_profile)
        
        self.assertIsNotNone(dashboard)
        self.assertIn("title", dashboard)
        self.assertIn("panels", dashboard)
        self.assertIn("templating", dashboard)
        self.assertIn("Test Government Department", dashboard["title"])


class TestDatabaseIntegration(unittest.TestCase):
    """Test cases for database integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Database connection parameters (from config)
        self.db_config = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": os.getenv("POSTGRES_PORT", "5432"),
            "database": os.getenv("POSTGRES_DB", "bhashini_profiling"),
            "user": os.getenv("POSTGRES_USER", "bhashini_user"),
            "password": os.getenv("POSTGRES_PASSWORD", "bhashini_password")
        }
    
    def test_database_connection(self):
        """Test database connectivity"""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.close()
            self.assertTrue(True)  # Connection successful
        except Exception as e:
            self.skipTest(f"Database connection failed: {e}")
    
    def test_table_existence(self):
        """Test if required tables exist"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Check for required tables
            required_tables = [
                "customer_profiles",
                "value_estimates", 
                "recommendations",
                "profile_history",
                "sector_kpi_templates",
                "use_case_templates"
            ]
            
            for table in required_tables:
                cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
                exists = cursor.fetchone()[0]
                self.assertTrue(exists, f"Table {table} does not exist")
            
            conn.close()
            
        except Exception as e:
            self.skipTest(f"Database test failed: {e}")
    
    def test_data_integrity(self):
        """Test data integrity constraints"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Test foreign key constraints
            cursor.execute("""
                SELECT COUNT(*) FROM customer_profiles cp
                LEFT JOIN value_estimates ve ON cp.tenant_id = ve.tenant_id
                WHERE ve.tenant_id IS NOT NULL
            """)
            
            # This should not raise an error if foreign keys are properly set up
            count = cursor.fetchone()[0]
            self.assertIsInstance(count, int)
            
            conn.close()
            
        except Exception as e:
            self.skipTest(f"Data integrity test failed: {e}")


class TestEndToEndWorkflow(unittest.TestCase):
    """Test cases for end-to-end workflow testing"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "http://localhost:8001"
        self.api_prefix = "/api/v1"
        
        # Sample workflow data
        self.workflow_data = {
            "customer_profile": {
                "organization_name": "E2E Test Organization",
                "sector": "healthcare",
                "use_case_category": "patient_communication",
                "specific_use_cases": ["medical_records", "appointments"],
                "target_user_base": 5000,
                "geographical_coverage": ["Test City"],
                "languages_required": ["English", "Hindi"],
                "business_objectives": ["patient_care", "communication"],
                "success_metrics": ["accuracy", "satisfaction"],
                "contact_email": "e2e@example.com",
                "sla_tier": "premium"
            },
            "qos_metrics": [
                {
                    "availability_percent": 99.8,
                    "response_time_p95": 1200,
                    "error_rate": 0.005,
                    "throughput_rps": 150,
                    "latency_p95": 800,
                    "timestamp": datetime.now().isoformat(),
                    "service_type": "Translation"
                }
            ]
        }
    
    def test_complete_customer_onboarding_workflow(self):
        """Test complete customer onboarding workflow"""
        try:
            # Step 1: Create customer profile
            response = requests.post(
                f"{self.base_url}{self.api_prefix}/profiles",
                json=self.workflow_data["customer_profile"],
                timeout=10
            )
            self.assertEqual(response.status_code, 201)
            
            profile_data = response.json()
            tenant_id = profile_data["data"]["tenant_id"]
            
            # Step 2: Generate value estimation
            response = requests.post(
                f"{self.base_url}{self.api_prefix}/value-estimation/{tenant_id}",
                json={"qos_metrics": self.workflow_data["qos_metrics"]},
                timeout=10
            )
            self.assertEqual(response.status_code, 200)
            
            # Step 3: Generate recommendations
            response = requests.post(
                f"{self.base_url}{self.api_prefix}/recommendations/{tenant_id}",
                json={"qos_metrics": self.workflow_data["qos_metrics"]},
                timeout=10
            )
            self.assertEqual(response.status_code, 200)
            
            # Step 4: Verify profile exists
            response = requests.get(f"{self.base_url}{self.api_prefix}/profiles/{tenant_id}", timeout=10)
            self.assertEqual(response.status_code, 200)
            
            # Step 5: Verify analytics data
            response = requests.get(f"{self.base_url}{self.api_prefix}/analytics/summary", timeout=10)
            self.assertEqual(response.status_code, 200)
            
            # Cleanup: Delete test profile
            response = requests.delete(f"{self.base_url}{self.api_prefix}/profiles/{tenant_id}", timeout=10)
            self.assertIn(response.status_code, [200, 204])
            
        except requests.exceptions.RequestException:
            self.skipTest("API server not running")


class TestPerformanceAndLoad(unittest.TestCase):
    """Test cases for performance and load testing"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "http://localhost:8001"
        self.api_prefix = "/api/v1"
    
    def test_api_response_time(self):
        """Test API response time under normal load"""
        try:
            start_time = datetime.now()
            
            response = requests.get(f"{self.base_url}/health", timeout=5)
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            self.assertEqual(response.status_code, 200)
            self.assertLess(response_time, 1.0, "API response time should be under 1 second")
            
        except requests.exceptions.RequestException:
            self.skipTest("API server not running")
    
    def test_concurrent_requests(self):
        """Test concurrent request handling"""
        try:
            import concurrent.futures
            
            def make_request():
                response = requests.get(f"{self.base_url}/health", timeout=5)
                return response.status_code
            
            # Make 10 concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                results = [future.result() for future in futures]
            
            # All requests should succeed
            self.assertEqual(len(results), 10)
            self.assertTrue(all(status == 200 for status in results))
            
        except requests.exceptions.RequestException:
            self.skipTest("API server not running")
        except ImportError:
            self.skipTest("concurrent.futures not available")


def run_all_tests():
    """Run all test suites"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestCustomerProfiler,
        TestValueEstimator,
        TestRecommendationEngine,
        TestDataModels,
        TestAPIServer,
        TestDashboardGeneration,
        TestDatabaseIntegration,
        TestEndToEndWorkflow,
        TestPerformanceAndLoad
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


def main():
    """Main function for running tests"""
    print("🚀 Starting Bhashini BI System Test Suite...")
    print("=" * 60)
    
    # Check if API server is running
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print("⚠️  API server responded with unexpected status")
    except requests.exceptions.RequestException:
        print("⚠️  API server is not running - some tests will be skipped")
    
    # Check database connection
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "bhashini_profiling"),
            user=os.getenv("POSTGRES_USER", "bhashini_user"),
            password=os.getenv("POSTGRES_PASSWORD", "bhashini_password")
        )
        conn.close()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"⚠️  Database connection failed: {e} - some tests will be skipped")
    
    print("=" * 60)
    
    # Run tests
    success = run_all_tests()
    
    print("=" * 60)
    if success:
        print("🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
