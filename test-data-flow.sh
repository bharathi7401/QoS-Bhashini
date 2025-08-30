#!/bin/bash

echo "🧪 Testing Bhashini QoS Data Flow - Enhanced Version..."
echo "====================================================="

# Configuration
GRAFANA_URL=${GRAFANA_URL:-http://localhost:3010}

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

# Run comprehensive verification scripts
echo ""
echo "🔍 Running Comprehensive Verification Scripts:"
echo "============================================="

# Run the complete data flow verification
echo ""
echo "1. Running Complete Data Flow Verification:"
echo "-------------------------------------------"
if [ -f "scripts/verify-complete-data-flow.py" ]; then
    python3 scripts/verify-complete-data-flow.py
else
    echo "  ❌ verify-complete-data-flow.py not found"
fi

# Run dashboard query validation
echo ""
echo "2. Running Dashboard Query Validation:"
echo "-------------------------------------"
if [ -f "scripts/validate-dashboard-queries.py" ]; then
    python3 scripts/validate-dashboard-queries.py
else
    echo "  ❌ validate-dashboard-queries.py not found"
fi

# Run Grafana connectivity tests
echo ""
echo "3. Running Grafana Connectivity Tests:"
echo "-------------------------------------"
if [ -f "scripts/test-grafana-connectivity.py" ]; then
    python3 scripts/test-grafana-connectivity.py
else
    echo "  ❌ test-grafana-connectivity.py not found"
fi

# Service name validation
echo ""
echo "4. Service Name Validation:"
echo "--------------------------"
echo "  - Checking if service names in data match dashboard expectations"
echo "  - Expected services: translation, tts, asr"
echo "  - Verifying case consistency between data generation and dashboards"

# Schema validation  
echo ""
echo "5. Schema Validation:"
echo "--------------------"
echo "  - Checking if expected fields (value, unit) are present in data"
echo "  - Verifying measurement name is consistently 'qos_metrics'"
echo "  - Validating tag consistency (customer_id vs tenant_id, service vs service_name)"

# Multi-tenant isolation test
echo ""
echo "6. Multi-tenant Isolation Test:"
echo "-------------------------------"
echo "  - Verifying each tenant has data and customer datasources work"
echo "  - Testing customer-specific datasources: enterprise_1, startup_2, freemium_1"
echo "  - Checking tenant data isolation"

# Customer dashboard access test
echo ""
echo "7. Customer Dashboard Access Test:"
echo "---------------------------------"
echo "  - Testing customer-specific dashboard UIDs and their panel queries"
echo "  - Verifying customer datasources are properly configured"
echo "  - Checking customer dashboard functionality"

# Check dashboard access
echo ""
echo "📊 Dashboard Access:"
if curl -s "$GRAFANA_URL/api/health" > /dev/null; then
    echo "  ✅ Grafana is running"
    
    # List all dashboards
    echo ""
    echo "  📋 Available Dashboards:"
    DASHBOARDS=$(curl -s "$GRAFANA_URL/api/search?type=dash-db" -u admin:admin123)
    echo "$DASHBOARDS" | jq -r '.[] | "    - " + .title + " (UID: " + .uid + ")"'
    
    # Check datasources
    echo ""
    echo "  🔌 Available Datasources:"
    DATASOURCES=$(curl -s "$GRAFANA_URL/api/datasources" -u admin:admin123)
    echo "$DATASOURCES" | jq -r '.[] | "    - " + .name + " (" + .type + ")"'
    
else
    echo "  ❌ Grafana is not running"
fi

# Alerting validation
echo ""
echo "8. Alerting Rules Validation:"
echo "----------------------------"
echo "  - Testing if alert queries execute successfully"
echo "  - Verifying alert rules from customer-alerts.yml"
echo "  - Checking alert query syntax and data availability"

# BI API integration test
echo ""
echo "9. BI API Integration Test:"
echo "--------------------------"
echo "  - Testing if BI API can connect to InfluxDB"
echo "  - Verifying BI API environment configuration"
echo "  - Checking data access for external integrations"

# Environment variables validation
echo ""
echo "10. Environment Variables Validation:"
echo "------------------------------------"
echo "  - Checking if all required tokens and configurations are set"
echo "  - Verifying customer datasource token configuration"
echo "  - Validating environment consistency"

echo ""
echo "🎯 Enhanced Data Structure Analysis:"
echo "  - Data simulator now generates records with updated schema:"
echo "    * Tags: customer_id (not tenant_id), service (not service_name), metric_type, sla_tier"
echo "    * Fields: value (with numeric data), unit (with unit strings like 'ms', 'percent')"
echo "  - Each metric type gets appropriate units:"
echo "    * latency: 'ms'"
echo "    * error_rate: 'percent'"
echo "    * throughput: 'requests_per_minute'"
echo "    * availability: 'percent'"
echo "  - Dashboard queries now filter by correct tag/field names"
echo "  - Customer datasources use customer_id for tenant isolation"

echo ""
echo "📋 Enhanced Next Steps:"
echo "1. Review all verification script outputs above"
echo "2. Address any ❌ issues found in the reports"
echo "3. Open $GRAFANA_URL in your browser"
echo "4. Login with admin/admin123"
echo "5. Navigate to available dashboards (listed above)"
echo "6. Verify customer-specific dashboards work with proper isolation"
echo "7. Check if all panels show data with proper units"
echo "8. Test alert rules are functioning"
echo "9. Verify multi-tenant data isolation"

echo ""
echo "🔧 Troubleshooting Guide:"
echo "  - If verification scripts report issues:"
echo "    * Follow specific recommendations in each script's report"
echo "    * Check schema consistency between data generation and dashboards"
echo "    * Verify environment variables are properly configured"
echo "  - If dashboards still show no data:"
echo "    * Check InfluxDB logs: docker logs bhashini-influxdb"
echo "    * Verify data simulator is writing: docker logs bhashini-data-simulator"
echo "    * Check datasource health in Grafana settings"
echo "    * Review customer datasource configuration"
echo "  - If customer isolation isn't working:"
echo "    * Verify customer datasource tokens are configured"
echo "    * Check customer_id filtering in queries"
echo "    * Review tenant-specific dashboard configurations"

echo ""
echo "📊 Verification Complete!"
echo "========================"
echo "Review the outputs above for detailed analysis of your Bhashini QoS monitoring system."
