#!/usr/bin/env python3
"""
Generate test data for Bhashini QoS monitoring dashboards
"""

import requests
import json
import time
from datetime import datetime, timedelta

def generate_test_data():
    """Generate test QoS metrics data"""
    
    # InfluxDB connection details
    influxdb_url = "http://localhost:8086"
    token = "admin-token-123"
    org = "bhashini"
    bucket = "qos_metrics"
    
    # Generate data for the last hour
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    
    # Services to generate data for
    services = ["translation", "tts", "asr", "mt"]
    tenants = ["enterprise_1", "startup_2", "freemium_1"]
    metric_types = ["availability", "latency", "error_rate", "throughput"]
    
    print("Generating test data for Bhashini QoS monitoring...")
    
    # Generate data points every 5 minutes for the last hour
    current_time = start_time
    data_points = []
    
    while current_time <= end_time:
        for tenant in tenants:
            for service in services:
                for metric_type in metric_types:
                    # Generate realistic values
                    if metric_type == "availability":
                        value = 0.95 + (0.05 * (hash(f"{tenant}{service}{current_time}") % 100) / 100)
                    elif metric_type == "latency":
                        value = 100 + (hash(f"{tenant}{service}{current_time}") % 400)
                    elif metric_type == "error_rate":
                        value = 0.01 + (0.04 * (hash(f"{tenant}{service}{current_time}") % 100) / 100)
                    else:  # throughput
                        value = 50 + (hash(f"{tenant}{service}{current_time}") % 150)
                    
                    # Create data point
                    data_point = {
                        "measurement": "qos_metrics",
                        "tags": {
                            "tenant_id": tenant,
                            "service_name": service,
                            "metric_type": metric_type,
                            "sla_tier": "premium" if tenant == "enterprise_1" else "standard" if tenant == "startup_2" else "basic"
                        },
                        "fields": {
                            "value": value
                        },
                        "time": current_time.isoformat()
                    }
                    data_points.append(data_point)
        
        current_time += timedelta(minutes=5)
    
    print(f"Generated {len(data_points)} data points")
    
    # Write data to InfluxDB using the HTTP API
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/lineprotocol"
    }
    
    # Convert to line protocol format
    line_protocol = []
    for point in data_points:
        tags = ",".join([f"{k}={v}" for k, v in point["tags"].items()])
        fields = f"value={point['fields']['value']}"
        timestamp = int(datetime.fromisoformat(point["time"]).timestamp() * 1e9)
        
        line = f"{point['measurement']},{tags} {fields} {timestamp}"
        line_protocol.append(line)
    
    # Write data in batches
    batch_size = 100
    for i in range(0, len(line_protocol), batch_size):
        batch = line_protocol[i:i + batch_size]
        batch_text = "\n".join(batch)
        
        url = f"{influxdb_url}/api/v2/write?org={org}&bucket={bucket}"
        response = requests.post(url, headers=headers, data=batch_text)
        
        if response.status_code == 204:
            print(f"Wrote batch {i//batch_size + 1}/{(len(line_protocol) + batch_size - 1)//batch_size}")
        else:
            print(f"Error writing batch: {response.status_code} - {response.text}")
    
    print("Test data generation complete!")
    print(f"Data written to bucket: {bucket}")
    print(f"Time range: {start_time} to {end_time}")
    print(f"Tenants: {', '.join(tenants)}")
    print(f"Services: {', '.join(services)}")
    print(f"Metrics: {', '.join(metric_types)}")

if __name__ == "__main__":
    generate_test_data()
