#!/bin/bash

set -e

echo "🔍 Waiting for InfluxDB to be ready..."

# Configuration
MAX_ATTEMPTS=30
INITIAL_DELAY=2
INFLUXDB_URL="http://localhost:8086/health"

# Function to check InfluxDB health
check_influxdb() {
    if curl -s "$INFLUXDB_URL" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Wait for InfluxDB with exponential backoff
attempt=1
delay=$INITIAL_DELAY

while [ $attempt -le $MAX_ATTEMPTS ]; do
    echo "⏳ Checking InfluxDB health... (attempt $attempt/$MAX_ATTEMPTS)"
    
    if check_influxdb; then
        echo "✅ InfluxDB is healthy and ready!"
        break
    fi
    
    if [ $attempt -eq $MAX_ATTEMPTS ]; then
        echo "❌ InfluxDB failed to become ready after $MAX_ATTEMPTS attempts"
        echo "❌ Timeout waiting for InfluxDB health check at $INFLUXDB_URL"
        exit 1
    fi
    
    echo "⏳ InfluxDB not ready, waiting ${delay}s before retry..."
    sleep $delay
    
    # Exponential backoff with cap at 10 seconds
    delay=$((delay * 2))
    if [ $delay -gt 10 ]; then
        delay=10
    fi
    
    attempt=$((attempt + 1))
done

echo "🚀 Starting target service: $*"
exec "$@"