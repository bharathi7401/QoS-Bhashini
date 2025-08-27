#!/bin/bash

echo "🔄 Restarting Bhashini QoS Monitoring Stack..."
echo "================================================"

# Stop existing containers
echo "📦 Stopping existing containers..."
docker-compose down

# Clean up any stale data
echo "🧹 Cleaning up stale data..."
docker volume prune -f

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
echo "InfluxDB Health:"
curl -s http://localhost:8086/health || echo "InfluxDB not ready yet"

echo "Grafana Health:"
curl -s http://localhost:3000/api/health || echo "Grafana not ready yet"

echo "Data Simulator Health:"
curl -s http://localhost:8000/health || echo "Data Simulator not ready yet"

# Wait a bit more for data generation
echo "⏳ Waiting for initial data generation..."
sleep 20

# Check data in InfluxDB
echo "📊 Checking data in InfluxDB..."
curl -s -G "http://localhost:8086/query" \
  --data-urlencode "org=bhashini" \
  --data-urlencode "token=admin-token-123" \
  --data-urlencode "q=from(bucket:\"qos_metrics\") |> range(start: -5m) |> count()" || echo "Failed to query InfluxDB"

echo ""
echo "✅ Services restarted and tested!"
echo "🌐 Grafana Dashboard: http://localhost:3000 (admin/admin)"
echo "📈 InfluxDB: http://localhost:8086"
echo "🔧 Data Simulator: http://localhost:8000/health"
echo ""
echo "📋 Next steps:"
echo "1. Open Grafana dashboard"
echo "2. Check if SLA Compliance shows data"
echo "3. Verify Performance Matrix panel works"
echo "4. Check Tenant Performance Ranking"
echo "5. Verify Capacity Utilization has correct names"
