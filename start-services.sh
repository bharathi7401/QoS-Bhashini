#!/bin/bash

echo "🚀 Starting Bhashini QoS Monitoring System..."

# Create necessary directories
mkdir -p /var/lib/influxdb2 /var/lib/grafana /var/log/supervisor

# Copy Grafana configuration
cp -r /app/grafana/provisioning /etc/grafana/
cp /app/grafana/config/grafana.ini /etc/grafana/

# Set environment variables
export DOCKER_INFLUXDB_INIT_USERNAME=admin
export DOCKER_INFLUXDB_INIT_PASSWORD=admin123
export DOCKER_INFLUXDB_INIT_ORG=bhashini
export DOCKER_INFLUXDB_INIT_BUCKET=qos_metrics
export DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=admin-token-123
export GF_SECURITY_ADMIN_USER=admin
export GF_SECURITY_ADMIN_PASSWORD=admin123

# Initialize InfluxDB if not already done
if [ ! -f /var/lib/influxdb2/.initialized ]; then
    echo "📊 Initializing InfluxDB..."
    
    # Start InfluxDB in background
    influxd --engine-path /var/lib/influxdb2/engine --bolt-path /var/lib/influxdb2/influxd.bolt --http-bind-address 127.0.0.1:8086 &
    INFLUX_PID=$!
    
    # Wait for InfluxDB to be ready
    echo "⏳ Waiting for InfluxDB to start..."
    for i in {1..30}; do
        if curl -s http://127.0.0.1:8086/health > /dev/null 2>&1; then
            echo "✅ InfluxDB is ready!"
            break
        fi
        echo "⏳ Waiting for InfluxDB... ($i/30)"
        sleep 2
    done
    
    # Setup InfluxDB
    echo "🔧 Setting up InfluxDB..."
    influx setup --username admin --password admin123 --org bhashini --bucket qos_metrics --token admin-token-123 --force
    
    # Mark as initialized
    touch /var/lib/influxdb2/.initialized
    
    # Stop InfluxDB for proper startup
    kill $INFLUX_PID
    sleep 5
fi

echo "🔧 Starting supervisord..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
