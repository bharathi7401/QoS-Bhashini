#!/usr/bin/env python3
"""
Grafana Organization Setup Script for Multi-Tenant Configuration
Automates creation of provider and customer organizations with proper RBAC
"""

import os
import sys
import json
import requests
import yaml
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GrafanaOrganizationManager:
    """Manages Grafana organizations and user assignments for multi-tenancy"""
    
    def __init__(self):
        self.grafana_url = "http://localhost:3000"
        self.admin_user = os.getenv('GRAFANA_ADMIN_USER', 'admin')
        self.admin_password = os.getenv('GRAFANA_ADMIN_PASSWORD', 'admin')
        self.session = requests.Session()
        self.auth_token = None
        
    def authenticate(self):
        """Authenticate with Grafana admin credentials"""
        try:
            auth_url = f"{self.grafana_url}/api/auth/keys"
            auth_data = {
                "name": "setup-script",
                "role": "Admin"
            }
            
            response = self.session.post(
                auth_url,
                json=auth_data,
                auth=(self.admin_user, self.admin_password)
            )
            
            if response.status_code == 200:
                self.auth_token = response.json()['key']
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                print("✅ Successfully authenticated with Grafana")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def create_organization(self, name, org_id=None):
        """Create a new Grafana organization"""
        try:
            org_data = {"name": name}
            if org_id:
                org_data["orgId"] = org_id
                
            response = self.session.post(
                f"{self.grafana_url}/api/orgs",
                json=org_data
            )
            
            if response.status_code == 200:
                org_info = response.json()
                print(f"✅ Created organization: {name} (ID: {org_info['orgId']})")
                return org_info
            elif response.status_code == 409:
                print(f"⚠️  Organization {name} already exists")
                # Try to get existing org
                return self.get_organization_by_name(name)
            else:
                print(f"❌ Failed to create organization {name}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating organization {name}: {str(e)}")
            return None
    
    def get_organization_by_name(self, name):
        """Get organization by name"""
        try:
            response = self.session.get(f"{self.grafana_url}/api/orgs")
            if response.status_code == 200:
                orgs = response.json()
                for org in orgs:
                    if org['name'] == name:
                        return org
            return None
        except Exception as e:
            print(f"❌ Error getting organization {name}: {str(e)}")
            return None
    
    def create_user(self, email, password, name, org_id, role="Viewer"):
        """Create a new user in the specified organization"""
        try:
            user_data = {
                "email": email,
                "password": password,
                "name": name,
                "login": email.split('@')[0],
                "orgId": org_id
            }
            
            response = self.session.post(
                f"{self.grafana_url}/api/admin/users",
                json=user_data
            )
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ Created user: {email} in org {org_id}")
                
                # Assign user to organization with role
                self.assign_user_to_org(user_info['id'], org_id, role)
                return user_info
            else:
                print(f"❌ Failed to create user {email}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating user {email}: {str(e)}")
            return None
    
    def assign_user_to_org(self, user_id, org_id, role="Viewer"):
        """Assign user to organization with specific role"""
        try:
            # First, add user to organization
            add_data = {"userId": user_id}
            response = self.session.post(
                f"{self.grafana_url}/api/orgs/{org_id}/users",
                json=add_data
            )
            
            if response.status_code == 200:
                # Then, update user role in organization
                role_data = {"role": role}
                response = self.session.patch(
                    f"{self.grafana_url}/api/orgs/{org_id}/users/{user_id}",
                    json=role_data
                )
                
                if response.status_code == 200:
                    print(f"✅ Assigned user {user_id} to org {org_id} with role {role}")
                    return True
                else:
                    print(f"⚠️  User added to org but role assignment failed: {response.status_code}")
                    return False
            else:
                print(f"❌ Failed to add user to organization: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error assigning user to org: {str(e)}")
            return False
    
    def setup_provider_organization(self):
        """Setup the provider organization with admin users"""
        print("\n🏢 Setting up Provider Organization...")
        
        provider_org_name = os.getenv('GRAFANA_PROVIDER_ORG_NAME', 'Bhashini-Provider')
        provider_org = self.create_organization(provider_org_name)
        
        if provider_org:
            org_id = provider_org['orgId']
            
            # Create provider admin user
            provider_admin_email = "provider.admin@bhashini.com"
            provider_admin_password = "ProviderAdmin123!"
            provider_admin_name = "Provider Admin"
            
            self.create_user(
                provider_admin_email,
                provider_admin_password,
                provider_admin_name,
                org_id,
                "Admin"
            )
            
            # Create provider analyst user
            provider_analyst_email = "provider.analyst@bhashini.com"
            provider_analyst_password = "ProviderAnalyst123!"
            provider_analyst_name = "Provider Analyst"
            
            self.create_user(
                provider_analyst_email,
                provider_analyst_password,
                provider_analyst_name,
                org_id,
                "Editor"
            )
            
            return org_id
        return None
    
    def setup_customer_organizations(self):
        """Setup customer organizations with appropriate users"""
        print("\n👥 Setting up Customer Organizations...")
        
        customer_orgs = []
        customer_prefix = os.getenv('GRAFANA_CUSTOMER_ORG_PREFIX', 'Customer')
        
        for i in range(1, 4):  # Create 3 customer orgs
            org_name = f"{customer_prefix}-{i}"
            print(f"\n📋 Setting up {org_name}...")
            
            customer_org = self.create_organization(org_name)
            if customer_org:
                org_id = customer_org['orgId']
                
                # Create customer admin user
                customer_admin_email = f"customer{i}.admin@example.com"
                customer_admin_password = f"Customer{i}Admin123!"
                customer_admin_name = f"{org_name} Admin"
                
                self.create_user(
                    customer_admin_email,
                    customer_admin_password,
                    customer_admin_name,
                    org_id,
                    "Admin"
                )
                
                # Create customer viewer user
                customer_viewer_email = f"customer{i}.viewer@example.com"
                customer_viewer_password = f"Customer{i}Viewer123!"
                customer_viewer_name = f"{org_name} Viewer"
                
                self.create_user(
                    customer_viewer_email,
                    customer_viewer_password,
                    customer_viewer_name,
                    org_id,
                    "Viewer"
                )
                
                customer_orgs.append({
                    'name': org_name,
                    'id': org_id,
                    'admin_email': customer_admin_email,
                    'admin_password': customer_admin_password,
                    'viewer_email': customer_viewer_email,
                    'viewer_password': customer_viewer_password
                })
        
        return customer_orgs
    
    def generate_credentials_report(self, provider_org_id, customer_orgs):
        """Generate a report of all created credentials"""
        print("\n📊 Generating Credentials Report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'provider_organization': {
                'name': os.getenv('GRAFANA_PROVIDER_ORG_NAME', 'Bhashini-Provider'),
                'id': provider_org_id,
                'users': [
                    {
                        'email': 'provider.admin@bhashini.com',
                        'password': 'ProviderAdmin123!',
                        'role': 'Admin'
                    },
                    {
                        'email': 'provider.analyst@bhashini.com',
                        'password': 'ProviderAnalyst123!',
                        'role': 'Editor'
                    }
                ]
            },
            'customer_organizations': customer_orgs
        }
        
        # Save report to file
        with open('grafana_credentials_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("✅ Credentials report saved to grafana_credentials_report.json")
        
        # Print summary
        print("\n🎯 Multi-Tenant Setup Summary:")
        print("=" * 50)
        print(f"Provider Organization: {report['provider_organization']['name']}")
        print(f"Customer Organizations: {len(customer_orgs)}")
        print(f"Total Users Created: {2 + len(customer_orgs) * 2}")
        print("\n📋 Access Credentials:")
        
        for user in report['provider_organization']['users']:
            print(f"  {user['email']} ({user['role']}) - {user['password']}")
        
        for org in customer_orgs:
            print(f"\n  {org['name']}:")
            print(f"    Admin: {org['admin_email']} - {org['admin_password']}")
            print(f"    Viewer: {org['viewer_email']} - {org['viewer_password']}")
    
    def run_setup(self):
        """Run the complete organization setup"""
        print("🚀 Grafana Multi-Tenant Organization Setup")
        print("=" * 50)
        
        # Authenticate
        if not self.authenticate():
            print("❌ Setup failed - authentication required")
            return False
        
        # Setup provider organization
        provider_org_id = self.setup_provider_organization()
        if not provider_org_id:
            print("❌ Setup failed - provider organization creation failed")
            return False
        
        # Setup customer organizations
        customer_orgs = self.setup_customer_organizations()
        if not customer_orgs:
            print("❌ Setup failed - customer organization creation failed")
            return False
        
        # Generate credentials report
        self.generate_credentials_report(provider_org_id, customer_orgs)
        
        print("\n🎉 Multi-tenant organization setup completed successfully!")
        return True

def main():
    """Main entry point"""
    manager = GrafanaOrganizationManager()
    
    try:
        success = manager.run_setup()
        if success:
            print("\n✅ Setup completed successfully!")
            print("📚 Next steps:")
            print("  1. Update your .env file with the generated tokens")
            print("  2. Restart Grafana to apply new configurations")
            print("  3. Test authentication with the created users")
            print("  4. Run test-authentication.py to verify setup")
            return 0
        else:
            print("\n❌ Setup failed!")
            return 1
            
    except Exception as e:
        print(f"\n❌ Setup failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
