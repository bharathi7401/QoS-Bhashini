#!/usr/bin/env python3
"""
Test Alerting Setup
Verifies that the alerting system is properly configured and working
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_grafana_connection():
    """Test connection to Grafana"""
    grafana_url = os.getenv('GRAFANA_URL', 'http://localhost:3000')
    admin_user = os.getenv('GRAFANA_ADMIN_USER', 'admin')
    admin_password = os.getenv('GRAFANA_ADMIN_PASSWORD', 'admin123')
    
    try:
        # Test basic connectivity
        response = requests.get(f"{grafana_url}/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Grafana is running and accessible")
        else:
            print(f"❌ Grafana health check failed: {response.status_code}")
            return False
        
        # Test authentication
        auth_response = requests.post(
            f"{grafana_url}/api/login",
            json={"user": admin_user, "password": admin_password},
            timeout=10
        )
        
        if auth_response.status_code == 200:
            print("✅ Grafana authentication successful")
            return True
        else:
            print(f"❌ Grafana authentication failed: {auth_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Grafana connection error: {e}")
        return False

def test_alerting_configuration():
    """Test alerting configuration"""
    grafana_url = os.getenv('GRAFANA_URL', 'http://localhost:3000')
    admin_user = os.getenv('GRAFANA_ADMIN_USER', 'admin')
    admin_password = os.getenv('GRAFANA_ADMIN_PASSWORD', 'admin123')
    
    try:
        # Login to get session
        session = requests.Session()
        login_response = session.post(
            f"{grafana_url}/api/login",
            json={"user": admin_user, "password": admin_password},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print("❌ Cannot test alerting without authentication")
            return False
        
        # Test unified alerting status
        alerting_response = session.get(
            f"{grafana_url}/api/v1/provisioning/contact-points",
            timeout=10
        )
        
        if alerting_response.status_code == 200:
            print("✅ Unified alerting is enabled and accessible")
            contact_points = alerting_response.json()
            print(f"   Found {len(contact_points)} contact points")
        else:
            print(f"❌ Unified alerting test failed: {alerting_response.status_code}")
            return False
        
        # Test alert rules
        rules_response = session.get(
            f"{grafana_url}/api/ruler/grafana/api/v1/rules",
            timeout=10
        )
        
        if rules_response.status_code == 200:
            print("✅ Alert rules API is accessible")
            rules = rules_response.json()
            print(f"   Found {len(rules)} rule groups")
        else:
            print(f"❌ Alert rules API test failed: {rules_response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Alerting configuration test error: {e}")
        return False

def test_environment_variables():
    """Test required environment variables"""
    required_vars = [
        'SMTP_HOST',
        'SMTP_PORT', 
        'SMTP_USER',
        'SMTP_PASSWORD',
        'SLACK_WEBHOOK_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def test_provisioning_files():
    """Test that alerting provisioning files exist"""
    required_files = [
        'grafana/provisioning/alerting/contact-points.yml',
        'grafana/provisioning/alerting/notification-policies.yml',
        'grafana/provisioning/alerting/alert-rules.yml',
        'grafana/provisioning/alerting/mute-timings.yml'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required provisioning files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required provisioning files exist")
        return True

def main():
    """Main test function"""
    print("🧪 Testing Bhashini Alerting Setup")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Grafana Connection", test_grafana_connection),
        ("Alerting Configuration", test_alerting_configuration),
        ("Provisioning Files", test_provisioning_files)
    ]
    
    results = {}
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            result = test_func()
            results[test_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            results[test_name] = False
            all_passed = False
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    if all_passed:
        print("\n🎉 All tests passed! Alerting system is properly configured.")
        return 0
    else:
        print("\n💥 Some tests failed. Please check the configuration.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
