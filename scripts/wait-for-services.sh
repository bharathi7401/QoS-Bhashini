#!/bin/bash

set -e

# Check if services list was provided
if [ $# -lt 2 ]; then
    echo "❌ Usage: $0 <service1,service2,...> <command> [args...]"
    echo "   Example: $0 influxdb,postgres python3 /app/app.py"
    exit 1
fi

SERVICES_LIST="$1"
shift

echo "🔍 Waiting for services to be ready: $SERVICES_LIST"

# Configuration
MAX_ATTEMPTS=30
INITIAL_DELAY=2

# Function to check InfluxDB health
check_influxdb() {
    if curl -s http://localhost:8086/health > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check PostgreSQL health
check_postgres() {
    if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check Grafana health
check_grafana() {
    if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check a specific service
check_service() {
    local service_name="$1"
    
    case "$service_name" in
        "influxdb")
            check_influxdb
            ;;
        "postgres"|"postgresql")
            check_postgres
            ;;
        "grafana")
            check_grafana
            ;;
        *)
            echo "❌ Unknown service: $service_name"
            echo "   Supported services: influxdb, postgres, grafana"
            return 1
            ;;
    esac
}

# Parse services from comma-separated list
IFS=',' read -ra SERVICES <<< "$SERVICES_LIST"

# Wait for each service
for service in "${SERVICES[@]}"; do
    echo "🔍 Checking service: $service"
    
    attempt=1
    delay=$INITIAL_DELAY
    
    while [ $attempt -le $MAX_ATTEMPTS ]; do
        echo "⏳ Checking $service health... (attempt $attempt/$MAX_ATTEMPTS)"
        
        if check_service "$service"; then
            echo "✅ $service is healthy and ready!"
            break
        fi
        
        if [ $attempt -eq $MAX_ATTEMPTS ]; then
            echo "❌ $service failed to become ready after $MAX_ATTEMPTS attempts"
            echo "❌ Timeout waiting for $service health check"
            exit 1
        fi
        
        echo "⏳ $service not ready, waiting ${delay}s before retry..."
        sleep $delay
        
        # Exponential backoff with cap at 10 seconds
        delay=$((delay * 2))
        if [ $delay -gt 10 ]; then
            delay=10
        fi
        
        attempt=$((attempt + 1))
    done
done

echo "✅ All services are ready: $SERVICES_LIST"
echo "🚀 Starting target service: $*"
exec "$@"