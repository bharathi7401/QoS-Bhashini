#!/usr/bin/env python3
"""
Simple test data generator for Bhashini QoS Dashboard
This script will populate InfluxDB with sample data so the dashboard shows something
"""

import requests
import json
import time
from datetime import datetime, timedelta
import random

# InfluxDB configuration
INFLUXDB_URL = "https://bhashini-qos-dashboards.fly.dev/influxdb"
ORG = "bhashini"
BUCKET = "qos_metrics"
TOKEN = "admin-token-123"

def generate_test_data():
    """Generate realistic test data for the dashboard"""
    
    # Base data points
    services = ["translation", "tts", "asr"]
    tenants = ["enterprise_1", "enterprise_2", "startup_1", "startup_2", "freemium_1"]
    metric_types = ["availability", "latency", "error_rate", "throughput"]
    
    # Generate data for the last 2 hours
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=2)
    
    data_points = []
    current_time = start_time
    
    while current_time <= end_time:
        for service in services:
            for tenant in tenants:
                for metric_type in metric_types:
                    # Generate realistic values based on metric type
                    if metric_type == "availability":
                        # Availability: 95-99.9%
                        value = random.uniform(95.0, 99.9)
                    elif metric_type == "latency":
                        # Latency: 80-500ms
                        value = random.uniform(80, 500)
                    elif metric_type == "error_rate":
                        # Error rate: 0.1-5%
                        value = random.uniform(0.1, 5.0)
                    elif metric_type == "throughput":
                        # Throughput: 50-200 requests/min
                        value = random.uniform(50, 200)
                    
                    # Add some variation based on tenant tier
                    if "enterprise" in tenant:
                        value *= 0.8  # 20% better for enterprise
                    elif "freemium" in tenant:
                        value *= 1.3  # 30% worse for freemium
                    
                    # Create data point
                    data_point = {
                        "measurement": "qos_metrics",
                        "tags": {
                            "service_name": service,
                            "tenant_id": tenant,
                            "metric_type": metric_type,
                            "sla_tier": "premium" if "enterprise" in tenant else "standard" if "startup" in tenant else "basic"
                        },
                        "fields": {
                            "value": round(value, 2)
                        },
                        "time": current_time.isoformat() + "Z"
                    }
                    
                    data_points.append(data_point)
        
        # Move to next time interval (every 5 minutes)
        current_time += timedelta(minutes=5)
    
    return data_points

def write_to_influxdb(data_points):
    """Write data points to InfluxDB using the HTTP API"""
    
    # Convert to InfluxDB line protocol format
    lines = []
    for point in data_points:
        tags = ",".join([f"{k}={v}" for k, v in point["tags"].items()])
        fields = ",".join([f"{k}={v}" for k, v in point["fields"].items()])
        timestamp = int(datetime.fromisoformat(point["time"].replace("Z", "")).timestamp() * 1000000000)  # nanoseconds
        
        line = f"{point['measurement']},{tags} {fields} {timestamp}"
        lines.append(line)
    
    # Write data in batches
    batch_size = 100
    for i in range(0, len(lines), batch_size):
        batch = lines[i:i + batch_size]
        batch_text = "\n".join(batch)
        
        # Write to InfluxDB
        url = f"{INFLUXDB_URL}/api/v2/write"
        headers = {
            "Authorization": f"Token {TOKEN}",
            "Content-Type": "text/plain; charset=utf-8"
        }
        params = {
            "org": ORG,
            "bucket": BUCKET,
            "precision": "ns"
        }
        
        try:
            response = requests.post(url, headers=headers, params=params, data=batch_text)
            if response.status_code == 204:
                print(f"✅ Wrote batch {i//batch_size + 1} ({len(batch)} points)")
            else:
                print(f"❌ Failed to write batch {i//batch_size + 1}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error writing batch {i//batch_size + 1}: {e}")
        
        # Small delay between batches
        time.sleep(0.1)

def main():
    """Main function"""
    print("🚀 Starting Bhashini QoS Test Data Generation...")
    
    # Generate test data
    print("📊 Generating test data...")
    data_points = generate_test_data()
    print(f"✅ Generated {len(data_points)} data points")
    
    # Write to InfluxDB
    print("💾 Writing data to InfluxDB...")
    write_to_influxdb(data_points)
    
    print("🎉 Test data generation complete!")
    print(f"📈 Dashboard should now show data for the last 2 hours")
    print(f"🔗 Check your dashboard at: https://bhashini-qos-dashboards.fly.dev/grafana/")

if __name__ == "__main__":
    main()
