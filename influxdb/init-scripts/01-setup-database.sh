#!/bin/bash
# InfluxDB initialization script for Bhashini QoS monitoring

set -e

echo "Setting up InfluxDB for Bhashini QoS monitoring..."

# Wait for InfluxDB to be ready
echo "Waiting for InfluxDB to be ready..."
until curl -s http://localhost:8086/health > /dev/null; do
    echo "Waiting for InfluxDB..."
    sleep 2
done

echo "InfluxDB is ready, setting up database..."

# Create organization if it doesn't exist
echo "Creating organization: ${DOCKER_INFLUXDB_INIT_ORG}"
influx org create \
    --name "${DOCKER_INFLUXDB_INIT_ORG}" \
    --token "${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}" \
    --host http://localhost:8086 \
    --skip-verify || echo "Organization already exists"

# Get organization ID
ORG_ID=$(influx org list \
    --token "${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}" \
    --host http://localhost:8086 \
    --skip-verify | grep "${DOCKER_INFLUXDB_INIT_ORG}" | awk '{print $1}')

echo "Organization ID: ${ORG_ID}"

# Create main bucket for QoS metrics
echo "Creating main bucket: ${DOCKER_INFLUXDB_INIT_BUCKET}"
influx bucket create \
    --name "${DOCKER_INFLUXDB_INIT_BUCKET}" \
    --org "${DOCKER_INFLUXDB_INIT_ORG}" \
    --token "${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}" \
    --host http://localhost:8086 \
    --skip-verify \
    --retention 30d || echo "Bucket already exists"

# Create aggregated metrics bucket for long-term storage
echo "Creating aggregated metrics bucket: qos_metrics_aggregated"
influx bucket create \
    --name "qos_metrics_aggregated" \
    --org "${DOCKER_INFLUXDB_INIT_ORG}" \
    --token "${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}" \
    --host http://localhost:8086 \
    --skip-verify \
    --retention 365d || echo "Aggregated bucket already exists"

# Create downsampling task for aggregating metrics
echo "Creating downsampling task..."
influx task create \
    --name "qos_metrics_downsampling" \
    --org "${DOCKER_INFLUXDB_INIT_ORG}" \
    --token "${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}" \
    --host http://localhost:8086 \
    --skip-verify \
    --every 1h \
    --query "
import \"influxdata/influxdb/schema\"
import \"influxdata/influxdb/v1\"

from(bucket: \"${DOCKER_INFLUXDB_INIT_BUCKET}\")
    |> range(start: -1h)
    |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")
    |> filter(fn: (r) => r._field == \"value\")
    |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
    |> to(bucket: \"qos_metrics_aggregated\")
" || echo "Downsampling task already exists"

echo "InfluxDB setup completed successfully!"
echo "Buckets created:"
echo "  - ${DOCKER_INFLUXDB_INIT_BUCKET} (30 days retention)"
echo "  - qos_metrics_aggregated (365 days retention)"
echo "Downsampling task created for hourly aggregation"
