#!/usr/bin/env python3
"""
Generate test data for Bhashini Ultimate Overview Dashboard
"""

import requests
import random
from datetime import datetime, timedelta
import time

# Configuration
INFLUXDB_URL = "https://bhashini-qos-dashboards.fly.dev/influxdb/api/v2/write?org=bhashini&bucket=qos_metrics"
TOKEN = "admin-token-123"

def generate_qos_metrics():
    """Generate QoS metrics matching the dashboard queries"""
    
    # Time range: last 24 hours
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    
    data_points = []
    
    # Generate data every 5 minutes
    current = start_time
    while current <= end_time:
        timestamp = int(current.timestamp() * 1_000_000_000)  # nanoseconds
        
        # System availability (0-100%)
        availability = 95 + random.uniform(0, 4)
        data_points.append(f'qos_metrics,metric_type=availability value={availability} {timestamp}')
        
        # Active services count
        active_services = random.randint(4, 6)
        data_points.append(f'qos_metrics,metric_type=active_services value={active_services} {timestamp}')
        
        # API calls
        api_calls = random.randint(10000, 15000)
        data_points.append(f'qos_metrics,metric_type=api_calls value={api_calls} {timestamp}')
        
        # Error rate
        error_rate = random.uniform(0.5, 2.5)
        data_points.append(f'qos_metrics,metric_type=error_rate value={error_rate} {timestamp}')
        
        # Service-specific metrics
        services = ['translation', 'asr', 'tts', 'ocr']
        for service in services:
            # Calls
            calls = random.randint(2000, 4000)
            data_points.append(f'service_metrics,service={service},metric_type=calls value={calls} {timestamp}')
            
            # Response time
            response_time = random.randint(100, 300)
            data_points.append(f'service_metrics,service={service},metric_type=response_time value={response_time} {timestamp}')
            
            # Success rate
            success_rate = 95 + random.uniform(0, 4)
            data_points.append(f'service_metrics,service={service},metric_type=success_rate value={success_rate} {timestamp}')
        
        # Regional distribution
        regions = ['north', 'south', 'east', 'west', 'central']
        for region in regions:
            traffic = random.randint(1000, 3000)
            data_points.append(f'regional_metrics,region={region} traffic={traffic} {timestamp}')
        
        # Language pairs
        language_pairs = ['en-hi', 'hi-en', 'en-ta', 'ta-en', 'en-bn', 'bn-en']
        for pair in language_pairs:
            usage = random.randint(500, 2000)
            data_points.append(f'language_metrics,language_pair={pair} usage={usage} {timestamp}')
        
        current += timedelta(minutes=5)
    
    return data_points

def write_to_influxdb(data_points):
    """Write data points to InfluxDB"""
    
    # Join all data points
    data = '\n'.join(data_points)
    
    headers = {
        'Authorization': f'Token {TOKEN}',
        'Content-Type': 'text/plain; charset=utf-8'
    }
    
    response = requests.post(INFLUXDB_URL, headers=headers, data=data)
    
    print(f"Response Status: {response.status_code}")
    if response.status_code != 204:
        print(f"Response: {response.text}")
    
    return response.status_code == 204

def main():
    print("🚀 Populating Bhashini Ultimate Dashboard with Sample Data...")
    
    # Generate data
    data_points = generate_qos_metrics()
    print(f"📊 Generated {len(data_points)} data points")
    
    # Write to InfluxDB
    print("Writing data to InfluxDB...")
    print(f"URL: {INFLUXDB_URL}")
    
    success = write_to_influxdb(data_points)
    
    if success:
        print("✅ Successfully wrote data to InfluxDB!")
        print("✅ Data population complete!")
        print("🌐 You can now view the data in your Ultimate Overview dashboard at:")
        print("   https://bhashini-qos-dashboards.fly.dev/")
        print("🔐 Login with: admin / admin123")
    else:
        print("❌ Failed to write data")

if __name__ == "__main__":
    main()
