#!/usr/bin/env python3
"""
Setup Script for Bhashini Business Intelligence System

This script provides comprehensive setup and initialization for the BI system,
including database setup, profile migration, dashboard generation, and validation.

Features:
- Database initialization and migration
- Customer profile migration from existing tenant config
- Sector-specific dashboard generation
- System validation and health checks
- Test data generation
- Rollback capabilities

Author: Bhashini BI Team
Date: 2024
"""

import os
import sys
import json
import yaml
import logging
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import psycopg2
from psycopg2.extras import RealDictCursor
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BISystemSetup:
    """
    Comprehensive setup and initialization for the BI system
    """
    
    def __init__(self, config_path: str = "config.env"):
        """
        Initialize the BI system setup
        
        Args:
            config_path: Path to environment configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.setup_status = {
            "database_initialized": False,
            "profiles_migrated": False,
            "dashboards_generated": False,
            "api_tested": False,
            "overall_status": "not_started"
        }
        
        # Database connection parameters
        self.db_config = {
            "host": self.config.get("POSTGRES_HOST", "localhost"),
            "port": self.config.get("POSTGRES_PORT", "5432"),
            "database": self.config.get("POSTGRES_DB", "bhashini_profiling"),
            "user": self.config.get("POSTGRES_USER", "bhashini_user"),
            "password": self.config.get("POSTGRES_PASSWORD", "bhashini_password")
        }
        
        # API configuration
        self.api_config = {
            "host": self.config.get("BI_API_HOST", "localhost"),
            "port": self.config.get("BI_API_PORT", "8001"),
            "base_url": f"http://{self.config.get('BI_API_HOST', 'localhost')}:{self.config.get('BI_API_PORT', '8001')}"
        }
    
    def _load_config(self) -> Dict[str, str]:
        """Load environment configuration"""
        config = {}
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key] = value
        
        # Load from environment variables as fallback
        for key in ["POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DB", "POSTGRES_USER", 
                   "POSTGRES_PASSWORD", "BI_API_HOST", "BI_API_PORT"]:
            if key not in config:
                config[key] = os.getenv(key, "")
        
        return config
    
    def _test_database_connection(self) -> bool:
        """Test database connectivity"""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.close()
            logger.info("Database connection successful")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def _test_api_connection(self) -> bool:
        """Test API connectivity"""
        try:
            response = requests.get(f"{self.api_config['base_url']}/health", timeout=10)
            if response.status_code == 200:
                logger.info("API connection successful")
                return True
            else:
                logger.error(f"API health check failed with status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"API connection failed: {e}")
            return False
    
    def initialize_database(self) -> bool:
        """Initialize the customer profiling database"""
        try:
            logger.info("Starting database initialization...")
            
            # Test connection
            if not self._test_database_connection():
                logger.error("Cannot proceed with database initialization - connection failed")
                return False
            
            # Connect to database
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Check if tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('customer_profiles', 'value_estimates', 'recommendations')
            """)
            
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            if len(existing_tables) >= 3:
                logger.info("Database tables already exist, skipping initialization")
                self.setup_status["database_initialized"] = True
                return True
            
            # Run initialization script
            init_script_path = Path("database/profiling-db-init.sql")
            if not init_script_path.exists():
                logger.error(f"Database initialization script not found: {init_script_path}")
                return False
            
            with open(init_script_path, 'r') as f:
                init_sql = f.read()
            
            # Execute initialization SQL
            cursor.execute(init_sql)
            conn.commit()
            
            logger.info("Database initialization completed successfully")
            self.setup_status["database_initialized"] = True
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def migrate_customer_profiles(self) -> bool:
        """Migrate existing customer data from tenant configuration"""
        try:
            logger.info("Starting customer profile migration...")
            
            if not self.setup_status["database_initialized"]:
                logger.error("Database must be initialized before profile migration")
                return False
            
            # Load existing tenant configuration
            tenant_config_path = Path("config/tenant-config.yml")
            if not tenant_config_path.exists():
                logger.error(f"Tenant configuration not found: {tenant_config_path}")
                return False
            
            with open(tenant_config_path, 'r') as f:
                tenant_config = yaml.safe_load(f)
            
            # Connect to database
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Check if profiles already exist
            cursor.execute("SELECT COUNT(*) FROM customer_profiles")
            existing_count = cursor.fetchone()[0]
            
            if existing_count > 0:
                logger.info(f"Customer profiles already exist ({existing_count} profiles), skipping migration")
                self.setup_status["profiles_migrated"] = True
                return True
            
            # Migrate tenant data to customer profiles
            migrated_count = 0
            for tenant_id, tenant_data in tenant_config.get("tenants", {}).items():
                try:
                    # Infer sector and use case from tenant data
                    sector = self._infer_sector_from_tenant(tenant_data)
                    use_case = self._infer_use_case_from_tenant(tenant_data)
                    
                    # Create customer profile
                    profile_data = {
                        "tenant_id": tenant_id,
                        "organization_name": tenant_data.get("name", f"Organization {tenant_id}"),
                        "sector": sector,
                        "use_case_category": use_case,
                        "specific_use_cases": ["general_services"],
                        "target_user_base": self._estimate_user_base(tenant_data),
                        "geographical_coverage": ["India"],
                        "languages_required": ["Hindi", "English"],
                        "business_objectives": ["improve_service_quality", "increase_efficiency"],
                        "success_metrics": ["availability", "response_time", "user_satisfaction"],
                        "sla_tier": tenant_data.get("sla_tier", "standard"),
                        "profile_status": "active"
                    }
                    
                    # Insert profile
                    cursor.execute("""
                        INSERT INTO customer_profiles (
                            tenant_id, organization_name, sector, use_case_category,
                            specific_use_cases, target_user_base, geographical_coverage,
                            languages_required, business_objectives, success_metrics,
                            sla_tier, profile_status
                        ) VALUES (
                            %(tenant_id)s, %(organization_name)s, %(sector)s, %(use_case_category)s,
                            %(specific_use_cases)s, %(target_user_base)s, %(geographical_coverage)s,
                            %(languages_required)s, %(business_objectives)s, %(success_metrics)s,
                            %(sla_tier)s, %(profile_status)s
                        )
                    """, profile_data)
                    
                    migrated_count += 1
                    logger.info(f"Migrated profile for tenant: {tenant_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to migrate profile for tenant {tenant_id}: {e}")
                    continue
            
            conn.commit()
            logger.info(f"Customer profile migration completed: {migrated_count} profiles migrated")
            self.setup_status["profiles_migrated"] = True
            return True
            
        except Exception as e:
            logger.error(f"Customer profile migration failed: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def _infer_sector_from_tenant(self, tenant_data: Dict[str, Any]) -> str:
        """Infer sector from tenant data"""
        # Default to private sector
        return "private"
    
    def _infer_use_case_from_tenant(self, tenant_data: Dict[str, Any]) -> str:
        """Infer use case from tenant data"""
        # Default to general services
        return "general_services"
    
    def _estimate_user_base(self, tenant_data: Dict[str, Any]) -> int:
        """Estimate user base from tenant data"""
        # Default to 1000 users
        return 1000
    
    def generate_sector_dashboards(self) -> bool:
        """Generate sector-specific dashboards for existing customers"""
        try:
            logger.info("Starting sector dashboard generation...")
            
            if not self.setup_status["profiles_migrated"]:
                logger.error("Customer profiles must be migrated before dashboard generation")
                return False
            
            # Import dashboard generator
            sys.path.append(str(Path("scripts/dashboard-generation")))
            from sector_dashboard_generator import SectorDashboardGenerator
            
            # Initialize generator
            generator = SectorDashboardGenerator()
            
            # Get customer profiles from database
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT * FROM customer_profiles WHERE profile_status = 'active'")
            customer_profiles = cursor.fetchall()
            
            if not customer_profiles:
                logger.warning("No active customer profiles found for dashboard generation")
                return True
            
            # Generate dashboards
            results = generator.generate_batch_dashboards(customer_profiles)
            
            if results["successful_generations"] > 0:
                logger.info(f"Dashboard generation completed: {results['successful_generations']} successful")
                self.setup_status["dashboards_generated"] = True
                return True
            else:
                logger.error("Dashboard generation failed")
                return False
                
        except Exception as e:
            logger.error(f"Sector dashboard generation failed: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def test_api_functionality(self) -> bool:
        """Test API functionality and endpoints"""
        try:
            logger.info("Testing API functionality...")
            
            # Test health endpoint
            if not self._test_api_connection():
                logger.error("API health check failed")
                return False
            
            # Test customer profiles endpoint
            response = requests.get(f"{self.api_config['base_url']}/api/v1/profiles", timeout=10)
            if response.status_code != 200:
                logger.error(f"Customer profiles endpoint failed with status {response.status_code}")
                return False
            
            # Test value estimation endpoint
            response = requests.get(f"{self.api_config['base_url']}/api/v1/value-estimation/health", timeout=10)
            if response.status_code != 200:
                logger.error(f"Value estimation endpoint failed with status {response.status_code}")
                return False
            
            # Test recommendations endpoint
            response = requests.get(f"{self.api_config['base_url']}/api/v1/recommendations/health", timeout=10)
            if response.status_code != 200:
                logger.error(f"Recommendations endpoint failed with status {response.status_code}")
                return False
            
            logger.info("API functionality tests passed")
            self.setup_status["api_tested"] = True
            return True
            
        except Exception as e:
            logger.error(f"API functionality testing failed: {e}")
            return False
    
    def validate_system_health(self) -> Dict[str, Any]:
        """Validate overall system health"""
        health_status = {
            "database": self._test_database_connection(),
            "api": self._test_api_connection(),
            "config_files": self._validate_config_files(),
            "dependencies": self._validate_dependencies(),
            "overall_status": "unknown"
        }
        
        # Determine overall status
        if all(health_status.values()):
            health_status["overall_status"] = "healthy"
        elif any(health_status.values()):
            health_status["overall_status"] = "degraded"
        else:
            health_status["overall_status"] = "unhealthy"
        
        return health_status
    
    def _validate_config_files(self) -> bool:
        """Validate required configuration files"""
        required_files = [
            "config/sector-kpis.yml",
            "config/use-case-templates.yml",
            "config/tenant-config.yml"
        ]
        
        for file_path in required_files:
            if not Path(file_path).exists():
                logger.error(f"Required config file not found: {file_path}")
                return False
        
        return True
    
    def _validate_dependencies(self) -> bool:
        """Validate system dependencies"""
        try:
            import fastapi
            import sqlalchemy
            import sklearn
            import pandas
            import numpy
            return True
        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            return False
    
    def generate_test_data(self) -> bool:
        """Generate test data for development and testing"""
        try:
            logger.info("Generating test data...")
            
            if not self.setup_status["database_initialized"]:
                logger.error("Database must be initialized before test data generation")
                return False
            
            # Connect to database
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Check if test data already exists
            cursor.execute("SELECT COUNT(*) FROM customer_profiles WHERE organization_name LIKE '%Test%'")
            existing_test_data = cursor.fetchone()[0]
            
            if existing_test_data > 0:
                logger.info("Test data already exists, skipping generation")
                return True
            
            # Generate test customer profiles
            test_profiles = [
                {
                    "tenant_id": "test-gov-001",
                    "organization_name": "Test Government Department",
                    "sector": "government",
                    "use_case_category": "citizen_services",
                    "specific_use_cases": ["test_portal", "test_document_translation"],
                    "target_user_base": 50000,
                    "geographical_coverage": ["Test City"],
                    "languages_required": ["Hindi", "English"],
                    "business_objectives": ["test_efficiency", "test_quality"],
                    "success_metrics": ["test_availability", "test_satisfaction"],
                    "sla_tier": "standard",
                    "profile_status": "active"
                },
                {
                    "tenant_id": "test-health-001",
                    "organization_name": "Test Healthcare Provider",
                    "sector": "healthcare",
                    "use_case_category": "patient_communication",
                    "specific_use_cases": ["test_medical_records", "test_appointments"],
                    "target_user_base": 10000,
                    "geographical_coverage": ["Test City"],
                    "languages_required": ["English", "Hindi"],
                    "business_objectives": ["test_patient_care", "test_communication"],
                    "success_metrics": ["test_accuracy", "test_satisfaction"],
                    "sla_tier": "premium",
                    "profile_status": "active"
                }
            ]
            
            # Insert test profiles
            for profile in test_profiles:
                cursor.execute("""
                    INSERT INTO customer_profiles (
                        tenant_id, organization_name, sector, use_case_category,
                        specific_use_cases, target_user_base, geographical_coverage,
                        languages_required, business_objectives, success_metrics,
                        sla_tier, profile_status
                    ) VALUES (
                        %(tenant_id)s, %(organization_name)s, %(sector)s, %(use_case_category)s,
                        %(specific_use_cases)s, %(target_user_base)s, %(geographical_coverage)s,
                        %(languages_required)s, %(business_objectives)s, %(success_metrics)s,
                        %(sla_tier)s, %(profile_status)s
                    )
                """, profile)
            
            conn.commit()
            logger.info("Test data generation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Test data generation failed: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def run_complete_setup(self) -> bool:
        """Run complete setup process"""
        try:
            logger.info("Starting complete BI system setup...")
            
            # Step 1: Initialize database
            if not self.initialize_database():
                logger.error("Database initialization failed")
                return False
            
            # Step 2: Migrate customer profiles
            if not self.migrate_customer_profiles():
                logger.error("Customer profile migration failed")
                return False
            
            # Step 3: Generate sector dashboards
            if not self.generate_sector_dashboards():
                logger.error("Sector dashboard generation failed")
                return False
            
            # Step 4: Test API functionality
            if not self.test_api_functionality():
                logger.error("API functionality testing failed")
                return False
            
            # Step 5: Generate test data (optional)
            if self.config.get("GENERATE_TEST_DATA", "false").lower() == "true":
                self.generate_test_data()
            
            # Step 6: Validate system health
            health_status = self.validate_system_health()
            
            if health_status["overall_status"] == "healthy":
                logger.info("BI system setup completed successfully!")
                self.setup_status["overall_status"] = "completed"
                return True
            else:
                logger.warning(f"BI system setup completed with warnings: {health_status['overall_status']}")
                self.setup_status["overall_status"] = "completed_with_warnings"
                return True
                
        except Exception as e:
            logger.error(f"Complete setup failed: {e}")
            self.setup_status["overall_status"] = "failed"
            return False
    
    def get_setup_status(self) -> Dict[str, Any]:
        """Get current setup status"""
        return self.setup_status.copy()
    
    def rollback_setup(self) -> bool:
        """Rollback setup changes"""
        try:
            logger.info("Starting setup rollback...")
            
            # Connect to database
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Drop all tables
            cursor.execute("""
                DROP TABLE IF EXISTS 
                    qos_metrics_cache,
                    sector_kpi_templates,
                    use_case_templates,
                    profile_history,
                    recommendations,
                    value_estimates,
                    customer_profiles
                CASCADE
            """)
            
            conn.commit()
            conn.close()
            
            # Reset setup status
            self.setup_status = {
                "database_initialized": False,
                "profiles_migrated": False,
                "dashboards_generated": False,
                "api_tested": False,
                "overall_status": "rolled_back"
            }
            
            logger.info("Setup rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Setup rollback failed: {e}")
            return False


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bhashini BI System Setup")
    parser.add_argument("--action", choices=["setup", "validate", "rollback", "status"], 
                       default="setup", help="Action to perform")
    parser.add_argument("--config", default="config.env", help="Configuration file path")
    parser.add_argument("--generate-test-data", action="store_true", 
                       help="Generate test data during setup")
    
    args = parser.parse_args()
    
    # Initialize setup
    setup = BISystemSetup(args.config)
    
    if args.generate_test_data:
        setup.config["GENERATE_TEST_DATA"] = "true"
    
    if args.action == "setup":
        success = setup.run_complete_setup()
        if success:
            print("✅ BI system setup completed successfully!")
            sys.exit(0)
        else:
            print("❌ BI system setup failed!")
            sys.exit(1)
    
    elif args.action == "validate":
        health_status = setup.validate_system_health()
        print(f"System Health Status: {health_status['overall_status']}")
        for component, status in health_status.items():
            if component != "overall_status":
                print(f"  {component}: {'✅' if status else '❌'}")
        sys.exit(0 if health_status['overall_status'] == 'healthy' else 1)
    
    elif args.action == "rollback":
        success = setup.rollback_setup()
        if success:
            print("✅ Setup rollback completed successfully!")
            sys.exit(0)
        else:
            print("❌ Setup rollback failed!")
            sys.exit(1)
    
    elif args.action == "status":
        status = setup.get_setup_status()
        print("BI System Setup Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        sys.exit(0)


if __name__ == "__main__":
    main()
