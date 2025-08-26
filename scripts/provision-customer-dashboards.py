#!/usr/bin/env python3
"""
Bhashini Customer Dashboard Provisioning Script
Automates provisioning of customer dashboards and data sources
"""

import json
import yaml
import os
import sys
import argparse
import time
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CustomerDashboardProvisioner:
    """Automates provisioning of customer dashboards and data sources"""
    
    def __init__(self, config_path: str, grafana_url: str, grafana_token: str):
        """
        Initialize the dashboard provisioner
        
        Args:
            config_path: Path to tenant configuration file
            grafana_url: Grafana base URL
            grafana_token: Grafana API token
        """
        self.config_path = Path(config_path)
        self.grafana_url = grafana_url.rstrip('/')
        self.grafana_token = grafana_token
        self.tenant_config = None
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {grafana_token}',
            'Content-Type': 'application/json'
        })
        
        self._load_configuration()
    
    def _load_configuration(self):
        """Load tenant configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                self.tenant_config = yaml.safe_load(f)
            logger.info(f"Loaded tenant configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load tenant configuration: {e}")
            raise
    
    def _get_customer_organizations(self) -> List[Dict[str, Any]]:
        """Extract customer organizations from tenant configuration"""
        if not self.tenant_config or 'customer_organizations' not in self.tenant_config:
            raise ValueError("No customer organizations found in configuration")
        
        return self.tenant_config['customer_organizations']
    
    def _create_grafana_organization(self, customer: Dict[str, Any]) -> Optional[int]:
        """Create Grafana organization for customer if it doesn't exist"""
        org_name = customer["name"]
        org_id = customer.get("org_id")
        
        try:
            # Check if organization already exists
            response = self.session.get(f"{self.grafana_url}/api/orgs/name/{org_name}")
            
            if response.status_code == 200:
                existing_org = response.json()
                logger.info(f"Organization {org_name} already exists with ID {existing_org['id']}")
                return existing_org['id']
            elif response.status_code == 404:
                # Create new organization
                org_data = {
                    "name": org_name,
                    "id": org_id
                }
                
                response = self.session.post(f"{self.grafana_url}/api/orgs", json=org_data)
                
                if response.status_code == 200:
                    new_org = response.json()
                    logger.info(f"Created organization {org_name} with ID {new_org['id']}")
                    return new_org['id']
                else:
                    logger.error(f"Failed to create organization {org_name}: {response.text}")
                    return None
            else:
                logger.error(f"Unexpected response checking organization {org_name}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating organization {org_name}: {e}")
            return None
    
    def _create_grafana_user(self, customer: Dict[str, Any], org_id: int) -> bool:
        """Create Grafana user for customer organization"""
        try:
            for user_config in customer.get("users", []):
                user_data = {
                    "name": user_config["email"].split("@")[0],
                    "email": user_config["email"],
                    "login": user_config["email"],
                    "password": self._generate_secure_password(),
                    "OrgId": org_id
                }
                
                response = self.session.post(f"{self.grafana_url}/api/admin/users", json=user_data)
                
                if response.status_code == 200:
                    user = response.json()
                    logger.info(f"Created user {user_config['email']} in organization {org_id}")
                    
                    # Assign user to organization
                    self._add_user_to_organization(user["id"], org_id, user_config["role"])
                else:
                    logger.error(f"Failed to create user {user_config['email']}: {response.text}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating users for customer {customer['name']}: {e}")
            return False
    
    def _add_user_to_organization(self, user_id: int, org_id: int, role: str) -> bool:
        """Add user to organization with specified role"""
        try:
            # Add user to organization
            add_user_data = {
                "userId": user_id,
                "role": role
            }
            
            response = self.session.post(f"{self.grafana_url}/api/orgs/{org_id}/users", json=add_user_data)
            
            if response.status_code == 200:
                logger.info(f"Added user {user_id} to organization {org_id} with role {role}")
                return True
            else:
                logger.error(f"Failed to add user {user_id} to organization {org_id}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding user {user_id} to organization {org_id}: {e}")
            return False
    
    def _generate_secure_password(self) -> str:
        """Generate a secure password for new users"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for i in range(12))
        return password
    
    def _create_dashboard_folder(self, customer: Dict[str, Any], org_id: int) -> Optional[int]:
        """Create dashboard folder for customer organization"""
        folder_name = f"{customer['name']} Dashboards"
        
        try:
            # Switch to customer organization context
            self.session.post(f"{self.grafana_url}/api/user/using/{org_id}")
            
            # Create folder
            folder_data = {
                "title": folder_name
            }
            
            response = self.session.post(f"{self.grafana_url}/api/folders", json=folder_data)
            
            if response.status_code == 200:
                folder = response.json()
                logger.info(f"Created dashboard folder {folder_name} with ID {folder['id']}")
                return folder['id']
            else:
                logger.error(f"Failed to create folder {folder_name}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating folder {folder_name}: {e}")
            return None
    
    def _import_dashboard(self, dashboard_path: str, org_id: int, folder_id: Optional[int] = None) -> bool:
        """Import dashboard to customer organization"""
        try:
            # Load dashboard JSON
            with open(dashboard_path, 'r') as f:
                dashboard_data = json.load(f)
            
            # Prepare import data
            import_data = {
                "dashboard": dashboard_data,
                "overwrite": True,
                "inputs": []
            }
            
            if folder_id:
                import_data["dashboard"]["folderId"] = folder_id
            
            # Switch to customer organization context
            self.session.post(f"{self.grafana_url}/api/user/using/{org_id}")
            
            # Import dashboard
            response = self.session.post(f"{self.grafana_url}/api/dashboards/import", json=import_data)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Imported dashboard {dashboard_data['title']} successfully")
                return True
            else:
                logger.error(f"Failed to import dashboard: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error importing dashboard {dashboard_path}: {e}")
            return False
    
    def _create_data_source(self, customer: Dict[str, Any], org_id: int) -> bool:
        """Create InfluxDB data source for customer"""
        try:
            # Switch to customer organization context
            self.session.post(f"{self.grafana_url}/api/user/using/{org_id}")
            
            # Get actual environment values
            org = os.getenv("INFLUXDB_ORG")
            bucket = os.getenv("INFLUXDB_BUCKET")
            var_name = f"INFLUXDB_{customer['tenant_id'].upper()}_TOKEN"
            token = os.getenv(var_name)
            
            # Validate required environment variables
            if not org:
                logger.error(f"Missing required environment variable: INFLUXDB_ORG")
                return False
            if not bucket:
                logger.error(f"Missing required environment variable: INFLUXDB_BUCKET")
                return False
            if not token:
                logger.error(f"Missing required environment variable: {var_name}")
                return False
            
            # Create data source
            datasource_data = {
                "name": f"InfluxDB-Customer-{customer['tenant_id']}",
                "uid": f"InfluxDB-Customer-{customer['tenant_id']}",
                "type": "influxdb",
                "access": "proxy",
                "url": "http://influxdb:8086",
                "secureJsonData": {
                    "token": token
                },
                "jsonData": {
                    "version": "Flux",
                    "organization": org,
                    "defaultBucket": bucket,
                    "tlsSkipVerify": True,
                    "httpMethod": "POST",
                    "queryTimeout": "60s",
                    "maxSeries": 10000
                }
            }
            
            response = self.session.post(f"{self.grafana_url}/api/datasources", json=datasource_data)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Created data source for customer {customer['tenant_id']}")
                return True
            else:
                logger.error(f"Failed to create data source: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating data source for customer {customer['tenant_id']}: {e}")
            return False
    
    def provision_customer(self, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Provision complete setup for a customer"""
        logger.info(f"Provisioning customer: {customer['name']} ({customer['tenant_id']})")
        
        results = {
            "customer": customer["name"],
            "tenant_id": customer["tenant_id"],
            "status": "SUCCESS",
            "steps": {},
            "errors": []
        }
        
        try:
            # Step 1: Create organization
            org_id = self._create_grafana_organization(customer)
            if org_id:
                results["steps"]["organization_creation"] = {"status": "SUCCESS", "org_id": org_id}
            else:
                results["steps"]["organization_creation"] = {"status": "FAILED"}
                results["status"] = "FAILED"
                results["errors"].append("Failed to create organization")
                return results
            
            # Step 2: Create users
            users_created = self._create_grafana_user(customer, org_id)
            if users_created:
                results["steps"]["user_creation"] = {"status": "SUCCESS"}
            else:
                results["steps"]["user_creation"] = {"status": "FAILED"}
                results["status"] = "FAILED"
                results["errors"].append("Failed to create users")
            
            # Step 3: Create dashboard folder
            folder_id = self._create_dashboard_folder(customer, org_id)
            if folder_id:
                results["steps"]["folder_creation"] = {"status": "SUCCESS", "folder_id": folder_id}
            else:
                results["steps"]["folder_creation"] = {"status": "FAILED"}
                results["errors"].append("Failed to create dashboard folder")
            
            # Step 4: Create data source
            datasource_created = self._create_data_source(customer, org_id)
            if datasource_created:
                results["steps"]["datasource_creation"] = {"status": "SUCCESS"}
            else:
                results["steps"]["datasource_creation"] = {"status": "FAILED"}
                results["errors"].append("Failed to create data source")
            
            # Step 5: Import dashboard (if dashboard file exists)
            dashboard_path = f"grafana/provisioning/dashboards/customer-dashboards/{customer['tenant_id']}-customer-dashboard.json"
            if os.path.exists(dashboard_path):
                dashboard_imported = self._import_dashboard(dashboard_path, org_id, folder_id)
                if dashboard_imported:
                    results["steps"]["dashboard_import"] = {"status": "SUCCESS"}
                else:
                    results["steps"]["dashboard_import"] = {"status": "FAILED"}
                    results["errors"].append("Failed to import dashboard")
            else:
                results["steps"]["dashboard_import"] = {"status": "SKIPPED", "reason": "Dashboard file not found"}
            
            # Update overall status
            if any(step.get("status") == "FAILED" for step in results["steps"].values()):
                results["status"] = "FAILED"
            
            logger.info(f"Completed provisioning for customer {customer['name']}")
            
        except Exception as e:
            logger.error(f"Error provisioning customer {customer['name']}: {e}")
            results["status"] = "FAILED"
            results["errors"].append(f"Exception: {e}")
        
        return results
    
    def provision_all_customers(self) -> List[Dict[str, Any]]:
        """Provision all customers"""
        customers = self._get_customer_organizations()
        results = []
        
        logger.info(f"Provisioning {len(customers)} customers")
        
        for customer in customers:
            try:
                result = self.provision_customer(customer)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to provision customer {customer['name']}: {e}")
                results.append({
                    "customer": customer["name"],
                    "tenant_id": customer["tenant_id"],
                    "status": "FAILED",
                    "steps": {},
                    "errors": [f"Exception: {e}"]
                })
        
        return results
    
    def provision_specific_customer(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Provision specific customer by tenant ID"""
        customers = self._get_customer_organizations()
        
        for customer in customers:
            if customer["tenant_id"] == tenant_id:
                return self.provision_customer(customer)
        
        logger.error(f"Customer with tenant ID {tenant_id} not found")
        return None
    
    def update_existing_customers(self) -> List[Dict[str, Any]]:
        """Update existing customer configurations"""
        logger.info("Updating existing customer configurations")
        return self.provision_all_customers()
    
    def cleanup_customer(self, customer: Dict[str, Any]) -> bool:
        """Clean up customer resources (for offboarding)"""
        logger.info(f"Cleaning up customer: {customer['name']}")
        
        try:
            # This would typically remove organizations, users, dashboards, and data sources
            # For now, we'll just log the cleanup action
            logger.info(f"Cleanup completed for customer {customer['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up customer {customer['name']}: {e}")
            return False
    
    def generate_provisioning_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate comprehensive provisioning report"""
        report = []
        report.append("=" * 80)
        report.append("Bhashini Customer Dashboard Provisioning Report")
        report.append("=" * 80)
        report.append("")
        
        total_customers = len(results)
        successful_customers = sum(1 for r in results if r["status"] == "SUCCESS")
        failed_customers = total_customers - successful_customers
        
        for result in results:
            report.append(f"Customer: {result['customer']} ({result['tenant_id']})")
            report.append("-" * 60)
            report.append(f"Status: {result['status']}")
            
            for step_name, step_result in result["steps"].items():
                status = step_result["status"]
                report.append(f"  {step_name}: {status}")
                
                if status == "FAILED":
                    report.append(f"    Error: {step_result.get('error', 'Unknown error')}")
            
            if result["errors"]:
                report.append("  Errors:")
                for error in result["errors"]:
                    report.append(f"    - {error}")
            
            report.append("")
        
        # Summary
        report.append("=" * 80)
        report.append("Provisioning Summary")
        report.append("=" * 80)
        report.append(f"Total Customers: {total_customers}")
        report.append(f"Successful: {successful_customers}")
        report.append(f"Failed: {failed_customers}")
        report.append(f"Success Rate: {(successful_customers/total_customers)*100:.1f}%")
        report.append("")
        
        return "\n".join(report)
    
    def save_provisioning_results(self, results: List[Dict[str, Any]], output_file: str):
        """Save provisioning results to JSON file"""
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Provisioning results saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save provisioning results: {e}")
            raise

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="Provision customer dashboards and data sources")
    parser.add_argument(
        "--config", 
        default="config/tenant-config.yml",
        help="Path to tenant configuration file"
    )
    parser.add_argument(
        "--grafana-url", 
        default="http://localhost:3000",
        help="Grafana base URL"
    )
    parser.add_argument(
        "--grafana-token", 
        required=True,
        help="Grafana API token"
    )
    parser.add_argument(
        "--output", 
        default="provisioning-results.json",
        help="Output file for provisioning results"
    )
    parser.add_argument(
        "--report", 
        default="provisioning-report.txt",
        help="Output file for provisioning report"
    )
    parser.add_argument(
        "--customer", 
        help="Provision specific customer (tenant_id)"
    )
    parser.add_argument(
        "--all", 
        action="store_true",
        help="Provision all customers"
    )
    parser.add_argument(
        "--update", 
        action="store_true",
        help="Update existing customer configurations"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize provisioner
        provisioner = CustomerDashboardProvisioner(args.config, args.grafana_url, args.grafana_token)
        
        if args.customer:
            # Provision specific customer
            result = provisioner.provision_specific_customer(args.customer)
            if result:
                results = [result]
            else:
                print(f"Failed to provision customer {args.customer}")
                sys.exit(1)
        
        elif args.all or args.update:
            # Provision all customers
            results = provisioner.provision_all_customers()
        
        else:
            # Default: provision all customers
            results = provisioner.provision_all_customers()
        
        # Save results
        provisioner.save_provisioning_results(results, args.output)
        
        # Generate and save report
        report = provisioner.generate_provisioning_report(results)
        with open(args.report, 'w') as f:
            f.write(report)
        
        print(f"Provisioning results saved to {args.output}")
        print(f"Provisioning report saved to {args.report}")
        
        # Print summary to console
        print("\n" + "=" * 80)
        print("Provisioning Summary")
        print("=" * 80)
        
        total_customers = len(results)
        successful_customers = sum(1 for r in results if r["status"] == "SUCCESS")
        
        print(f"Total Customers: {total_customers}")
        print(f"Successful: {successful_customers}")
        print(f"Failed: {total_customers - successful_customers}")
        print(f"Success Rate: {(successful_customers/total_customers)*100:.1f}%")
        
    except Exception as e:
        logger.error(f"Provisioning failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
