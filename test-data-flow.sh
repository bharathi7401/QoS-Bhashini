#!/bin/bash

echo "🧪 Testing Bhashini QoS Data Flow..."
echo "====================================="

# Check data simulator status
echo "📊 Data Simulator Status:"
DATA_STATUS=$(curl -s http://localhost:8000/status)
echo "  - Running: $(echo "$DATA_STATUS" | jq -r '.running')"
echo "  - Metrics Generated: $(echo "$DATA_STATUS" | jq -r '.metrics_generated')"
echo "  - Last Generation: $(echo "$DATA_STATUS" | jq -r '.last_generation')"

# Check if data is being written to InfluxDB
echo ""
echo "📈 Data Generation Check:"
echo "  - Data simulator is generating $(echo "$DATA_STATUS" | jq -r '.config.services_count') services"
echo "  - Data simulator is generating $(echo "$DATA_STATUS" | jq -r '.config.tenants_count') tenants"
echo "  - Total metrics per batch: $(echo "$DATA_STATUS" | jq -r '.config.services_count') × $(echo "$DATA_STATUS" | jq -r '.config.tenants_count') × 4 = $(( $(echo "$DATA_STATUS" | jq -r '.config.services_count') * $(echo "$DATA_STATUS" | jq -r '.config.tenants_count') * 4 ))"

# Check dashboard access
echo ""
echo "📊 Dashboard Access:"
if curl -s "http://localhost:3000/api/health" > /dev/null; then
    echo "  ✅ Grafana is running"
    
    # Check if dashboard is accessible
    if curl -s "http://localhost:3000/api/dashboards/uid/bhashini-provider-overview" -u admin:admin123 > /dev/null; then
        echo "  ✅ Dashboard is accessible"
        
        # Check panel queries
        echo ""
        echo "🔍 Panel Query Analysis:"
        
        # Get SLA Compliance panel query
        SLA_QUERY=$(curl -s "http://localhost:3000/api/dashboards/uid/bhashini-provider-overview" -u admin:admin123 | jq -r '.dashboard.panels[] | select(.title == "SLA Compliance") | .targets[0].query')
        echo "  - SLA Compliance Query:"
        echo "    $SLA_QUERY"
        
        # Get Capacity Utilization panel query
        CAP_QUERY=$(curl -s "http://localhost:3000/api/dashboards/uid/bhashini-provider-overview" -u admin:admin123 | jq -r '.dashboard.panels[] | select(.title == "Capacity Utilization") | .targets[0].query')
        echo "  - Capacity Utilization Query:"
        echo "    $CAP_QUERY"
        
    else
        echo "  ❌ Dashboard access failed"
    fi
else
    echo "  ❌ Grafana is not running"
fi

echo ""
echo "🎯 Data Structure Analysis:"
echo "  - Data simulator generates records with fields: latency, error_rate, throughput, availability"
echo "  - Each field becomes a separate data point in InfluxDB with _field set to the field name"
echo "  - Dashboard queries filter by _field values and group by tenant_id, service_name, _field"
echo "  - This should now match the data structure being generated"

echo ""
echo "📋 Next Steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Login with admin/admin123"
echo "3. Navigate to Bhashini Provider Overview dashboard"
echo "4. Check if panels now show data instead of 'No data'"
echo "5. Verify SLA Compliance shows percentage values"
echo "6. Check Capacity Utilization shows throughput data"
echo "7. Verify Performance Matrix displays service-tenant data"
echo "8. Check Tenant Performance Ranking for sorted data"

echo ""
echo "🔧 If still no data:"
echo "  - Check InfluxDB logs: docker logs bhashini-influxdb"
echo "  - Verify data simulator is writing: docker logs bhashini-data-simulator"
echo "  - Check datasource configuration in Grafana"
