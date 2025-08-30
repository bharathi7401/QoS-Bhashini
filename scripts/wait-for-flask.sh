#!/bin/bash

set -e

echo "🔍 Waiting for Flask application to be ready..."

# Configuration
MAX_ATTEMPTS=30
INITIAL_DELAY=2
FLASK_PORT="${PORT:-80}"
FLASK_URL="http://localhost:${FLASK_PORT}"

# Try both health endpoint and root endpoint
HEALTH_ENDPOINTS=("${FLASK_URL}/health" "${FLASK_URL}/")

# Function to check Flask health
check_flask() {
    for endpoint in "${HEALTH_ENDPOINTS[@]}"; do
        if curl -s "$endpoint" > /dev/null 2>&1; then
            return 0
        fi
    done
    return 1
}

# Wait for Flask with exponential backoff
attempt=1
delay=$INITIAL_DELAY

while [ $attempt -le $MAX_ATTEMPTS ]; do
    echo "⏳ Checking Flask application health... (attempt $attempt/$MAX_ATTEMPTS)"
    
    if check_flask; then
        echo "✅ Flask application is healthy and ready on port $FLASK_PORT!"
        break
    fi
    
    if [ $attempt -eq $MAX_ATTEMPTS ]; then
        echo "❌ Flask application failed to become ready after $MAX_ATTEMPTS attempts"
        echo "❌ Timeout waiting for Flask application at $FLASK_URL"
        exit 1
    fi
    
    echo "⏳ Flask application not ready, waiting ${delay}s before retry..."
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