#!/usr/bin/env python3
"""
Populate Bhashini QoS Dashboards with Sample Data
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
INFLUXDB_URL = "https://bhashini-qos-dashboards.fly.dev/influxdb"
INFLUXDB_TOKEN = "admin-token-123"
INFLUXDB_ORG = "bhashini"
INFLUXDB_BUCKET = "qos_metrics"

def generate_sample_data():
    """Generate realistic QoS metrics data"""
    
    data_points = []
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    current_time = start_time
    
    print(f"Generating data from {start_time} to {end_time}")
    
    while current_time <= end_time:
        # Use nanoseconds timestamp for InfluxDB
        timestamp = int(current_time.timestamp() * 1_000_000_000)
        hour_factor = current_time.hour
        
        # API Calls - Translation Service
        data_points.append({
            "measurement": "api_calls",
            "tags": {
                "service": "translation",
                "tenant": "healthcare",
                "region": "bom",
                "language": "en-hi"
            },
            "fields": {
                "total_calls": 150 + (hour_factor * 10),
                "successful_calls": 145 + (hour_factor * 9),
                "failed_calls": 5 + hour_factor,
                "response_time_ms": 200 + (hour_factor * 5)
            },
            "time": timestamp
        })
        
        # API Calls - TTS Service
        data_points.append({
            "measurement": "api_calls",
            "tags": {
                "service": "tts",
                "tenant": "healthcare",
                "region": "bom",
                "language": "en-hi"
            },
            "fields": {
                "total_calls": 80 + (hour_factor * 8),
                "successful_calls": 78 + (hour_factor * 7),
                "failed_calls": 2 + hour_factor,
                "response_time_ms": 150 + (hour_factor * 3)
            },
            "time": timestamp
        })
        
        # API Calls - ASR Service
        data_points.append({
            "measurement": "api_calls",
            "tags": {
                "service": "asr",
                "tenant": "healthcare",
                "region": "bom",
                "language": "en-hi"
            },
            "fields": {
                "total_calls": 120 + (hour_factor * 12),
                "successful_calls": 115 + (hour_factor * 11),
                "failed_calls": 5 + hour_factor,
                "response_time_ms": 180 + (hour_factor * 4)
            },
            "time": timestamp
        })
        
        # Response Time Metrics
        data_points.append({
            "measurement": "response_time",
            "tags": {
                "service": "translation",
                "tenant": "healthcare",
                "region": "bom"
            },
            "fields": {
                "avg_response_time_ms": 180 + (hour_factor * 3),
                "p95_response_time_ms": 250 + (hour_factor * 5),
                "p99_response_time_ms": 350 + (hour_factor * 8),
                "min_response_time_ms": 120 + hour_factor,
                "max_response_time_ms": 500 + (hour_factor * 10)
            },
            "time": timestamp
        })
        
        # Error Rate Metrics
        data_points.append({
            "measurement": "error_rate",
            "tags": {
                "service": "translation",
                "tenant": "healthcare",
                "region": "bom"
            },
            "fields": {
                "error_percentage": 2.5 + (hour_factor * 0.1),
                "total_errors": 5 + hour_factor,
                "timeout_errors": 3 + hour_factor,
                "validation_errors": 2 + hour_factor
            },
            "time": timestamp
        })
        
        # SLA Compliance
        data_points.append({
            "measurement": "sla_compliance",
            "tags": {
                "service": "translation",
                "tenant": "healthcare",
                "region": "bom"
            },
            "fields": {
                "compliance_percentage": 97.5 - (hour_factor * 0.1),
                "sla_threshold": 95.0,
                "violations": int(hour_factor * 0.5),
                "uptime_percentage": 99.8 - (hour_factor * 0.01)
            },
            "time": timestamp
        })
        
        # Throughput Metrics
        data_points.append({
            "measurement": "throughput",
            "tags": {
                "service": "translation",
                "tenant": "healthcare",
                "region": "bom"
            },
            "fields": {
                "requests_per_second": 10 + (hour_factor * 2),
                "characters_per_second": 5000 + (hour_factor * 500),
                "peak_throughput": 15 + (hour_factor * 3),
                "average_throughput": 8 + (hour_factor * 1.5)
            },
            "time": timestamp
        })
        
        # Add data for other tenants
        for tenant in ["education", "government"]:
            data_points.append({
                "measurement": "api_calls",
                "tags": {
                    "service": "translation",
                    "tenant": tenant,
                    "region": "bom",
                    "language": "en-hi"
                },
                "fields": {
                    "total_calls": 100 + (hour_factor * 8),
                    "successful_calls": 95 + (hour_factor * 7),
                    "failed_calls": 5 + hour_factor,
                    "response_time_ms": 220 + (hour_factor * 6)
                },
                "time": timestamp
            })
        
        current_time += timedelta(minutes=15)
    
    return data_points

def write_to_influxdb(data_points):
    """Write data points to InfluxDB"""
    
    # Convert to InfluxDB line protocol format
    lines = []
    for point in data_points:
        tags = ",".join([f"{k}={v}" for k, v in point["tags"].items()])
        fields = ",".join([f"{k}={v}" for k, v in point["fields"].items()])
        line = f"{point['measurement']},{tags} {fields} {point['time']}"
        lines.append(line)
    
    data = "\n".join(lines)
    
    url = f"{INFLUXDB_URL}/api/v2/write?org={INFLUXDB_ORG}&bucket={INFLUXDB_BUCKET}"
    headers = {
        "Authorization": f"Token {INFLUXDB_TOKEN}",
        "Content-Type": "application/octet-stream"
    }
    
    print(f"Writing {len(data_points)} data points to InfluxDB...")
    print(f"URL: {url}")
    
    try:
        response = requests.post(url, headers=headers, data=data)
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 204:
            print("✅ Successfully wrote data to InfluxDB!")
            return True
        else:
            print(f"❌ Failed to write data: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Populating Bhashini QoS Dashboards with Sample Data...")
    
    # Generate sample data
    data_points = generate_sample_data()
    print(f"📊 Generated {len(data_points)} data points")
    
    # Write to InfluxDB
    if write_to_influxdb(data_points):
        print("✅ Data population complete!")
        print("🌐 You can now view the data in your Grafana dashboards at:")
        print("   https://bhashini-qos-dashboards.fly.dev/")
        print("🔐 Login with: admin / admin123")
    else:
        print("❌ Failed to populate data")
