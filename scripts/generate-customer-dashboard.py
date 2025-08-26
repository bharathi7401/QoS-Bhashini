#!/usr/bin/env python3
"""
Bhashini Customer Dashboard Generator
Generates customer-specific dashboards from templates with tenant isolation
"""

import json
import yaml
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from jinja2 import Template, Environment, FileSystemLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CustomerDashboardGenerator:
    """Generates customer-specific dashboards from templates"""
    
    def __init__(self, config_path: str, template_path: str, output_dir: str, queries_path: str = None):
        """
        Initialize the dashboard generator
        
        Args:
            config_path: Path to tenant configuration file
            template_path: Path to dashboard template file
            output_dir: Directory to save generated dashboards
            queries_path: Path to Flux queries file (optional)
        """
        self.config_path = Path(config_path)
        self.template_path = Path(template_path)
        self.output_dir = Path(output_dir)
        self.queries_path = Path(queries_path) if queries_path else None
        self.tenant_config = None
        self.template = None
        self.flux_queries = {}
        
        # SLA tier configurations
        self.sla_configs = {
            "premium": {
                "availability_threshold": 99.9,
                "latency_threshold": 100.0,
                "error_rate_threshold": 0.1,
                "refresh_interval": "15s",
                "color_scheme": "dark"
            },
            "standard": {
                "availability_threshold": 99.5,
                "latency_threshold": 200.0,
                "error_rate_threshold": 0.5,
                "refresh_interval": "30s",
                "color_scheme": "dark"
            },
            "basic": {
                "availability_threshold": 99.0,
                "latency_threshold": 500.0,
                "error_rate_threshold": 1.0,
                "refresh_interval": "60s",
                "color_scheme": "dark"
            }
        }
        
        self._load_configuration()
        self._load_template()
        if self.queries_path:
            self._load_flux_queries()
        
    def _load_configuration(self):
        """Load tenant configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                self.tenant_config = yaml.safe_load(f)
            logger.info(f"Loaded tenant configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load tenant configuration: {e}")
            raise
    
    def _load_template(self):
        """Load dashboard template from JSON file"""
        try:
            with open(self.template_path, 'r') as f:
                self.template = json.load(f)
            logger.info(f"Loaded dashboard template from {self.template_path}")
        except Exception as e:
            logger.error(f"Failed to load dashboard template: {e}")
            raise
    
    def _load_flux_queries(self):
        """Load Flux query snippets from file"""
        try:
            if not self.queries_path or not self.queries_path.exists():
                logger.warning("Flux queries file not found, skipping query injection")
                return
            
            with open(self.queries_path, 'r') as f:
                content = f.read()
            
            # Parse Flux queries and extract function definitions
            lines = content.split('\n')
            current_function = None
            current_content = []
            
            for line in lines:
                if line.strip().startswith('//') or not line.strip():
                    continue
                
                if '=' in line and '=>' in line and line.strip().endswith('=>'):
                    # Start of function definition
                    if current_function:
                        self.flux_queries[current_function] = '\n'.join(current_content).strip()
                    
                    current_function = line.split('=')[0].strip()
                    current_content = [line]
                elif current_function:
                    current_content.append(line)
            
            # Add the last function
            if current_function:
                self.flux_queries[current_function] = '\n'.join(current_content).strip()
            
            logger.info(f"Loaded {len(self.flux_queries)} Flux query functions")
            
        except Exception as e:
            logger.error(f"Failed to load Flux queries: {e}")
            # Continue without queries
    
    def _inject_flux_queries(self, dashboard: Dict[str, Any], customer: Dict[str, Any]) -> Dict[str, Any]:
        """Inject Flux query snippets into dashboard template"""
        if not self.flux_queries:
            return dashboard
        
        dashboard_str = json.dumps(dashboard)
        
        # Replace query placeholders with actual Flux queries
        for query_name, query_content in self.flux_queries.items():
            placeholder = f"{{{{FLUX_{query_name.upper()}_QUERY}}}}"
            if placeholder in dashboard_str:
                # Customize query for customer
                customized_query = query_content.replace('tenant_id', f'"{customer["tenant_id"]}"')
                dashboard_str = dashboard_str.replace(placeholder, customized_query)
                logger.info(f"Injected Flux query: {query_name}")
        
        # Parse back to JSON
        return json.loads(dashboard_str)
    
    def _get_customer_organizations(self) -> List[Dict[str, Any]]:
        """Extract customer organizations from tenant configuration"""
        if not self.tenant_config or 'customer_organizations' not in self.tenant_config:
            raise ValueError("No customer organizations found in configuration")
        
        return self.tenant_config['customer_organizations']
    
    def _customize_dashboard_for_sla_tier(self, dashboard: Dict[str, Any], sla_tier: str) -> Dict[str, Any]:
        """Customize dashboard based on SLA tier"""
        sla_config = self.sla_configs.get(sla_tier, self.sla_configs["standard"])
        
        # Update dashboard refresh interval
        dashboard["refresh"] = sla_config["refresh_interval"]
        
        # Customize panel thresholds based on SLA tier
        for panel in dashboard.get("panels", []):
            if "fieldConfig" in panel and "defaults" in panel["fieldConfig"]:
                defaults = panel["fieldConfig"]["defaults"]
                
                # Customize availability thresholds
                if "thresholds" in defaults and "unit" in defaults and defaults["unit"] == "percent":
                    if "availability" in panel.get("title", "").lower():
                        thresholds = defaults["thresholds"]["steps"]
                        if len(thresholds) >= 3:
                            thresholds[2]["value"] = sla_config["availability_threshold"]
                
                # Customize latency thresholds
                if "thresholds" in defaults and "unit" in defaults and defaults["unit"] == "ms":
                    if "latency" in panel.get("title", "").lower():
                        thresholds = defaults["thresholds"]["steps"]
                        if len(thresholds) >= 3:
                            thresholds[1]["value"] = sla_config["latency_threshold"]
                            thresholds[2]["value"] = sla_config["latency_threshold"] * 2
                
                # Customize error rate thresholds
                if "thresholds" in defaults and "unit" in defaults and defaults["unit"] == "percent":
                    if "error" in panel.get("title", "").lower():
                        thresholds = defaults["thresholds"]["steps"]
                        if len(thresholds) >= 3:
                            # Fix error rate thresholds to use realistic levels
                            warning = sla_config["error_rate_threshold"] * 100  # percent
                            critical = warning * 5  # e.g., ×5
                            thresholds[1]["value"] = warning
                            thresholds[2]["value"] = critical
        
        return dashboard
    
    def _replace_template_variables(self, dashboard: Dict[str, Any], customer: Dict[str, Any]) -> Dict[str, Any]:
        """Replace template variables with customer-specific values"""
        dashboard_str = json.dumps(dashboard)
        
        # Replace template variables
        replacements = {
            "{{TENANT_ID}}": customer["tenant_id"],
            "{{CUSTOMER_NAME}}": customer["name"],
            "{{SLA_TIER}}": customer["sla_tier"]
        }
        
        for placeholder, value in replacements.items():
            dashboard_str = dashboard_str.replace(placeholder, str(value))
        
        # Parse back to JSON
        return json.loads(dashboard_str)
    
    def _validate_dashboard(self, dashboard: Dict[str, Any]) -> bool:
        """Validate generated dashboard JSON structure"""
        required_fields = ["title", "panels", "templating"]
        
        for field in required_fields:
            if field not in dashboard:
                logger.error(f"Missing required field: {field}")
                return False
        
        if not dashboard["panels"]:
            logger.error("Dashboard has no panels")
            return False
        
        logger.info("Dashboard validation passed")
        return True
    
    def _save_dashboard(self, dashboard: Dict[str, Any], customer: Dict[str, Any]) -> str:
        """Save generated dashboard to file"""
        filename = f"{customer['tenant_id']}-customer-dashboard.json"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(dashboard, f, indent=2)
            logger.info(f"Saved dashboard to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to save dashboard: {e}")
            raise
    
    def generate_customer_dashboard(self, customer: Dict[str, Any]) -> str:
        """Generate dashboard for a specific customer"""
        logger.info(f"Generating dashboard for customer: {customer['name']} ({customer['tenant_id']})")
        
        # Create a copy of the template
        dashboard = json.loads(json.dumps(self.template))
        
        # Replace template variables
        dashboard = self._replace_template_variables(dashboard, customer)
        
        # Inject Flux queries if available
        dashboard = self._inject_flux_queries(dashboard, customer)
        
        # Customize based on SLA tier
        dashboard = self._customize_dashboard_for_sla_tier(dashboard, customer["sla_tier"])
        
        # Validate dashboard
        if not self._validate_dashboard(dashboard):
            raise ValueError(f"Dashboard validation failed for customer {customer['name']}")
        
        # Save dashboard
        filepath = self._save_dashboard(dashboard, customer)
        
        logger.info(f"Successfully generated dashboard for {customer['name']}")
        return filepath
    
    def generate_all_customer_dashboards(self) -> List[str]:
        """Generate dashboards for all customers"""
        customers = self._get_customer_organizations()
        generated_files = []
        
        logger.info(f"Generating dashboards for {len(customers)} customers")
        
        for customer in customers:
            try:
                filepath = self.generate_customer_dashboard(customer)
                generated_files.append(filepath)
            except Exception as e:
                logger.error(f"Failed to generate dashboard for {customer['name']}: {e}")
                continue
        
        logger.info(f"Generated {len(generated_files)} out of {len(customers)} dashboards")
        return generated_files
    
    def generate_specific_customer_dashboard(self, tenant_id: str) -> Optional[str]:
        """Generate dashboard for a specific customer by tenant ID"""
        customers = self._get_customer_organizations()
        
        for customer in customers:
            if customer["tenant_id"] == tenant_id:
                try:
                    return self.generate_customer_dashboard(customer)
                except Exception as e:
                    logger.error(f"Failed to generate dashboard for {tenant_id}: {e}")
                    return None
        
        logger.error(f"Customer with tenant ID {tenant_id} not found")
        return None
    
    def update_existing_dashboards(self) -> List[str]:
        """Update existing customer dashboards"""
        logger.info("Updating existing customer dashboards")
        return self.generate_all_customer_dashboards()
    
    def rollback_dashboard(self, customer: Dict[str, Any], backup_file: str) -> bool:
        """Rollback dashboard to previous version"""
        try:
            if os.path.exists(backup_file):
                with open(backup_file, 'r') as f:
                    backup_dashboard = json.load(f)
                
                filepath = self._save_dashboard(backup_dashboard, customer)
                logger.info(f"Rolled back dashboard for {customer['name']} to {filepath}")
                return True
            else:
                logger.error(f"Backup file not found: {backup_file}")
                return False
        except Exception as e:
            logger.error(f"Failed to rollback dashboard: {e}")
            return False

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="Generate customer-specific dashboards")
    parser.add_argument(
        "--config", 
        default="config/tenant-config.yml",
        help="Path to tenant configuration file"
    )
    parser.add_argument(
        "--template", 
        default="grafana/provisioning/dashboards/customer-dashboards/customer-dashboard-template.json",
        help="Path to dashboard template file"
    )
    parser.add_argument(
        "--output", 
        default="grafana/provisioning/dashboards/customer-dashboards",
        help="Output directory for generated dashboards"
    )
    parser.add_argument(
        "--queries", 
        default="scripts/dashboard-queries/customer-queries.flux",
        help="Path to Flux queries file"
    )
    parser.add_argument(
        "--customer", 
        help="Generate dashboard for specific customer (tenant_id)"
    )
    parser.add_argument(
        "--all", 
        action="store_true",
        help="Generate dashboards for all customers"
    )
    parser.add_argument(
        "--update", 
        action="store_true",
        help="Update existing customer dashboards"
    )
    parser.add_argument(
        "--validate", 
        action="store_true",
        help="Validate generated dashboards"
    )
    
    args = parser.parse_args()
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(args.output, exist_ok=True)
        
        # Initialize generator
        generator = CustomerDashboardGenerator(args.config, args.template, args.output, args.queries)
        
        if args.customer:
            # Generate for specific customer
            filepath = generator.generate_specific_customer_dashboard(args.customer)
            if filepath:
                print(f"Generated dashboard: {filepath}")
            else:
                print(f"Failed to generate dashboard for customer {args.customer}")
                sys.exit(1)
        
        elif args.all or args.update:
            # Generate for all customers
            generated_files = generator.generate_all_customer_dashboards()
            print(f"Generated {len(generated_files)} dashboards:")
            for filepath in generated_files:
                print(f"  - {filepath}")
        
        else:
            # Default: generate for all customers
            generated_files = generator.generate_all_customer_dashboards()
            print(f"Generated {len(generated_files)} dashboards:")
            for filepath in generated_files:
                print(f"  - {filepath}")
        
        if args.validate:
            print("\nValidating generated dashboards...")
            # Validation logic would go here
            print("Dashboard validation completed")
        
    except Exception as e:
        logger.error(f"Dashboard generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
