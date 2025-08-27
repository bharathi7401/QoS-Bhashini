#!/usr/bin/env python3
"""Debug script to test InfluxDB connection"""

import os
from influxdb_client import InfluxDBClient

# Print environment variables
print("Environment variables:")
print(f"INFLUXDB_URL: {os.getenv('INFLUXDB_URL')}")
print(f"INFLUXDB_TOKEN: {os.getenv('INFLUXDB_TOKEN')}")
print(f"INFLUXDB_ORG: {os.getenv('INFLUXDB_ORG')}")
print(f"INFLUXDB_BUCKET: {os.getenv('INFLUXDB_BUCKET')}")

# Test connection
print("\nTesting connection...")
try:
    client = InfluxDBClient(
        url=os.getenv('INFLUXDB_URL', 'http://localhost:8086'),
        token=os.getenv('INFLUXDB_TOKEN'),
        org=os.getenv('INFLUXDB_ORG', 'bhashini'),
        timeout=30_000
    )
    
    print("Client created successfully")
    
    # Test ping
    ping_result = client.ping()
    print(f"Ping result: {ping_result}")
    
    # Test query API
    query_api = client.query_api()
    print("Query API created successfully")
    
    # Test a simple query
    query = f'from(bucket: "{os.getenv("INFLUXDB_BUCKET", "qos_metrics")}") |> range(start: -1m) |> limit(n:1)'
    print(f"Testing query: {query}")
    
    result = query_api.query(query, org=os.getenv('INFLUXDB_ORG', 'bhashini'))
    print(f"Query result: {result}")
    
    client.close()
    print("Connection test successful!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
