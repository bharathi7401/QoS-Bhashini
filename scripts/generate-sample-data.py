#!/usr/bin/env python3
"""
Generate sample QoS data for Bhashini dashboards
"""

import requests
import json
import time
from datetime import datetime, timedelta

# InfluxDB configuration
INFLUXDB_URL = "http://127.0.0.1:8086"
INFLUXDB_TOKEN = "admin-token-123"
INFLUXDB_ORG = "bhashini"
INFLUXDB_BUCKET = "qos_metrics"

def generate_sample_data():
    """Generate sample QoS metrics data"""
    
    # Sample data points
    data_points = []
    
    # Generate data for the last 24 hours
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    current_time = start_time
    while current_time <= end_time:
        timestamp = current_time.isoformat() + "Z"
        
        # API Calls metric
        data_points.append({
            "measurement": "api_calls",
            "tags": {
                "service": "translation",
                "tenant": "healthcare",
                "region": "bom"
            },
            "fields": {
                "total_calls": 150 + int(current_time.hour * 10),
                "successful_calls": 145 + int(current_time.hour * 9),
                "failed_calls": 5 + int(current_time.hour * 1),
                "response_time_ms": 200 + int(current_time.hour * 5)
            },
            "time": timestamp
        })
        
        # Response Time metric
        data_points.append({
            "measurement": "response_time",
            "tags": {
                "service": "translation",
                "tenant": "healthcare",
                "region": "bom"
            },
            "fields": {
                "avg_response_time_ms": 180 + int(current_time.hour * 3),
                "p95_response_time_ms": 250 + int(current_time.hour * 5),
                "p99_response_time_ms": 350 + int(current_time.hour * 8)
            },
            "time": timestamp
        })
        
        # Error Rate metric
        data_points.append({
            "measurement": "error_rate",
            "tags": {
                "service": "translation",
                "tenant": "healthcare",
                "region": "bom"
            },
            "fields": {
                "error_percentage": 2.5 + (current_time.hour * 0.1),
                "total_errors": 5 + int(current_time.hour * 1),
                "error_type": "timeout"
            },
            "time": timestamp
        })
        
        # SLA Compliance metric
        data_points.append({
            "measurement": "sla_compliance",
            "tags": {
                "service": "translation",
                "tenant": "healthcare",
                "region": "bom"
            },
            "fields": {
                "compliance_percentage": 97.5 - (current_time.hour * 0.1),
                "sla_threshold": 95.0,
                "violations": int(current_time.hour * 0.5)
            },
            "time": timestamp
        })
        
        current_time += timedelta(minutes=15)
    
    return data_points

def write_to_influxdb(data_points):
    """Write data points to InfluxDB using the HTTP API"""
    
    headers = {
        "Authorization": f"Token {INFLUXDB_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Convert to InfluxDB line protocol format
    lines = []
    for point in data_points:
        tags = ",".join([f"{k}={v}" for k, v in point["tags"].items()])
        fields = ",".join([f"{k}={v}" for k, v in point["fields"].items()])
        line = f"{point['measurement']},{tags} {fields} {point['time']}"
        lines.append(line)
    
    data = "\n".join(lines)
    
    url = f"{INFLUXDB_URL}/api/v2/write?org={INFLUXDB_ORG}&bucket={INFLUXDB_BUCKET}"
    
    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 204:
            print(f"✅ Successfully wrote {len(data_points)} data points to InfluxDB")
            return True
        else:
            print(f"❌ Failed to write data: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error writing to InfluxDB: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Generating sample QoS data for Bhashini dashboards...")
    
    # Generate sample data
    data_points = generate_sample_data()
    print(f"📊 Generated {len(data_points)} data points")
    
    # Write to InfluxDB
    if write_to_influxdb(data_points):
        print("✅ Sample data generation complete!")
        print("🌐 You can now view the data in your Grafana dashboards at:")
        print("   https://bhashini-qos-dashboards.fly.dev/")
    else:
        print("❌ Failed to generate sample data")
