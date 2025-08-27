#!/bin/bash
# Grafana entrypoint script to pre-render datasource and alerting configuration

set -e

echo "🔧 Pre-rendering Grafana configuration..."

# Load environment variables from secrets file
if [ -f /secrets/influxdb_tokens.env ]; then
    echo "📁 Loading tokens from secrets file..."
    export $(cat /secrets/influxdb_tokens.env | xargs)
fi

# Load notification configuration from secrets file
if [ -f /secrets/notification_config.env ]; then
    echo "📁 Loading notification config from secrets file..."
    export $(cat /secrets/notification_config.env | xargs)
fi

# Check required notification variables (warning only for now)
if [ -z "$SMTP_HOST" ] || [ -z "$SMTP_PASSWORD" ] || [ -z "$SLACK_WEBHOOK_URL" ]; then
    echo "⚠️  Warning: Notification variables not configured - alerting will be limited"
    echo "   Set SMTP_HOST, SMTP_PASSWORD, and SLACK_WEBHOOK_URL for full functionality"
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

# Pre-render alerting configuration files
echo "📝 Rendering alerting configuration templates..."
for template in /etc/grafana/provisioning/alerting/*.yml.template; do
    if [ -f "$template" ]; then
        filename=$(basename "$template" .template)
        echo "📝 Rendering $filename..."
        envsubst < "$template" > "/etc/grafana/provisioning/alerting/$filename"
        echo "✅ $filename rendered successfully"
    fi
done

# Start Grafana
echo "🚀 Starting Grafana..."
exec /run.sh
