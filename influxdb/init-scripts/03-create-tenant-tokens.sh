#!/bin/bash
# InfluxDB tenant-specific token creation script for multi-tenant access

set -e

echo "Creating InfluxDB tenant-specific tokens for multi-tenant access..."

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

# Create provider cross-tenant token (read access to all tenant data)
echo "Creating provider cross-tenant token..."
PROVIDER_CROSS_TENANT_TOKEN=$(influx auth create \
    --org "${DOCKER_INFLUXDB_INIT_ORG}" \
    --token "${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}" \
    --host http://localhost:8086 \
    --skip-verify \
    --read-bucket "${DOCKER_INFLUXDB_INIT_BUCKET}" \
    --read-bucket "qos_metrics_aggregated" \
    --description "Provider Cross-Tenant Access Token" | grep -o '[a-zA-Z0-9_-]*$' | head -1)

echo "Provider Cross-Tenant Token: ${PROVIDER_CROSS_TENANT_TOKEN}"

# Create customer-specific tokens with tenant isolation
CUSTOMER_TOKENS=()

for i in {1..3}; do
    CUSTOMER_NAME="customer_${i}"
    echo "Creating token for ${CUSTOMER_NAME}..."
    
    # Create read-only token for customer
    CUSTOMER_TOKEN=$(influx auth create \
        --org "${DOCKER_INFLUXDB_INIT_ORG}" \
        --token "${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}" \
        --host http://localhost:8086 \
        --skip-verify \
        --read-bucket "${DOCKER_INFLUXDB_INIT_BUCKET}" \
        --description "${CUSTOMER_NAME} Tenant Access Token" | grep -o '[a-zA-Z0-9_-]*$' | head -1)
    
    CUSTOMER_TOKENS+=("${CUSTOMER_TOKEN}")
    echo "${CUSTOMER_NAME} Token: ${CUSTOMER_TOKEN}"
done

# Create tenant-specific buckets for data isolation (optional)
echo "Creating tenant-specific buckets for data isolation..."
for i in {1..3}; do
    BUCKET_NAME="qos_metrics_tenant_${i}"
    echo "Creating bucket: ${BUCKET_NAME}"
    
    influx bucket create \
        --name "${BUCKET_NAME}" \
        --org "${DOCKER_INFLUXDB_INIT_ORG}" \
        --token "${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}" \
        --host http://localhost:8086 \
        --skip-verify \
        --retention 30d || echo "Bucket ${BUCKET_NAME} already exists"
done

# Save tokens to environment file
echo "Saving tenant tokens to environment file..."
cat > /tmp/tenant_tokens.env << EOF
# InfluxDB Tenant Tokens for Multi-Tenant Access
# Generated on $(date)

# Provider Cross-Tenant Token (Read access to all tenant data)
INFLUXDB_PROVIDER_CROSS_TENANT_TOKEN=${PROVIDER_CROSS_TENANT_TOKEN}

# Customer Tenant Tokens (Read access to specific tenant data)
INFLUXDB_CUSTOMER_1_TOKEN=${CUSTOMER_TOKENS[0]}
INFLUXDB_CUSTOMER_2_TOKEN=${CUSTOMER_TOKENS[1]}
INFLUXDB_CUSTOMER_3_TOKEN=${CUSTOMER_TOKENS[2]}

# Organization and Bucket Information
INFLUXDB_ORG=${DOCKER_INFLUXDB_INIT_ORG}
INFLUXDB_BUCKET=${DOCKER_INFLUXDB_INIT_BUCKET}

# Tenant Bucket Names
INFLUXDB_TENANT_BUCKET_1=qos_metrics_tenant_1
INFLUXDB_TENANT_BUCKET_2=qos_metrics_tenant_2
INFLUXDB_TENANT_BUCKET_3=qos_metrics_tenant_3
EOF

echo "Tenant tokens created successfully!"
echo "Token summary:"
echo "  - Provider Cross-Tenant: ${PROVIDER_CROSS_TENANT_TOKEN}"
echo "  - Customer 1: ${CUSTOMER_TOKENS[0]}"
echo "  - Customer 2: ${CUSTOMER_TOKENS[1]}"
echo "  - Customer 3: ${CUSTOMER_TOKENS[2]}"
echo ""
echo "Tenant buckets created:"
echo "  - qos_metrics_tenant_1 (30 days retention)"
echo "  - qos_metrics_tenant_2 (30 days retention)"
echo "  - qos_metrics_tenant_3 (30 days retention)"
echo ""
echo "Tokens saved to /tmp/tenant_tokens.env"
echo "Copy these values to your .env file for multi-tenant configuration."
