#!/usr/bin/env python3
"""
Populate data for existing Bhashini QoS dashboards only
- Ultimate Overview Dashboard (8 panels)
- Customer Overview Dashboard
"""

import requests
import random
from datetime import datetime, timedelta

# Configuration
INFLUXDB_URL = "https://bhashini-qos-dashboards.fly.dev/influxdb/api/v2/write?org=bhashini&bucket=qos_metrics"
TOKEN = "admin-token-123"

def generate_ultimate_dashboard_data():
    """Generate data for the Ultimate Overview Dashboard (8 panels)"""
    
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    data_points = []
    current = start_time
    
    while current <= end_time:
        timestamp = int(current.timestamp() * 1_000_000_000)  # nanoseconds
        
        # 1. System Status (availability)
        availability = 95 + random.uniform(0, 4)
        data_points.append(f'qos_metrics,metric_type=availability value={availability} {timestamp}')
        
        # 2. Total API Calls
        api_calls = random.randint(5000, 20000)
        data_points.append(f'qos_metrics,metric_type=api_calls value={api_calls} {timestamp}')
        
        # 3. Active Tenants
        active_tenants = random.randint(3, 8)
        data_points.append(f'qos_metrics,metric_type=active_tenants value={active_tenants} {timestamp}')
        
        # 4. Average Response Time
        response_time = random.randint(80, 400)
        data_points.append(f'qos_metrics,metric_type=latency value={response_time} {timestamp}')
        
        # 5. Overall Error Rate
        error_rate = random.uniform(0.5, 3.0)
        data_points.append(f'qos_metrics,metric_type=error_rate value={error_rate} {timestamp}')
        
        # 6. SLA Compliance
        sla_compliance = 94 + random.uniform(0, 5)
        data_points.append(f'qos_metrics,metric_type=sla_compliance value={sla_compliance} {timestamp}')
        
        # 7. Peak Throughput
        throughput = random.randint(15, 60)
        data_points.append(f'qos_metrics,metric_type=throughput value={throughput} {timestamp}')
        
        # 8. Service Count
        service_count = random.randint(3, 8)
        data_points.append(f'qos_metrics,metric_type=active_services value={service_count} {timestamp}')
        
        current += timedelta(minutes=5)
    
    return data_points

def generate_customer_dashboard_data():
    """Generate data for customer dashboards"""
    
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    data_points = []
    customers = ["enterprise_1", "freemium_1", "startup_2"]
    
    current = start_time
    while current <= end_time:
        timestamp = int(current.timestamp() * 1_000_000_000)  # nanoseconds
        
        for customer_id in customers:
            # Availability (95-99%)
            availability = 95 + random.uniform(0, 4)
            data_points.append(f'qos_metrics,customer_id={customer_id},metric_type=availability value={availability} {timestamp}')
            
            # Active services count
            active_services = random.randint(3, 8)
            data_points.append(f'qos_metrics,customer_id={customer_id},metric_type=active_services value={active_services} {timestamp}')
            
            # API calls
            api_calls = random.randint(5000, 20000)
            data_points.append(f'qos_metrics,customer_id={customer_id},metric_type=api_calls value={api_calls} {timestamp}')
            
            # Error rate
            error_rate = random.uniform(0.5, 3.0)
            data_points.append(f'qos_metrics,customer_id={customer_id},metric_type=error_rate value={error_rate} {timestamp}')
            
            # Latency
            latency = random.randint(80, 400)
            data_points.append(f'qos_metrics,customer_id={customer_id},metric_type=latency value={latency} {timestamp}')
            
            # Throughput
            throughput = random.randint(15, 60)
            data_points.append(f'qos_metrics,customer_id={customer_id},metric_type=throughput value={throughput} {timestamp}')
            
            # SLA compliance
            sla_compliance = 94 + random.uniform(0, 5)
            data_points.append(f'qos_metrics,customer_id={customer_id},metric_type=sla_compliance value={sla_compliance} {timestamp}')
        
        current += timedelta(minutes=5)
    
    return data_points

def write_to_influxdb(data_points):
    """Write data points to InfluxDB"""
    
    print(f"📊 Writing {len(data_points)} data points to InfluxDB...")
    print(f"URL: {INFLUXDB_URL}")
    
    headers = {
        'Authorization': f'Token {TOKEN}',
        'Content-Type': 'text/plain; charset=utf-8'
    }
    
    # Convert to line protocol format
    data = '\n'.join(data_points)
    
    response = requests.post(INFLUXDB_URL, headers=headers, data=data)
    
    if response.status_code == 204:
        print("✅ Successfully wrote data to InfluxDB!")
        return True
    else:
        print(f"❌ Failed to write data. Status: {response.status_code}, Response: {response.text}")
        return False

def main():
    """Main function to populate all existing dashboards"""
    
    print("🚀 Populating existing Bhashini QoS dashboards with data...")
    
    # Generate data for Ultimate Dashboard (8 panels)
    print("📊 Generating Ultimate Dashboard data...")
    ultimate_data = generate_ultimate_dashboard_data()
    print(f"   ✅ Generated {len(ultimate_data)} data points")
    
    # Generate data for Customer Dashboards
    print("📊 Generating Customer Dashboard data...")
    customer_data = generate_customer_dashboard_data()
    print(f"   ✅ Generated {len(customer_data)} data points")
    
    # Combine all data
    all_data = ultimate_data + customer_data
    print(f"\n📈 Total data points to write: {len(all_data)}")
    
    # Write to InfluxDB
    if write_to_influxdb(all_data):
        print("\n🎉 Successfully populated existing dashboards!")
        print("\n📊 Dashboards now have data:")
        print("   ✅ Ultimate Overview Dashboard (8 panels)")
        print("   ✅ Customer Overview Dashboard")
        print("\n🌐 Access your dashboards at:")
        print("   https://bhashini-qos-dashboards.fly.dev/")
        print("🔐 Login with: admin / admin123")
    else:
        print("\n❌ Failed to populate dashboards")

if __name__ == "__main__":
    main()
