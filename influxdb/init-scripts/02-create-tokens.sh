#!/bin/bash
# InfluxDB token creation script for Bhashini QoS monitoring

set -e

echo "Creating InfluxDB API tokens for Bhashini QoS monitoring..."

# Wait for InfluxDB to be ready
echo "Waiting for InfluxDB to be ready..."
until curl -s http://localhost:8086/health > /dev/null; do
    echo "Waiting for InfluxDB..."
    sleep 2
done

# Get organization ID
ORG_ID=$(influx org list \
    --token "${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}" \
    --host http://localhost:8086 \
    --skip-verify | grep "${DOCKER_INFLUXDB_INIT_ORG}" | awk '{print $1}')

echo "Organization ID: ${ORG_ID}"

# Create token for data simulator (read-write access to main bucket)
echo "Creating token for data simulator..."
SIMULATOR_JSON=$(influx auth create \
    --org "${DOCKER_INFLUXDB_INIT_ORG}" \
    --token "${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}" \
    --host http://localhost:8086 \
    --skip-verify \
    --write-bucket "${DOCKER_INFLUXDB_INIT_BUCKET}" \
    --read-bucket "${DOCKER_INFLUXDB_INIT_BUCKET}" \
    --description "Data Simulator Token" --json)
SIMULATOR_TOKEN=$(echo "$SIMULATOR_JSON" | jq -r '.[0].token')

echo "Data Simulator Token: ${SIMULATOR_TOKEN}"

# Create token for Grafana (read-only access to all buckets)
echo "Creating token for Grafana..."
GRAFANA_JSON=$(influx auth create \
    --org "${DOCKER_INFLUXDB_INIT_ORG}" \
    --token "${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}" \
    --host http://localhost:8086 \
    --skip-verify \
    --read-bucket "${DOCKER_INFLUXDB_INIT_BUCKET}" \
    --read-bucket "qos_metrics_aggregated" \
    --description "Grafana Read-Only Token" --json)
GRAFANA_TOKEN=$(echo "$GRAFANA_JSON" | jq -r '.[0].token')

echo "Grafana Token: ${GRAFANA_TOKEN}"

# Create token for verification scripts (read access to main bucket)
echo "Creating token for verification scripts..."
VERIFICATION_JSON=$(influx auth create \
    --token "${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}" \
    --host http://localhost:8086 \
    --skip-verify \
    --read-bucket "${DOCKER_INFLUXDB_INIT_BUCKET}" \
    --description "Verification Scripts Token" --json)
VERIFICATION_TOKEN=$(echo "$VERIFICATION_JSON" | jq -r '.[0].token')

echo "Verification Token: ${VERIFICATION_TOKEN}"

# Validate tokens are non-empty
if [ -z "$SIMULATOR_TOKEN" ] || [ -z "$GRAFANA_TOKEN" ] || [ -z "$VERIFICATION_TOKEN" ]; then
    echo "❌ Error: One or more tokens are empty. Token generation failed."
    echo "SIMULATOR_TOKEN: ${SIMULATOR_TOKEN}"
    echo "GRAFANA_TOKEN: ${GRAFANA_TOKEN}"
    echo "VERIFICATION_TOKEN: ${VERIFICATION_TOKEN}"
    exit 1
fi

echo "✅ All tokens generated successfully"

# Save tokens to environment file for easy access
echo "Saving tokens to environment file..."
cat > /secrets/influxdb_tokens.env << EOF
# InfluxDB API Tokens for Bhashini QoS Monitoring
# Generated on $(date)

# Data Simulator Token (Read-Write access to main bucket)
INFLUXDB_SIMULATOR_TOKEN=${SIMULATOR_TOKEN}

# Grafana Token (Read-Only access to all buckets)
INFLUXDB_GRAFANA_TOKEN=${GRAFANA_TOKEN}

# Verification Scripts Token (Read access to main bucket)
INFLUXDB_VERIFICATION_TOKEN=${VERIFICATION_TOKEN}

# Organization and Bucket
INFLUXDB_ORG=${DOCKER_INFLUXDB_INIT_ORG}
INFLUXDB_BUCKET=${DOCKER_INFLUXDB_INIT_BUCKET}
EOF

echo "Tokens created successfully!"
echo "Token summary:"
echo "  - Data Simulator: ${SIMULATOR_TOKEN}"
echo "  - Grafana: ${GRAFANA_TOKEN}"
echo "  - Verification: ${VERIFICATION_TOKEN}"
echo ""
echo "Tokens saved to /secrets/influxdb_tokens.env"
echo "Copy these values to your .env file for the respective services."
