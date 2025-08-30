#!/usr/bin/env python3
"""
Populate data for all Bhashini QoS dashboards
- Ultimate Overview Dashboard
- Customer Dashboards (Enterprise, Freemium, Startup)
- Provider Overview Dashboard
- Sector-specific Dashboards (Healthcare, Education, Government)
"""

import requests
import random
from datetime import datetime, timedelta

# Configuration
INFLUXDB_URL = "https://bhashini-qos-dashboards.fly.dev/influxdb/api/v2/write?org=bhashini&bucket=qos_metrics"
TOKEN = "admin-token-123"

def generate_customer_data():
    """Generate data for customer dashboards with customer_id tags"""
    
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

def generate_sector_data():
    """Generate data for sector-specific dashboards"""
    
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    data_points = []
    sectors = ["healthcare", "education", "government"]
    
    current = start_time
    while current <= end_time:
        timestamp = int(current.timestamp() * 1_000_000_000)  # nanoseconds
        
        for sector in sectors:
            # Medical translation accuracy (for healthcare)
            if sector == "healthcare":
                accuracy = 96 + random.uniform(0, 3)
                data_points.append(f'medical_translation_accuracy,sector={sector} value={accuracy} {timestamp}')
                
                # Critical communication response time
                response_time = random.uniform(5, 25)
                data_points.append(f'critical_communication_response_time,sector={sector} value={response_time} {timestamp}')
            
            # Educational content quality (for education)
            if sector == "education":
                quality_score = 92 + random.uniform(0, 7)
                data_points.append(f'educational_content_quality,sector={sector} value={quality_score} {timestamp}')
                
                # Student engagement metrics
                engagement = 85 + random.uniform(0, 14)
                data_points.append(f'student_engagement,sector={sector} value={engagement} {timestamp}')
            
            # Government compliance (for government)
            if sector == "government":
                compliance = 98 + random.uniform(0, 2)
                data_points.append(f'government_compliance,sector={sector} value={compliance} {timestamp}')
                
                # Security audit score
                security_score = 95 + random.uniform(0, 5)
                data_points.append(f'security_audit_score,sector={sector} value={security_score} {timestamp}')
            
            # Common sector metrics
            data_points.append(f'sector_performance,sector={sector} value={random.uniform(85, 98)} {timestamp}')
            data_points.append(f'user_satisfaction,sector={sector} value={random.uniform(80, 95)} {timestamp}')
        
        current += timedelta(minutes=5)
    
    return data_points

def generate_tenant_data():
    """Generate data for tenant-specific metrics"""
    
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    data_points = []
    tenants = ["healthcare", "education", "government"]
    services = ["asr", "translation", "tts"]
    regions = ["bom", "del", "blr", "hyd"]
    languages = ["en-hi", "hi-en", "en-ta", "ta-en"]
    
    current = start_time
    while current <= end_time:
        timestamp = int(current.timestamp() * 1_000_000_000)  # nanoseconds
        
        for tenant in tenants:
            for service in services:
                for region in regions:
                    for language in languages:
                        # API calls with tenant context
                        total_calls = random.randint(100, 500)
                        successful_calls = int(total_calls * (0.95 + random.uniform(0, 0.04)))
                        failed_calls = total_calls - successful_calls
                        
                        data_points.append(f'api_calls,tenant={tenant},service={service},region={region},language={language},field=total_calls value={total_calls} {timestamp}')
                        data_points.append(f'api_calls,tenant={tenant},service={service},region={region},language={language},field=successful_calls value={successful_calls} {timestamp}')
                        data_points.append(f'api_calls,tenant={tenant},service={service},region={region},language={language},field=failed_calls value={failed_calls} {timestamp}')
                        
                        # Response time
                        response_time = random.randint(100, 300)
                        data_points.append(f'response_time,tenant={tenant},service={service},region={region},language={language} value={response_time} {timestamp}')
                        
                        # Error rate
                        error_rate = (failed_calls / total_calls) * 100
                        data_points.append(f'error_rate,tenant={tenant},service={service},region={region},language={language} value={error_rate} {timestamp}')
        
        current += timedelta(minutes=10)  # Less frequent for tenant data
    
    return data_points

def write_to_influxdb(data_points):
    """Write data points to InfluxDB in batches"""
    
    batch_size = 1000  # Write 1000 data points at a time
    total_batches = (len(data_points) + batch_size - 1) // batch_size
    
    print(f"📦 Writing data in {total_batches} batches of {batch_size} points each...")
    
    headers = {
        'Authorization': f'Token {TOKEN}',
        'Content-Type': 'text/plain; charset=utf-8'
    }
    
    successful_writes = 0
    
    for i in range(0, len(data_points), batch_size):
        batch = data_points[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        print(f"   📤 Writing batch {batch_num}/{total_batches} ({len(batch)} points)...")
        
        # Join batch data points
        data = '\n'.join(batch)
        
        response = requests.post(INFLUXDB_URL, headers=headers, data=data)
        
        if response.status_code == 204:
            successful_writes += 1
            print(f"   ✅ Batch {batch_num} successful")
        else:
            print(f"   ❌ Batch {batch_num} failed: {response.status_code}")
            if response.status_code != 204:
                print(f"      Response: {response.text}")
    
    print(f"\n📊 Successfully wrote {successful_writes}/{total_batches} batches")
    return successful_writes == total_batches

def main():
    print("🚀 Populating all Bhashini QoS dashboards with comprehensive data...")
    
    all_data_points = []
    
    # 1. Customer dashboard data
    print("📊 Generating customer dashboard data...")
    customer_data = generate_customer_data()
    all_data_points.extend(customer_data)
    print(f"   ✅ Generated {len(customer_data)} customer data points")
    
    # 2. Sector-specific data
    print("🏥 Generating sector-specific dashboard data...")
    sector_data = generate_sector_data()
    all_data_points.extend(sector_data)
    print(f"   ✅ Generated {len(sector_data)} sector data points")
    
    # 3. Tenant-specific data
    print("🏢 Generating tenant-specific data...")
    tenant_data = generate_tenant_data()
    all_data_points.extend(tenant_data)
    print(f"   ✅ Generated {len(tenant_data)} tenant data points")
    
    print(f"\n📈 Total data points to write: {len(all_data_points)}")
    
    # Write to InfluxDB
    print("\n💾 Writing data to InfluxDB...")
    print(f"URL: {INFLUXDB_URL}")
    
    success = write_to_influxdb(all_data_points)
    
    if success:
        print("\n🎉 Successfully populated all dashboards!")
        print("\n📊 Dashboards now have data:")
        print("   ✅ Ultimate Overview Dashboard")
        print("   ✅ Customer Dashboards (Enterprise, Freemium, Startup)")
        print("   ✅ Provider Overview Dashboard")
        print("   ✅ Sector Dashboards (Healthcare, Education, Government)")
        print("   ✅ Tenant-specific Metrics")
        
        print("\n🌐 Access your dashboards at:")
        print("   https://bhashini-qos-dashboards.fly.dev/")
        print("🔐 Login with: admin / admin123")
        
        print("\n📋 Dashboard locations:")
        print("   • Ultimate Overview: Ultimate Overview folder")
        print("   • Customer Dashboards: Customer Overview folder")
        print("   • Provider Dashboard: Bhashini Provider folder")
        print("   • Sector Dashboards: Working Dashboards folder")
    else:
        print("❌ Failed to write data")

if __name__ == "__main__":
    main()
