#!/usr/bin/env python3
"""
Simple QoS data generator for Bhashini Dashboards
"""

import os
import time
import random
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuration
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'admin-token-123')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'bhashini')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'qos_metrics')

def generate_qos_data():
    """Generate realistic QoS metrics data"""
    
    # Initialize InfluxDB client
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    # Service configurations
    services = ['asr', 'translation', 'tts']
    tenants = ['enterprise_1', 'startup_1', 'freemium_1']
    sla_tiers = ['premium', 'standard', 'basic']
    
    try:
        while True:
            timestamp = datetime.utcnow()
            points = []
            
            for service in services:
                for tenant in tenants:
                    # Determine SLA tier based on tenant
                    sla_tier = 'premium' if tenant == 'enterprise_1' else 'standard' if tenant == 'startup_1' else 'basic'
                    
                    # Generate availability (higher for premium tiers)
                    base_availability = 99.5 if sla_tier == 'premium' else 97.0 if sla_tier == 'standard' else 94.0
                    availability = max(85.0, min(100.0, base_availability + random.uniform(-2.0, 2.0)))
                    
                    # Generate latency (lower for premium tiers)
                    base_latency = 50 if sla_tier == 'premium' else 150 if sla_tier == 'standard' else 300
                    latency = max(10, min(1000, base_latency + random.uniform(-20, 50)))
                    
                    # Generate error rate (lower for premium tiers)
                    base_error_rate = 0.1 if sla_tier == 'premium' else 0.5 if sla_tier == 'standard' else 1.0
                    error_rate = max(0.0, min(5.0, base_error_rate + random.uniform(-0.1, 0.3)))
                    
                    # Generate throughput
                    throughput = random.uniform(100, 2000)
                    
                    # Create data points
                    points.extend([
                        Point("qos_metrics")
                            .tag("service_name", service)
                            .tag("tenant_id", tenant)
                            .tag("sla_tier", sla_tier)
                            .field("metric_type", "availability")
                            .field("value", availability)
                            .time(timestamp),
                        
                        Point("qos_metrics")
                            .tag("service_name", service)
                            .tag("tenant_id", tenant)
                            .tag("sla_tier", sla_tier)
                            .field("metric_type", "latency")
                            .field("value", latency)
                            .time(timestamp),
                        
                        Point("qos_metrics")
                            .tag("service_name", service)
                            .tag("tenant_id", tenant)
                            .tag("sla_tier", sla_tier)
                            .field("metric_type", "error_rate")
                            .field("value", error_rate)
                            .time(timestamp),
                        
                        Point("qos_metrics")
                            .tag("service_name", service)
                            .tag("tenant_id", tenant)
                            .tag("sla_tier", sla_tier)
                            .field("metric_type", "throughput")
                            .field("value", throughput)
                            .time(timestamp)
                    ])
            
            # Write data to InfluxDB
            if points:
                write_api.write(bucket=INFLUXDB_BUCKET, record=points)
                print(f"✅ Generated {len(points)} data points at {timestamp}")
            
            # Wait before next generation
            time.sleep(30)  # Generate data every 30 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Data generation stopped by user")
    except Exception as e:
        print(f"❌ Error generating data: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    print("🚀 Starting QoS data generation...")
    generate_qos_data()
