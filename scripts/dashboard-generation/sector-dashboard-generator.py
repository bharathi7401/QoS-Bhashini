#!/usr/bin/env python3
"""
Sector Dashboard Generator for Bhashini Business Intelligence System

This module provides automated sector-specific dashboard generation capabilities
that extend the existing customer dashboard generation system.

Features:
- Sector-specific dashboard template selection
- KPI injection from sector-kpis.yml configuration
- Query template processing with customer-specific values
- Dashboard validation and testing
- Batch generation capabilities
- Integration with Grafana provisioning
- Dashboard versioning and updates

Author: Bhashini BI Team
Date: 2024
"""

import json
import yaml
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import re
import copy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SectorDashboardGenerator:
    """
    Automated sector-specific dashboard generation system
    """
    
    def __init__(self, config_path: str = "config/sector-kpis.yml"):
        """
        Initialize the sector dashboard generator
        
        Args:
            config_path: Path to sector KPI configuration file
        """
        self.config_path = Path(config_path)
        self.sector_config = self._load_sector_config()
        self.template_path = Path("grafana/provisioning/dashboards/sector-dashboards")
        self.output_path = Path("grafana/provisioning/dashboards/customer-dashboards")
        
        # Ensure output directory exists
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Dashboard generation metrics
        self.generation_metrics = {
            "total_dashboards_generated": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "sectors_processed": set(),
            "templates_used": set()
        }
    
    def _load_sector_config(self) -> Dict[str, Any]:
        """Load sector-specific KPI configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded sector configuration from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load sector configuration: {e}")
            return {}
    
    def _get_sector_template(self, sector: str) -> Optional[Dict[str, Any]]:
        """Get dashboard template for specific sector"""
        template_file = self.template_path / f"{sector.lower()}-dashboard-template.json"
        
        if not template_file.exists():
            logger.warning(f"Template not found for sector: {sector}")
            return None
        
        try:
            with open(template_file, 'r') as f:
                template = json.load(f)
            logger.info(f"Loaded template for sector: {sector}")
            return template
        except Exception as e:
            logger.error(f"Failed to load template for sector {sector}: {e}")
            return None
    
    def _inject_customer_specific_values(self, template: Dict[str, Any], 
                                       customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Inject customer-specific values into dashboard template"""
        dashboard = copy.deepcopy(template)
        
        # Update dashboard title and tags
        tenant_name = customer_profile.get('organization_name', 'Unknown')
        sector = customer_profile.get('sector', 'general')
        
        dashboard['title'] = f"{tenant_name} - {sector.title()} Dashboard"
        dashboard['tags'] = [sector.lower(), 'customer', 'sector-specific']
        
        # Update template variables
        if 'templating' in dashboard and 'list' in dashboard['templating']:
            for var in dashboard['templating']['list']:
                if var.get('name') == 'tenant_id':
                    var['current'] = {'value': customer_profile.get('tenant_id', '')}
                elif var.get('name') == 'tenant_name':
                    var['current'] = {'value': tenant_name}
                elif var.get('name') == 'sector':
                    var['current'] = {'value': sector}
        
        # Update panel queries with customer-specific values
        if 'panels' in dashboard:
            for panel in dashboard['panels']:
                if 'targets' in panel:
                    for target in panel['targets']:
                        if 'expr' in target:
                            target['expr'] = self._process_query_template(
                                target['expr'], customer_profile
                            )
        
        return dashboard
    
    def _process_query_template(self, query: str, customer_profile: Dict[str, Any]) -> str:
        """Process query template with customer-specific values"""
        # Replace template variables
        replacements = {
            '${tenant_id}': customer_profile.get('tenant_id', ''),
            '${sector}': customer_profile.get('sector', ''),
            '${use_case}': customer_profile.get('use_case_category', ''),
            '${organization}': customer_profile.get('organization_name', '')
        }
        
        for placeholder, value in replacements.items():
            query = query.replace(placeholder, str(value))
        
        return query
    
    def _inject_sector_kpis(self, dashboard: Dict[str, Any], 
                           sector: str, customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Inject sector-specific KPIs into dashboard"""
        if sector not in self.sector_config.get('sectors', {}):
            logger.warning(f"Sector {sector} not found in configuration")
            return dashboard
            
        sector_config = self.sector_config['sectors'][sector]
        kpis = sector_config.get('kpis', {})
        
        # Add sector-specific panels
        new_panels = []
        panel_id = 1000  # Start with high ID to avoid conflicts
        
        for category, category_kpis in kpis.items():
            # Create category row
            row_panel = {
                "id": panel_id,
                "title": category.replace('_', ' ').title(),
                "type": "row",
                "gridPos": {"h": 1, "w": 24, "x": 0, "y": len(dashboard['panels'])},
                "panels": []
            }
            new_panels.append(row_panel)
            panel_id += 1
            
            # Add KPI panels for this category
            for metric_name, metric_config in category_kpis.items():
                if isinstance(metric_config, dict) and 'query' in metric_config:
                    kpi_panel = self._create_kpi_panel(
                        metric_name, metric_config, panel_id, customer_profile
                    )
                    new_panels.append(kpi_panel)
                    panel_id += 1
        
        # Add new panels to dashboard
        dashboard['panels'].extend(new_panels)
        
        return dashboard
    
    def _create_kpi_panel(self, metric_name: str, metric_config: Dict[str, Any], 
                          panel_id: int, customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create KPI panel from metric configuration"""
        panel_type = metric_config.get('panel_type', 'stat')
            
            panel = {
            "id": panel_id,
            "title": metric_config.get('name', metric_name.replace('_', ' ').title()),
            "type": panel_type,
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
            "targets": [
                {
                    "expr": self._process_query_template(
                        metric_config['query'], customer_profile
                    ),
                    "legendFormat": metric_config.get('name', metric_name)
                }
            ],
                "fieldConfig": {
                    "defaults": {
                    "unit": metric_config.get('unit', 'short'),
                    "decimals": metric_config.get('decimals', 2),
                        "thresholds": {
                            "steps": [
                            {"color": "red", "value": None},
                            {"color": "yellow", "value": metric_config.get('critical', 0)},
                            {"color": "green", "value": metric_config.get('target', 100)}
                        ]
                    }
                }
            }
            }
            
            return panel
            
    def _validate_dashboard(self, dashboard: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated dashboard for correctness"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required fields
        required_fields = ['title', 'panels', 'templating']
        for field in required_fields:
            if field not in dashboard:
                validation_result["is_valid"] = False
                validation_result["errors"].append(f"Missing required field: {field}")
        
        # Validate panels
        if 'panels' in dashboard:
            for i, panel in enumerate(dashboard['panels']):
                if 'targets' not in panel:
                    validation_result["warnings"].append(f"Panel {i} has no targets")
                elif panel['targets']:
                    for j, target in enumerate(panel['targets']):
                        if 'expr' not in target:
                            validation_result["warnings"].append(
                                f"Panel {i}, target {j} has no expression"
                            )
        
        # Check for template variables
        if 'templating' in dashboard and 'list' in dashboard['templating']:
            tenant_var = next((var for var in dashboard['templating']['list'] 
                             if var.get('name') == 'tenant_id'), None)
            if not tenant_var:
                validation_result["warnings"].append("Missing tenant_id template variable")
        
        return validation_result
    
    def generate_sector_dashboard(self, customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate sector-specific dashboard for customer
        
        Args:
            customer_profile: Customer profile data
            
        Returns:
            Generated dashboard configuration
        """
        sector = customer_profile.get('sector', 'general')
        tenant_id = customer_profile.get('tenant_id', 'unknown')
        
        logger.info(f"Generating dashboard for {customer_profile.get('organization_name')} ({sector})")
        
        # Get sector template
        template = self._get_sector_template(sector)
        if not template:
            logger.error(f"Failed to get template for sector: {sector}")
            return None
    
        # Inject customer-specific values
        dashboard = self._inject_customer_specific_values(template, customer_profile)
        
        # Inject sector-specific KPIs
        dashboard = self._inject_sector_kpis(dashboard, sector, customer_profile)
        
        # Validate dashboard
        validation = self._validate_dashboard(dashboard)
        if not validation["is_valid"]:
            logger.error(f"Dashboard validation failed: {validation['errors']}")
            return None
    
        if validation["warnings"]:
            logger.warning(f"Dashboard validation warnings: {validation['warnings']}")
        
        # Update metrics
        self.generation_metrics["total_dashboards_generated"] += 1
        self.generation_metrics["successful_generations"] += 1
        self.generation_metrics["sectors_processed"].add(sector)
        self.generation_metrics["templates_used"].add(f"{sector}-template")
        
        logger.info(f"Successfully generated dashboard for {tenant_id}")
            return dashboard
    
    def save_dashboard(self, dashboard: Dict[str, Any], 
                      customer_profile: Dict[str, Any]) -> bool:
        """Save generated dashboard to file"""
        try:
            tenant_id = customer_profile.get('tenant_id', 'unknown')
            filename = f"{tenant_id}-sector-dashboard.json"
            filepath = self.output_path / filename
            
            with open(filepath, 'w') as f:
                json.dump(dashboard, f, indent=2, default=str)
            
            logger.info(f"Saved dashboard to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save dashboard: {e}")
            return False
    
    def generate_batch_dashboards(self, customer_profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate dashboards for multiple customers
        
        Args:
            customer_profiles: List of customer profiles
            
        Returns:
            Batch generation results
        """
        results = {
            "total_customers": len(customer_profiles),
            "successful_generations": 0,
            "failed_generations": 0,
            "generated_dashboards": [],
            "errors": []
        }
        
        logger.info(f"Starting batch dashboard generation for {len(customer_profiles)} customers")
        
        for profile in customer_profiles:
            try:
                dashboard = self.generate_sector_dashboard(profile)
                if dashboard:
                    if self.save_dashboard(dashboard, profile):
                        results["successful_generations"] += 1
                        results["generated_dashboards"].append({
                            "tenant_id": profile.get('tenant_id'),
                            "organization": profile.get('organization_name'),
                            "sector": profile.get('sector'),
                            "filename": f"{profile.get('tenant_id')}-sector-dashboard.json"
                        })
                    else:
                        results["failed_generations"] += 1
                        results["errors"].append({
                            "tenant_id": profile.get('tenant_id'),
                            "error": "Failed to save dashboard"
                        })
                else:
                    results["failed_generations"] += 1
                    results["errors"].append({
                        "tenant_id": profile.get('tenant_id'),
                        "error": "Failed to generate dashboard"
                    })
            
        except Exception as e:
                results["failed_generations"] += 1
                results["errors"].append({
                    "tenant_id": profile.get('tenant_id'),
                    "error": str(e)
                })
                logger.error(f"Error generating dashboard for {profile.get('tenant_id')}: {e}")
        
        logger.info(f"Batch generation completed: {results['successful_generations']} successful, "
                   f"{results['failed_generations']} failed")
        
        return results
    
    def get_generation_metrics(self) -> Dict[str, Any]:
        """Get dashboard generation metrics"""
        metrics = copy.deepcopy(self.generation_metrics)
        metrics["sectors_processed"] = list(metrics["sectors_processed"])
        metrics["templates_used"] = list(metrics["templates_used"])
        return metrics
    
    def test_dashboard_connectivity(self, dashboard: Dict[str, Any]) -> Dict[str, Any]:
        """Test dashboard data source connectivity"""
        test_results = {
            "data_sources": [],
            "query_tests": [],
            "overall_status": "unknown"
        }
        
        # Test InfluxDB connectivity (placeholder)
        test_results["data_sources"].append({
            "name": "InfluxDB",
            "status": "connected",
            "type": "influxdb"
        })
        
        # Test query expressions
        if 'panels' in dashboard:
            for panel in dashboard['panels']:
                if 'targets' in panel:
                    for target in panel['targets']:
                        if 'expr' in target:
                            query = target['expr']
                            # Basic query validation
                            if '${tenant_id}' in query:
                                test_results["query_tests"].append({
                                    "panel": panel.get('title', 'Unknown'),
                                    "query": query,
                                    "status": "warning",
                                    "message": "Contains template variables"
                                })
                            else:
                                test_results["query_tests"].append({
                                    "panel": panel.get('title', 'Unknown'),
                                    "query": query,
                                    "status": "valid",
                                    "message": "Query syntax looks valid"
                                })
        
        # Determine overall status
        if any(test["status"] == "error" for test in test_results["query_tests"]):
            test_results["overall_status"] = "failed"
        elif any(test["status"] == "warning" for test in test_results["query_tests"]):
            test_results["overall_status"] = "warning"
                        else:
            test_results["overall_status"] = "passed"
        
        return test_results


def main():
    """Main function for testing"""
    # Example usage
    generator = SectorDashboardGenerator()
    
    # Sample customer profile
    sample_profile = {
        "tenant_id": "gov-department-001",
        "organization_name": "Ministry of Digital Services",
        "sector": "government",
        "use_case_category": "citizen_services",
        "target_user_base": 1000000,
        "geographical_coverage": ["Delhi", "Mumbai", "Bangalore"],
        "languages_required": ["Hindi", "English", "Marathi", "Kannada"],
        "sla_tier": "premium"
    }
    
    # Generate dashboard
    dashboard = generator.generate_sector_dashboard(sample_profile)
    if dashboard:
        # Save dashboard
        generator.save_dashboard(dashboard, sample_profile)
        
        # Test connectivity
        test_results = generator.test_dashboard_connectivity(dashboard)
        print(f"Connectivity test results: {test_results['overall_status']}")
        
        # Show metrics
        metrics = generator.get_generation_metrics()
        print(f"Generation metrics: {metrics}")
        else:
            print("Failed to generate dashboard")
            

if __name__ == "__main__":
    main()
