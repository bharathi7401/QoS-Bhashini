#!/bin/bash
# Manual InfluxDB setup script for Bhashini QoS monitoring

echo "Setting up InfluxDB manually..."

# Wait for InfluxDB to be ready
echo "Waiting for InfluxDB to be ready..."
until docker exec bhashini-influxdb influx ping > /dev/null 2>&1; do
    echo "Waiting for InfluxDB..."
    sleep 2
done

echo "InfluxDB is ready!"

# Create organization
echo "Creating organization: bhashini"
docker exec bhashini-influxdb influx org create --name bhashini --token admin-token-123 --host http://127.0.0.1:8086 --skip-verify

# Get organization ID
echo "Getting organization ID..."
ORG_ID=$(docker exec bhashini-influxdb influx org list --token admin-token-123 --host http://127.0.0.1:8086 --skip-verify | grep bhashini | awk '{print $1}')

if [ -z "$ORG_ID" ]; then
    echo "ERROR: Could not get organization ID"
    exit 1
fi

echo "Organization ID: $ORG_ID"

# Create bucket
echo "Creating bucket: qos_metrics"
docker exec bhashini-influxdb influx bucket create --name qos_metrics --org bhashini --token admin-token-123 --host http://127.0.0.1:8086 --skip-verify --retention 30d

# Create a test token for the data simulator
echo "Creating test token for data simulator..."
docker exec bhashini-influxdb influx auth create --org bhashini --token admin-token-123 --host http://127.0.0.1:8086 --skip-verify --write-bucket qos_metrics --read-bucket qos_metrics

echo "InfluxDB setup completed!"
echo "You can now test the connection with:"
echo "docker exec bhashini-influxdb influx org list --token admin-token-123 --host http://localhost:8086 --skip-verify"
