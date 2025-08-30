#!/usr/bin/env python3

import requests
import json
import time
import sys

def create_grafana_admin():
    """Create Grafana admin user programmatically"""
    
    grafana_url = "http://localhost:3010"
    
    # Wait for Grafana to be ready
    print("Waiting for Grafana to be ready...")
    for i in range(30):
        try:
            response = requests.get(f"{grafana_url}/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Grafana is ready")
                break
        except:
            pass
        time.sleep(1)
        print(f"  Waiting... ({i+1}/30)")
    else:
        print("❌ Grafana is not ready after 30 seconds")
        return False
    
    # Try to create admin user using the setup endpoint
    print("Attempting to create admin user...")
    
    # Method 1: Try the setup endpoint (works for first-time setup)
    setup_data = {
        "user": {
            "login": "admin",
            "email": "admin@bhashini.com",
            "password": "admin123"
        },
        "org": {
            "name": "Bhashini"
        }
    }
    
    try:
        response = requests.post(
            f"{grafana_url}/api/admin/users",
            json=setup_data,
            timeout=10
        )
        
        if response.status_code in [200, 201, 409]:  # 409 means user already exists
            print("✅ Admin user created or already exists")
            return True
        else:
            print(f"❌ Failed to create admin user: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
    
    # Method 2: Try to authenticate with the credentials
    print("Testing authentication...")
    try:
        response = requests.get(
            f"{grafana_url}/api/org",
            auth=("admin", "admin123"),
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Authentication successful with admin:admin123")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing authentication: {e}")
    
    return False

if __name__ == "__main__":
    print("🔧 Creating Grafana Admin User")
    print("=" * 40)
    
    success = create_grafana_admin()
    
    if success:
        print("\n✅ Admin user setup completed successfully!")
        print("You can now login with admin:admin123")
    else:
        print("\n❌ Failed to setup admin user")
        print("You may need to manually create the user through the web interface")
        print(f"Web interface: http://localhost:3010")
    
    sys.exit(0 if success else 1)
