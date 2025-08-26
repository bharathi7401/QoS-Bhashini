#!/bin/bash
# Grafana entrypoint script to pre-render datasource configuration

set -e

echo "🔧 Pre-rendering Grafana datasource configuration..."

# Load environment variables from secrets file
if [ -f /secrets/influxdb_tokens.env ]; then
    echo "📁 Loading tokens from secrets file..."
    export $(cat /secrets/influxdb_tokens.env | xargs)
fi

# Pre-render datasource configuration
if [ -f /etc/grafana/provisioning/datasources/influxdb.yml.template ]; then
    echo "📝 Rendering datasource template..."
    sed "s/\${INFLUXDB_GRAFANA_TOKEN}/$INFLUXDB_GRAFANA_TOKEN/g; s/\${INFLUXDB_ORG}/$INFLUXDB_ORG/g; s/\${INFLUXDB_BUCKET}/$INFLUXDB_BUCKET/g" \
        /etc/grafana/provisioning/datasources/influxdb.yml.template > /etc/grafana/provisioning/datasources/influxdb.yml
    echo "✅ Datasource configuration rendered successfully"
else
    echo "⚠️  Datasource template not found, using default configuration"
fi

# Start Grafana
echo "🚀 Starting Grafana..."
exec /run.sh
