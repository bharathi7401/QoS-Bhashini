#!/usr/bin/env python3
"""
Profile Data Collector for Bhashini Business Intelligence System

This module provides automated collection and processing of customer application form data.
It handles various input formats, validates data, and integrates with the existing
tenant configuration system.

Features:
- Form data ingestion from multiple sources
- Data validation and cleansing
- Automated profile enrichment
- Integration with tenant configurations
- Batch processing capabilities
- Profile change detection and notification
- Data quality monitoring and reporting

Author: Bhashini BI Team
Date: 2024
"""

import json
import csv
import yaml
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class FormData:
    """Represents customer application form data"""
    organization_name: str
    sector: str
    use_case_category: str
    specific_use_cases: List[str]
    target_user_base: int
    geographical_coverage: List[str]
    languages_required: List[str]
    business_objectives: List[str]
    success_metrics: List[str]
    contact_email: str
    contact_phone: Optional[str] = None
    industry: Optional[str] = None
    annual_revenue: Optional[float] = None
    employee_count: Optional[int] = None
    sla_tier: Optional[str] = None
    profile_status: str = "active"
    profile_created_date: Optional[datetime] = None


@dataclass
class ValidationResult:
    """Result of data validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    cleaned_data: Optional[Dict[str, Any]] = None


class ProfileDataCollector:
    """
    Automated system for collecting and processing customer application form data
    """
    
    def __init__(self, config_path: str = "config/tenant-config.yml"):
        """
        Initialize the profile data collector
        
        Args:
            config_path: Path to tenant configuration file
        """
        self.config_path = Path(config_path)
        self.tenant_config = self._load_tenant_config()
        self.validation_rules = self._load_validation_rules()
        self.sector_mappings = self._load_sector_mappings()
        self.use_case_mappings = self._load_use_case_mappings()
        
        # Data quality metrics
        self.quality_metrics = {
            "total_forms_processed": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "enrichment_applications": 0,
            "integration_successes": 0,
            "integration_failures": 0
        }
    
    def _load_tenant_config(self) -> Dict[str, Any]:
        """Load existing tenant configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"Tenant config file not found: {self.config_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading tenant config: {e}")
            return {}
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load data validation rules"""
        return {
            "required_fields": [
                "organization_name", "sector", "use_case_category",
                "target_user_base", "contact_email"
            ],
            "field_constraints": {
                "organization_name": {
                    "min_length": 2,
                    "max_length": 100,
                    "pattern": r"^[a-zA-Z0-9\s\-\.&]+$"
                },
                "contact_email": {
                    "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                },
                "target_user_base": {
                    "min_value": 1,
                    "max_value": 1000000000
                }
            },
            "sector_values": ["government", "healthcare", "education", "private", "NGO"],
            "use_case_categories": [
                "citizen_services", "patient_communication", "content_localization",
                "business_operations", "community_services"
            ]
        }
    
    def _load_sector_mappings(self) -> Dict[str, str]:
        """Load sector name mappings and aliases"""
        return {
            "gov": "government",
            "govt": "government",
            "public": "government",
            "health": "healthcare",
            "medical": "healthcare",
            "hospital": "healthcare",
            "edu": "education",
            "school": "education",
            "university": "education",
            "college": "education",
            "corporate": "private",
            "business": "private",
            "enterprise": "private",
            "non_profit": "NGO",
            "nonprofit": "NGO",
            "charity": "NGO"
        }
    
    def _load_use_case_mappings(self) -> Dict[str, str]:
        """Load use case category mappings and aliases"""
        return {
            "citizen_portal": "citizen_services",
            "government_services": "citizen_services",
            "public_services": "citizen_services",
            "patient_care": "patient_communication",
            "medical_communication": "patient_communication",
            "healthcare_services": "patient_communication",
            "content_translation": "content_localization",
            "learning_platform": "content_localization",
            "educational_content": "content_localization",
            "business_communication": "business_operations",
            "customer_service": "business_operations",
            "enterprise_services": "business_operations",
            "community_outreach": "community_services",
            "social_services": "community_services"
        }
    
    def process_form_data(self, form_data: Union[Dict[str, Any], FormData]) -> ValidationResult:
        """
        Process and validate customer application form data
        
        Args:
            form_data: Form data as dictionary or FormData object
            
        Returns:
            ValidationResult with validation status and cleaned data
        """
        try:
            # Convert to dictionary if FormData object
            if isinstance(form_data, FormData):
                data = asdict(form_data)
            else:
                data = form_data.copy()
            
            # Validate required fields
            validation_result = self._validate_required_fields(data)
            if not validation_result.is_valid:
                return validation_result
            
            # Clean and normalize data
            cleaned_data = self._clean_and_normalize_data(data)
            
            # Validate field constraints
            validation_result = self._validate_field_constraints(cleaned_data)
            if not validation_result.is_valid:
                return validation_result
            
            # Enrich data with additional context
            enriched_data = self._enrich_profile_data(cleaned_data)
            
            # Final validation
            validation_result = self._final_validation(enriched_data)
            if validation_result.is_valid:
                validation_result.cleaned_data = enriched_data
                self.quality_metrics["successful_validations"] += 1
            else:
                self.quality_metrics["failed_validations"] += 1
            
            self.quality_metrics["total_forms_processed"] += 1
            return validation_result
            
        except Exception as e:
            logger.error(f"Error processing form data: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Processing error: {str(e)}"],
                warnings=[]
            )
    
    def _validate_required_fields(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate that all required fields are present"""
        errors = []
        warnings = []
        
        for field in self.validation_rules["required_fields"]:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
            elif isinstance(data[field], str) and not data[field].strip():
                errors.append(f"Required field is empty: {field}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _clean_and_normalize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize form data"""
        cleaned = data.copy()
        
        # Normalize sector
        if "sector" in cleaned:
            sector = cleaned["sector"].lower().strip()
            cleaned["sector"] = self.sector_mappings.get(sector, sector)
        
        # Normalize use case category
        if "use_case_category" in cleaned:
            use_case = cleaned["use_case_category"].lower().strip()
            cleaned["use_case_category"] = self.use_case_mappings.get(use_case, use_case)
        
        # Clean organization name
        if "organization_name" in cleaned:
            cleaned["organization_name"] = cleaned["organization_name"].strip()
        
        # Clean email
        if "contact_email" in cleaned:
            cleaned["contact_email"] = cleaned["contact_email"].lower().strip()
        
        # Normalize lists
        for field in ["specific_use_cases", "geographical_coverage", "languages_required", 
                     "business_objectives", "success_metrics"]:
            if field in cleaned:
                if isinstance(cleaned[field], str):
                    # Split comma-separated strings
                    cleaned[field] = [item.strip() for item in cleaned[field].split(",") if item.strip()]
                elif not isinstance(cleaned[field], list):
                    cleaned[field] = []
        
        # Set default values
        if "profile_created_date" not in cleaned:
            cleaned["profile_created_date"] = datetime.now()
        
        if "profile_status" not in cleaned:
            cleaned["profile_status"] = "active"
        
        return cleaned
    
    def _validate_field_constraints(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate field constraints and patterns"""
        errors = []
        warnings = []
        
        constraints = self.validation_rules["field_constraints"]
        
        for field, rules in constraints.items():
            if field not in data:
                continue
            
            value = data[field]
            
            # Length validation
            if "min_length" in rules and isinstance(value, str):
                if len(value) < rules["min_length"]:
                    errors.append(f"{field} too short (min: {rules['min_length']})")
            
            if "max_length" in rules and isinstance(value, str):
                if len(value) > rules["max_length"]:
                    errors.append(f"{field} too long (max: {rules['max_length']})")
            
            # Pattern validation
            if "pattern" in rules and isinstance(value, str):
                if not re.match(rules["pattern"], value):
                    errors.append(f"{field} format invalid")
            
            # Value range validation
            if "min_value" in rules and isinstance(value, (int, float)):
                if value < rules["min_value"]:
                    errors.append(f"{field} below minimum ({rules['min_value']})")
            
            if "max_value" in rules and isinstance(value, (int, float)):
                if value > rules["max_value"]:
                    errors.append(f"{field} above maximum ({rules['max_value']})")
        
        # Validate sector and use case values
        if "sector" in data and data["sector"] not in self.validation_rules["sector_values"]:
            warnings.append(f"Unknown sector: {data['sector']}")
        
        if "use_case_category" in data and data["use_case_category"] not in self.validation_rules["use_case_categories"]:
            warnings.append(f"Unknown use case category: {data['use_case_category']}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _enrich_profile_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich profile data with additional context and inferred values"""
        enriched = data.copy()
        
        # Infer SLA tier based on sector and user base
        if "sla_tier" not in enriched:
            enriched["sla_tier"] = self._infer_sla_tier(
                enriched.get("sector", ""),
                enriched.get("target_user_base", 0)
            )
        
        # Infer industry based on sector
        if "industry" not in enriched:
            enriched["industry"] = self._infer_industry(enriched.get("sector", ""))
        
        # Estimate annual revenue based on sector and employee count
        if "annual_revenue" not in enriched and "employee_count" in enriched:
            enriched["annual_revenue"] = self._estimate_annual_revenue(
                enriched.get("sector", ""),
                enriched.get("employee_count", 0)
            )
        
        # Add geographical context
        if "geographical_coverage" in enriched:
            enriched["geographical_context"] = self._analyze_geographical_context(
                enriched["geographical_coverage"]
            )
        
        # Add language context
        if "languages_required" in enriched:
            enriched["language_context"] = self._analyze_language_context(
                enriched["languages_required"]
            )
        
        self.quality_metrics["enrichment_applications"] += 1
        return enriched
    
    def _infer_sla_tier(self, sector: str, user_base: int) -> str:
        """Infer appropriate SLA tier based on sector and user base"""
        if sector == "healthcare":
            return "premium"  # Critical services
        elif sector == "government" and user_base > 100000:
            return "premium"  # Large government services
        elif sector == "government":
            return "standard"  # Standard government services
        elif user_base > 1000000:
            return "premium"  # Large user base
        elif user_base > 100000:
            return "standard"  # Medium user base
        else:
            return "basic"  # Small user base
    
    def _infer_industry(self, sector: str) -> str:
        """Infer industry based on sector"""
        industry_mapping = {
            "government": "Public Sector",
            "healthcare": "Healthcare",
            "education": "Education",
            "private": "Private Sector",
            "NGO": "Non-Profit"
        }
        return industry_mapping.get(sector, "Other")
    
    def _estimate_annual_revenue(self, sector: str, employee_count: int) -> float:
        """Estimate annual revenue based on sector and employee count"""
        # Rough estimates per employee by sector
        revenue_per_employee = {
            "government": 80000,
            "healthcare": 120000,
            "education": 60000,
            "private": 150000,
            "NGO": 40000
        }
        
        base_revenue = revenue_per_employee.get(sector, 80000)
        return base_revenue * employee_count
    
    def _analyze_geographical_context(self, regions: List[str]) -> Dict[str, Any]:
        """Analyze geographical coverage context"""
        return {
            "total_regions": len(regions),
            "has_national_coverage": any("national" in region.lower() for region in regions),
            "has_international_coverage": any("international" in region.lower() for region in regions),
            "primary_focus": regions[0] if regions else "Unknown"
        }
    
    def _analyze_language_context(self, languages: List[str]) -> Dict[str, Any]:
        """Analyze language requirements context"""
        return {
            "total_languages": len(languages),
            "includes_english": "English" in languages or "english" in [lang.lower() for lang in languages],
            "includes_hindi": "Hindi" in languages or "hindi" in [lang.lower() for lang in languages],
            "language_diversity": "High" if len(languages) > 5 else "Medium" if len(languages) > 2 else "Low"
        }
    
    def _final_validation(self, data: Dict[str, Any]) -> ValidationResult:
        """Perform final validation on enriched data"""
        errors = []
        warnings = []
        
        # Check for logical inconsistencies
        if "target_user_base" in data and data["target_user_base"] > 1000000:
            if data.get("sla_tier") == "basic":
                warnings.append("Large user base should consider higher SLA tier")
        
        if "sector" in data and data["sector"] == "healthcare":
            if data.get("sla_tier") != "premium":
                warnings.append("Healthcare sector typically requires premium SLA")
        
        # Validate geographical coverage
        if "geographical_coverage" in data and len(data["geographical_coverage"]) == 0:
            warnings.append("No geographical coverage specified")
        
        # Validate language requirements
        if "languages_required" in data and len(data["languages_required"]) == 0:
            warnings.append("No languages specified")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def process_csv_batch(self, csv_file_path: str) -> List[ValidationResult]:
        """
        Process a batch of forms from CSV file
        
        Args:
            csv_file_path: Path to CSV file containing form data
            
        Returns:
            List of validation results for each form
        """
        results = []
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                    try:
                        # Convert empty strings to None
                        cleaned_row = {k: v.strip() if isinstance(v, str) and v.strip() else None 
                                     for k, v in row.items()}
                        
                        # Process the form data
                        result = self.process_form_data(cleaned_row)
                        results.append(result)
                        
                        if not result.is_valid:
                            logger.warning(f"Row {row_num}: Validation failed - {result.errors}")
                        else:
                            logger.info(f"Row {row_num}: Successfully processed")
                            
                    except Exception as e:
                        logger.error(f"Error processing row {row_num}: {e}")
                        results.append(ValidationResult(
                            is_valid=False,
                            errors=[f"Processing error: {str(e)}"],
                            warnings=[]
                        ))
        
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
        
        return results
    
    def process_json_batch(self, json_file_path: str) -> List[ValidationResult]:
        """
        Process a batch of forms from JSON file
        
        Args:
            json_file_path: Path to JSON file containing form data
            
        Returns:
            List of validation results for each form
        """
        results = []
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if isinstance(data, list):
                    forms = data
                elif isinstance(data, dict) and "forms" in data:
                    forms = data["forms"]
                else:
                    forms = [data]
                
                for form_num, form in enumerate(forms, start=1):
                    try:
                        result = self.process_form_data(form)
                        results.append(result)
                        
                        if not result.is_valid:
                            logger.warning(f"Form {form_num}: Validation failed - {result.errors}")
                        else:
                            logger.info(f"Form {form_num}: Successfully processed")
                            
                    except Exception as e:
                        logger.error(f"Error processing form {form_num}: {e}")
                        results.append(ValidationResult(
                            is_valid=False,
                            errors=[f"Processing error: {str(e)}"],
                            warnings=[]
                        ))
        
        except Exception as e:
            logger.error(f"Error reading JSON file: {e}")
        
        return results
    
    def integrate_with_tenant_config(self, profile_data: Dict[str, Any]) -> bool:
        """
        Integrate new profile with existing tenant configuration
        
        Args:
            profile_data: Validated and enriched profile data
            
        Returns:
            True if integration successful, False otherwise
        """
        try:
            # Generate tenant ID
            tenant_id = self._generate_tenant_id(profile_data["organization_name"])
            
            # Check if tenant already exists
            if tenant_id in self.tenant_config.get("tenants", {}):
                logger.warning(f"Tenant {tenant_id} already exists")
                return False
            
            # Create new tenant entry
            new_tenant = {
                "name": profile_data["organization_name"],
                "sla_tier": profile_data.get("sla_tier", "basic"),
                "sector": profile_data.get("sector", "private"),
                "use_cases": profile_data.get("specific_use_cases", []),
                "languages": profile_data.get("languages_required", []),
                "profile_data": profile_data
            }
            
            # Add to tenant config
            if "tenants" not in self.tenant_config:
                self.tenant_config["tenants"] = {}
            
            self.tenant_config["tenants"][tenant_id] = new_tenant
            
            # Save updated config
            self._save_tenant_config()
            
            logger.info(f"Successfully integrated tenant {tenant_id}")
            self.quality_metrics["integration_successes"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error integrating with tenant config: {e}")
            self.quality_metrics["integration_failures"] += 1
            return False
    
    def _generate_tenant_id(self, organization_name: str) -> str:
        """Generate unique tenant ID from organization name"""
        # Convert to lowercase and replace spaces/special chars with hyphens
        tenant_id = re.sub(r'[^a-zA-Z0-9]', '-', organization_name.lower())
        tenant_id = re.sub(r'-+', '-', tenant_id).strip('-')
        
        # Ensure uniqueness by adding timestamp if needed
        if tenant_id in self.tenant_config.get("tenants", {}):
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            tenant_id = f"{tenant_id}-{timestamp}"
        
        return tenant_id
    
    def _save_tenant_config(self):
        """Save updated tenant configuration"""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.tenant_config, f, default_flow_style=False, indent=2)
            logger.info("Tenant configuration saved successfully")
        except Exception as e:
            logger.error(f"Error saving tenant configuration: {e}")
    
    def get_quality_report(self) -> Dict[str, Any]:
        """Generate data quality report"""
        total_processed = self.quality_metrics["total_forms_processed"]
        
        if total_processed == 0:
            success_rate = 0.0
        else:
            success_rate = (self.quality_metrics["successful_validations"] / total_processed) * 100
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_forms_processed": total_processed,
            "successful_validations": self.quality_metrics["successful_validations"],
            "failed_validations": self.quality_metrics["failed_validations"],
            "success_rate_percentage": round(success_rate, 2),
            "enrichment_applications": self.quality_metrics["enrichment_applications"],
            "integration_successes": self.quality_metrics["integration_successes"],
            "integration_failures": self.quality_metrics["integration_failures"]
        }
    
    def export_processed_profiles(self, output_path: str, 
                                validation_results: List[ValidationResult]) -> bool:
        """
        Export processed profiles to JSON file
        
        Args:
            output_path: Path to output JSON file
            validation_results: List of validation results to export
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_profiles": len(validation_results),
                "successful_profiles": sum(1 for r in validation_results if r.is_valid),
                "failed_profiles": sum(1 for r in validation_results if not r.is_valid),
                "profiles": []
            }
            
            for result in validation_results:
                profile_entry = {
                    "validation_status": "success" if result.is_valid else "failed",
                    "errors": result.errors,
                    "warnings": result.warnings
                }
                
                if result.cleaned_data:
                    profile_entry["profile_data"] = result.cleaned_data
                
                export_data["profiles"].append(profile_entry)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Successfully exported {len(validation_results)} profiles to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting profiles: {e}")
            return False


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Profile Data Collector")
    parser.add_argument("--input", required=True, help="Input file path (CSV or JSON)")
    parser.add_argument("--output", help="Output file path for processed profiles")
    parser.add_argument("--config", default="config/tenant-config.yml", help="Tenant config path")
    parser.add_argument("--integrate", action="store_true", help="Integrate with tenant config")
    
    args = parser.parse_args()
    
    # Initialize collector
    collector = ProfileDataCollector(args.config)
    
    # Process input file
    if args.input.endswith('.csv'):
        results = collector.process_csv_batch(args.input)
    elif args.input.endswith('.json'):
        results = collector.process_json_batch(args.input)
    else:
        print("Unsupported file format. Use CSV or JSON.")
        return
    
    # Print summary
    successful = sum(1 for r in results if r.is_valid)
    failed = len(results) - successful
    
    print(f"\nProcessing Summary:")
    print(f"Total forms: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    # Show errors for failed validations
    if failed > 0:
        print(f"\nFailed validations:")
        for i, result in enumerate(results):
            if not result.is_valid:
                print(f"  Form {i+1}: {result.errors}")
    
    # Export results if requested
    if args.output:
        collector.export_processed_profiles(args.output, results)
    
    # Integrate with tenant config if requested
    if args.integrate:
        print(f"\nIntegrating successful profiles with tenant config...")
        integrated_count = 0
        
        for result in results:
            if result.is_valid and result.cleaned_data:
                if collector.integrate_with_tenant_config(result.cleaned_data):
                    integrated_count += 1
        
        print(f"Successfully integrated {integrated_count} profiles")
    
    # Print quality report
    quality_report = collector.get_quality_report()
    print(f"\nQuality Report:")
    print(f"Success Rate: {quality_report['success_rate_percentage']}%")
    print(f"Enrichment Applications: {quality_report['enrichment_applications']}")
    print(f"Integration Successes: {quality_report['integration_successes']}")


if __name__ == "__main__":
    main()
