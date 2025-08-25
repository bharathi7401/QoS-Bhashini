#!/usr/bin/env python3
"""
Test User Creation Script for Multi-Tenant Testing
Creates test users with different roles and generates API keys for testing
"""

import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestUserManager:
    """Manages test user creation and API key generation for multi-tenant testing"""
    
    def __init__(self):
        self.grafana_url = "http://localhost:3000"
        self.admin_user = os.getenv('GRAFANA_ADMIN_USER', 'admin')
        self.admin_password = os.getenv('GRAFANA_ADMIN_PASSWORD', 'admin')
        self.session = requests.Session()
        self.created_users = []
        self.created_api_keys = []
        
    def authenticate(self):
        """Authenticate with Grafana admin credentials"""
        try:
            response = self.session.post(
                f"{self.grafana_url}/api/login",
                json={'user': self.admin_user, 'password': self.admin_password}
            )
            
            if response.status_code == 200:
                print("✅ Successfully authenticated with Grafana")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def create_test_user(self, email, password, name, org_id, role="Viewer"):
        """Create a test user in the specified organization"""
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
                print(f"✅ Created test user: {email} in org {org_id}")
                
                # Assign user to organization with role
                self.assign_user_to_org(user_info['id'], org_id, role)
                
                self.created_users.append({
                    'id': user_info['id'],
                    'email': email,
                    'name': name,
                    'org_id': org_id,
                    'role': role,
                    'password': password
                })
                
                return user_info
            else:
                print(f"❌ Failed to create test user {email}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating test user {email}: {str(e)}")
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
    
    def create_api_key(self, user_email, user_password, key_name, role="Viewer"):
        """Create API key for a specific user"""
        try:
            # Login as the user to create API key
            response = self.session.post(
                f"{self.grafana_url}/api/login",
                json={'user': user_email, 'password': user_password}
            )
            
            if response.status_code == 200:
                # Create API key
                key_data = {
                    "name": key_name,
                    "role": role
                }
                
                key_response = self.session.post(
                    f"{self.grafana_url}/api/auth/keys",
                    json=key_data
                )
                
                if key_response.status_code == 200:
                    key_info = key_response.json()
                    print(f"✅ Created API key '{key_name}' for {user_email}")
                    
                    self.created_api_keys.append({
                        'name': key_name,
                        'key': key_info['key'],
                        'user_email': user_email,
                        'role': role,
                        'expires': key_info.get('expiration')
                    })
                    
                    return key_info
                else:
                    print(f"❌ Failed to create API key for {user_email}: {key_response.status_code}")
                    return None
            else:
                print(f"❌ Failed to login as {user_email} for API key creation")
                return None
                
        except Exception as e:
            print(f"❌ Error creating API key for {user_email}: {str(e)}")
            return None
    
    def create_provider_test_users(self):
        """Create test users for provider organization"""
        print("\n🏢 Creating Provider Test Users...")
        
        # Get provider organization
        provider_org_name = os.getenv('GRAFANA_PROVIDER_ORG_NAME', 'Bhashini-Provider')
        provider_org = self.get_organization_by_name(provider_org_name)
        
        if not provider_org:
            print(f"❌ Provider organization '{provider_org_name}' not found")
            return None
        
        org_id = provider_org['orgId']
        
        # Create provider test users
        provider_users = [
            {
                'email': 'provider.test.admin@bhashini.com',
                'password': 'ProviderTestAdmin123!',
                'name': 'Provider Test Admin',
                'role': 'Admin'
            },
            {
                'email': 'provider.test.editor@bhashini.com',
                'password': 'ProviderTestEditor123!',
                'name': 'Provider Test Editor',
                'role': 'Editor'
            },
            {
                'email': 'provider.test.viewer@bhashini.com',
                'password': 'ProviderTestViewer123!',
                'name': 'Provider Test Viewer',
                'role': 'Viewer'
            }
        ]
        
        for user_config in provider_users:
            self.create_test_user(
                user_config['email'],
                user_config['password'],
                user_config['name'],
                org_id,
                user_config['role']
            )
        
        return org_id
    
    def create_customer_test_users(self):
        """Create test users for customer organizations"""
        print("\n👥 Creating Customer Test Users...")
        
        customer_orgs = []
        customer_prefix = os.getenv('GRAFANA_CUSTOMER_ORG_PREFIX', 'Customer')
        
        for i in range(1, 4):  # Create 3 customer orgs
            org_name = f"{customer_prefix}-{i}"
            print(f"\n📋 Creating test users for {org_name}...")
            
            customer_org = self.get_organization_by_name(org_name)
            if customer_org:
                org_id = customer_org['orgId']
                
                # Create customer test users
                customer_users = [
                    {
                        'email': f'customer{i}.test.admin@example.com',
                        'password': f'Customer{i}TestAdmin123!',
                        'name': f'{org_name} Test Admin',
                        'role': 'Admin'
                    },
                    {
                        'email': f'customer{i}.test.editor@example.com',
                        'password': f'Customer{i}TestEditor123!',
                        'name': f'{org_name} Test Editor',
                        'role': 'Editor'
                    },
                    {
                        'email': f'customer{i}.test.viewer@example.com',
                        'password': f'Customer{i}TestViewer123!',
                        'name': f'{org_name} Test Viewer',
                        'role': 'Viewer'
                    }
                ]
                
                for user_config in customer_users:
                    self.create_test_user(
                        user_config['email'],
                        user_config['password'],
                        user_config['name'],
                        org_id,
                        user_config['role']
                    )
                
                customer_orgs.append({
                    'name': org_name,
                    'id': org_id
                })
        
        return customer_orgs
    
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
    
    def generate_api_keys_for_test_users(self):
        """Generate API keys for all test users"""
        print("\n🔑 Generating API Keys for Test Users...")
        
        for user in self.created_users:
            # Generate API key for each user
            key_name = f"test-key-{user['email'].split('@')[0]}"
            self.create_api_key(
                user['email'],
                user['password'],
                key_name,
                user['role']
            )
    
    def generate_test_credentials_report(self):
        """Generate comprehensive test credentials report"""
        print("\n📊 Generating Test Credentials Report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'test_users': self.created_users,
            'api_keys': self.created_api_keys,
            'usage_instructions': {
                'basic_auth': 'Use email/password for basic authentication',
                'api_keys': 'Use API key in Authorization header: Bearer <key>',
                'testing_scenarios': [
                    'Test different user roles (Admin, Editor, Viewer)',
                    'Test organization isolation',
                    'Test data source access permissions',
                    'Test dashboard creation and sharing'
                ]
            }
        }
        
        # Save report to file
        with open('test_users_credentials.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("✅ Test credentials report saved to test_users_credentials.json")
        
        # Print summary
        print("\n🎯 Test Users Created:")
        print("=" * 50)
        print(f"Total Users: {len(self.created_users)}")
        print(f"Total API Keys: {len(self.created_api_keys)}")
        
        print("\n📋 User Credentials:")
        for user in self.created_users:
            print(f"\n  {user['name']} ({user['role']}):")
            print(f"    Email: {user['email']}")
            print(f"    Password: {user['password']}")
            print(f"    Organization ID: {user['org_id']}")
        
        print("\n🔑 API Keys:")
        for key in self.created_api_keys:
            print(f"\n  {key['name']}:")
            print(f"    Key: {key['key']}")
            print(f"    User: {key['user_email']}")
            print(f"    Role: {key['role']}")
            if key['expires']:
                print(f"    Expires: {key['expires']}")
    
    def cleanup_test_users(self):
        """Clean up all created test users (for testing environment reset)"""
        print("\n🧹 Cleaning up test users...")
        
        cleanup_count = 0
        
        for user in self.created_users:
            try:
                response = self.session.delete(
                    f"{self.grafana_url}/api/admin/users/{user['id']}"
                )
                
                if response.status_code == 200:
                    print(f"✅ Deleted test user: {user['email']}")
                    cleanup_count += 1
                else:
                    print(f"⚠️  Failed to delete user {user['email']}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error deleting user {user['email']}: {str(e)}")
        
        print(f"✅ Cleanup completed: {cleanup_count}/{len(self.created_users)} users deleted")
        
        # Reset tracking
        self.created_users = []
        self.created_api_keys = []
    
    def run_user_creation(self):
        """Run the complete test user creation process"""
        print("🚀 Multi-Tenant Test User Creation")
        print("=" * 50)
        
        # Authenticate
        if not self.authenticate():
            print("❌ User creation failed - authentication required")
            return False
        
        # Create provider test users
        provider_org_id = self.create_provider_test_users()
        if not provider_org_id:
            print("❌ Provider test user creation failed")
            return False
        
        # Create customer test users
        customer_orgs = self.create_customer_test_users()
        if not customer_orgs:
            print("❌ Customer test user creation failed")
            return False
        
        # Generate API keys
        self.generate_api_keys_for_test_users()
        
        # Generate credentials report
        self.generate_test_credentials_report()
        
        print("\n🎉 Test user creation completed successfully!")
        return True

def main():
    """Main entry point"""
    manager = TestUserManager()
    
    try:
        success = manager.run_user_creation()
        
        if success:
            print("\n✅ Test users created successfully!")
            print("📚 Next steps:")
            print("  1. Review the test_users_credentials.json file")
            print("  2. Use these credentials for authentication testing")
            print("  3. Run test-authentication.py to verify setup")
            print("  4. Use cleanup_test_users() to reset when needed")
            return 0
        else:
            print("\n❌ Test user creation failed!")
            return 1
            
    except Exception as e:
        print(f"\n❌ User creation failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
