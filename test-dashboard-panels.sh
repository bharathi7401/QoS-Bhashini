#!/bin/bash

echo "🧪 Testing Bhashini QoS Dashboard Panels..."
echo "============================================="

# Check if services are running
echo "🔍 Checking service status..."
if ! curl -s http://localhost:3000/api/health > /dev/null; then
    echo "❌ Grafana is not running"
    exit 1
fi

if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Data Simulator is not running"
    exit 1
fi

echo "✅ All services are running"

# Test dashboard access
echo "📊 Testing dashboard access..."
DASHBOARD_RESPONSE=$(curl -s "http://localhost:3000/api/dashboards/uid/bhashini-provider-overview" -u admin:admin123)

if echo "$DASHBOARD_RESPONSE" | grep -q "Unauthorized"; then
    echo "❌ Dashboard access failed - authentication error"
    exit 1
fi

if echo "$DASHBOARD_RESPONSE" | grep -q "not found"; then
    echo "❌ Dashboard not found"
    exit 1
fi

echo "✅ Dashboard access successful"

# Check data generation
echo "📈 Checking data generation..."
DATA_SIMULATOR_STATUS=$(curl -s http://localhost:8000/status)
METRICS_COUNT=$(echo "$DATA_SIMULATOR_STATUS" | jq -r '.metrics_generated')

if [ "$METRICS_COUNT" -gt 0 ]; then
    echo "✅ Data simulator has generated $METRICS_COUNT metrics"
else
    echo "❌ No metrics generated"
    exit 1
fi

# Test datasource connectivity
echo "🔌 Testing datasource connectivity..."
DATASOURCES=$(curl -s "http://localhost:3000/api/datasources" -u admin:admin123)

if echo "$DATASOURCES" | grep -q "InfluxDB-Provider-CrossTenant"; then
    echo "✅ Provider cross-tenant datasource found"
else
    echo "❌ Provider cross-tenant datasource missing"
fi

if echo "$DATASOURCES" | grep -q "InfluxDB-QoS-Metrics"; then
    echo "✅ QoS metrics datasource found"
else
    echo "❌ QoS metrics datasource missing"
fi

# Check specific panels
echo "🎯 Checking specific panel configurations..."

# Check Performance Matrix panel
if echo "$DASHBOARD_RESPONSE" | grep -q '"title": "Performance Matrix"'; then
    echo "✅ Performance Matrix panel found"
else
    echo "❌ Performance Matrix panel missing"
fi

# Check SLA Compliance panel
if echo "$DASHBOARD_RESPONSE" | grep -q '"title": "SLA Compliance"'; then
    echo "✅ SLA Compliance panel found"
else
    echo "❌ SLA Compliance panel missing"
fi

# Check Tenant Performance Ranking panel
if echo "$DASHBOARD_RESPONSE" | grep -q '"title": "Tenant Performance Ranking"'; then
    echo "✅ Tenant Performance Ranking panel found"
else
    echo "❌ Tenant Performance Ranking panel missing"
fi

# Check Capacity Utilization panel
if echo "$DASHBOARD_RESPONSE" | grep -q '"title": "Capacity Utilization"'; then
    echo "✅ Capacity Utilization panel found"
else
    echo "❌ Capacity Utilization panel missing"
fi

echo ""
echo "🎉 Dashboard Panel Test Complete!"
echo "================================="
echo "📊 Dashboard URL: http://localhost:3000"
echo "🔑 Login: admin/admin123"
echo "📈 Data Simulator: http://localhost:8000/health"
echo ""
echo "📋 Next Steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Login with admin/admin123"
echo "3. Navigate to the Bhashini Provider Overview dashboard"
echo "4. Verify all panels are displaying data correctly"
echo "5. Check that SLA Compliance shows percentage values"
echo "6. Verify Performance Matrix displays service-tenant data"
echo "7. Check Tenant Performance Ranking for sorted data"
echo "8. Verify Capacity Utilization shows throughput data"
