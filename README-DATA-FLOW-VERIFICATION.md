# Bhashini QoS Data Flow Verification Guide

This comprehensive guide covers the complete data pipeline verification for the Bhashini QoS monitoring system, from data generation through InfluxDB to Grafana dashboards.

## Table of Contents

1. [Data Pipeline Overview](#data-pipeline-overview)
2. [Data Schema](#data-schema)
3. [Verification Scripts](#verification-scripts)
4. [Common Issues and Solutions](#common-issues-and-solutions)
5. [Troubleshooting Guide](#troubleshooting-guide)
6. [Multi-Tenant Setup](#multi-tenant-setup)
7. [Alerting Configuration](#alerting-configuration)
8. [Performance Expectations](#performance-expectations)
9. [Environment Variables](#environment-variables)
10. [Step-by-Step Verification Process](#step-by-step-verification-process)

## Data Pipeline Overview

The Bhashini QoS monitoring system consists of the following components:

```
Data Simulator → InfluxDB → Grafana Dashboards
     ↓              ↓            ↓
  Generates      Stores       Visualizes
  QoS Metrics    Time-Series   Dashboards
                 Data          & Alerts
```

### Component Flow:

1. **Data Simulator** (`data-simulator/`): Generates realistic QoS metrics for multiple services and tenants
2. **InfluxDB**: Stores time-series data with proper tenant isolation
3. **Grafana**: Provides dashboards and alerting for monitoring
4. **Customer Datasources**: Enable multi-tenant data isolation
5. **BI API**: Provides external access to metrics data

## Data Schema

### Updated Schema (Post-Fix)

The data schema has been standardized to ensure consistency between data generation and dashboard queries:

#### Measurement
- **Name**: `qos_metrics`

#### Tags
- **customer_id**: Tenant identifier (e.g., `enterprise_1`, `startup_2`, `freemium_1`)
- **service**: Service name (e.g., `translation`, `tts`, `asr`)
- **metric_type**: Type of metric (e.g., `latency`, `error_rate`, `throughput`, `availability`)
- **sla_tier**: Service level tier (e.g., `premium`, `standard`, `basic`)

#### Fields
- **value**: Numeric metric value
- **unit**: Unit of measurement with appropriate values:
  - `latency`: `'ms'` (milliseconds)
  - `error_rate`: `'percent'`
  - `throughput`: `'requests_per_minute'`
  - `availability`: `'percent'`

#### Example Data Point
```json
{
  "measurement": "qos_metrics",
  "tags": {
    "customer_id": "enterprise_1",
    "service": "translation",
    "metric_type": "latency",
    "sla_tier": "premium"
  },
  "fields": {
    "value": 45.67,
    "unit": "ms"
  },
  "time": "2025-01-15T10:30:00Z"
}
```

## Verification Scripts

### 1. Complete Data Flow Verification (`scripts/verify-complete-data-flow.py`)

**Purpose**: Comprehensive end-to-end verification of the entire data pipeline.

**What it tests**:
- InfluxDB connectivity and health
- Data simulator status and recent data generation
- Schema consistency between generated data and dashboard expectations
- Service name consistency (translation/tts/asr)
- Field presence validation (value and unit fields)
- Multi-tenant isolation
- Sample dashboard query execution
- Grafana datasource connectivity
- Alert query validation

**Usage**:
```bash
cd /path/to/QoS-Bhashini
python3 scripts/verify-complete-data-flow.py
```

**Expected Output**: Detailed report with ✅ successes and ❌ issues, plus recommendations.

### 2. Dashboard Query Validation (`scripts/validate-dashboard-queries.py`)

**Purpose**: Validates all dashboard and alert queries against actual data schema.

**What it tests**:
- Extracts Flux queries from all dashboard JSON files
- Executes queries against InfluxDB to verify syntax and data availability
- Checks for common schema mismatches
- Validates customer-specific dashboard queries
- Tests template variable queries for dropdown filters
- Validates alerting queries from YAML configuration files

**Usage**:
```bash
python3 scripts/validate-dashboard-queries.py
```

**Key Validations**:
- Service name consistency (`service` vs `service_name`)
- Customer ID usage (`customer_id` vs `tenant_id`)
- Field references (`value`, `unit`)
- Bucket and measurement name accuracy

### 3. Grafana Connectivity Test (`scripts/test-grafana-connectivity.py`)

**Purpose**: Tests Grafana's ability to connect to and query InfluxDB datasources.

**What it tests**:
- Grafana API health and accessibility
- All configured datasource health checks
- Query execution through Grafana's API
- Customer-specific datasource functionality
- Authentication token validation
- Network connectivity between containers

**Usage**:
```bash
python3 scripts/test-grafana-connectivity.py
```

**Customer Datasource Testing**: Validates each customer datasource (enterprise_1, startup_2, freemium_1) separately.

### 4. Enhanced Test Script (`test-data-flow.sh`)

**Purpose**: Orchestrates all verification scripts and provides comprehensive system status.

**Usage**:
```bash
chmod +x test-data-flow.sh
./test-data-flow.sh
```

**Enhanced Features**:
- Runs all verification scripts in sequence
- Provides detailed troubleshooting guidance
- Lists available dashboards and datasources
- Reports on schema improvements
- Offers step-by-step resolution steps

## Common Issues and Solutions

### Issue 1: Service Name Case Mismatch
**Problem**: Dashboards expect different service name casing than data generation.
**Solution**: 
- **Fixed in**: `data-simulator/metrics_generator.py`
- **Change**: Standardized to lowercase: `translation`, `tts`, `asr`
- **Verification**: Run verification scripts to confirm consistency

### Issue 2: Missing Unit Field
**Problem**: Dashboard queries expect `unit` field but data only contains `value`.
**Solution**:
- **Fixed in**: `data-simulator/metrics_generator.py`
- **Change**: Added `unit` field with appropriate values for each metric type
- **Verification**: Check field presence validation in verification scripts

### Issue 3: Tag Name Inconsistency
**Problem**: Data uses `tenant_id` and `service_name`, but dashboards expect `customer_id` and `service`.
**Solution**:
- **Fixed in**: `data-simulator/metrics_generator.py`, `grafana/provisioning/datasources/customer-influxdb.yml`
- **Change**: Standardized to `customer_id` and `service`
- **Verification**: Multi-tenant isolation tests confirm proper filtering

### Issue 4: Customer Datasource Token Configuration
**Problem**: Customer datasources reference undefined environment variables.
**Solution**:
- **Fixed in**: `docker-compose.yml`
- **Change**: Added environment variables with defaults:
  - `INFLUXDB_ENTERPRISE_1_TOKEN`
  - `INFLUXDB_STARTUP_2_TOKEN`
  - `INFLUXDB_FREEMIUM_1_TOKEN`
- **Verification**: Grafana connectivity tests validate token functionality

### Issue 5: Dashboard Query Filtering
**Problem**: Customer dashboards don't properly isolate tenant data.
**Solution**:
- **Fixed in**: `grafana/provisioning/datasources/customer-influxdb.yml`
- **Change**: Updated default queries to use `customer_id` filtering
- **Verification**: Customer-specific query testing confirms isolation

## Troubleshooting Guide

### No Data in Dashboards

1. **Check Data Simulator Status**:
   ```bash
   curl http://localhost:8000/status
   docker logs bhashini-data-simulator
   ```

2. **Verify InfluxDB Connectivity**:
   ```bash
   python3 scripts/verify-complete-data-flow.py
   ```

3. **Check Grafana Datasource Health**:
   ```bash
   python3 scripts/test-grafana-connectivity.py
   ```

4. **Validate Dashboard Queries**:
   ```bash
   python3 scripts/validate-dashboard-queries.py
   ```

### Schema Mismatch Issues

1. **Run Complete Verification**:
   ```bash
   ./test-data-flow.sh
   ```

2. **Check for Specific Issues**:
   - Service name casing
   - Field presence (`value`, `unit`)
   - Tag consistency (`customer_id`, `service`)

3. **Review Generated Data**:
   ```bash
   # Check recent data structure
   influx query 'from(bucket: "qos_metrics") |> range(start: -5m) |> limit(n: 1)'
   ```

### Customer Isolation Problems

1. **Verify Customer Datasources**:
   - Check Grafana datasource configuration
   - Validate customer tokens in `docker-compose.yml`
   - Test customer-specific queries

2. **Check Customer Dashboard Access**:
   ```bash
   curl -u admin:admin123 http://localhost:3010/api/dashboards/uid/CUSTOMER_DASHBOARD_UID
   ```

3. **Validate Data Filtering**:
   - Ensure `customer_id` is properly set in generated data
   - Verify customer datasource queries use correct filtering

### Performance Issues

1. **Check Resource Usage**:
   ```bash
   docker stats
   ```

2. **Monitor Data Generation Rate**:
   ```bash
   # Check metrics generation frequency
   curl http://localhost:8000/status | jq '.config'
   ```

3. **Optimize Query Performance**:
   - Review query complexity in dashboards
   - Check InfluxDB performance metrics
   - Consider data retention policies

## Multi-Tenant Setup

### Customer Configuration

The system supports three tenant tiers:

1. **enterprise_1**: Premium tier with enhanced SLA
2. **startup_2**: Standard tier for growing businesses  
3. **freemium_1**: Basic tier with limited resources

### Datasource Isolation

Each customer has a dedicated datasource in Grafana:
- **UID Pattern**: `InfluxDB-Customer-{customer_id}`
- **Token**: Separate environment variable per customer
- **Default Query**: Automatically filters by `customer_id`

### Data Isolation

Customer isolation is achieved through:
- **Tag-based filtering**: All queries automatically filter by `customer_id`
- **Dedicated datasources**: Each customer uses their own datasource
- **Access control**: Customers can only access their own data

## Alerting Configuration

### Alert Rules Location
- **Path**: `grafana/provisioning/alerting/customer-alerts.yml`
- **Validation**: Included in dashboard query validation script

### Common Alert Types
- **High Latency**: Triggers when response time exceeds threshold
- **High Error Rate**: Alerts on elevated error percentages
- **Low Availability**: Monitors service uptime
- **Throughput Anomalies**: Detects unusual traffic patterns

### Alert Query Testing
All alert queries are validated during the verification process to ensure:
- Proper syntax
- Data availability
- Threshold accuracy
- Customer isolation

## Performance Expectations

### Data Generation
- **Services**: 3 (translation, tts, asr)
- **Tenants**: 3 (enterprise_1, startup_2, freemium_1) 
- **Metrics per Batch**: 36 (3 × 3 × 4 metric types)
- **Generation Interval**: Configurable (default: 10 seconds)

### Healthy System Indicators
- ✅ Data simulator generates metrics consistently
- ✅ InfluxDB receives and stores data without errors
- ✅ All verification scripts report no critical issues
- ✅ Grafana dashboards display data within expected timeframes
- ✅ Customer datasources function with proper isolation
- ✅ Alert rules execute without errors

### Performance Benchmarks
- **Data Ingestion**: < 100ms per batch
- **Dashboard Load**: < 2 seconds for standard queries
- **Alert Evaluation**: < 5 seconds per rule
- **Customer Query Isolation**: < 500ms additional overhead

## Environment Variables

### Required Variables (with defaults)

#### InfluxDB Configuration
```bash
INFLUXDB_TOKEN=admin-token-123
INFLUXDB_ORG=bhashini
INFLUXDB_BUCKET=qos_metrics
```

#### Customer Datasource Tokens
```bash
INFLUXDB_ENTERPRISE_1_TOKEN=admin-token-123  # Use separate tokens in production
INFLUXDB_STARTUP_2_TOKEN=admin-token-123
INFLUXDB_FREEMIUM_1_TOKEN=admin-token-123
```

#### Grafana Configuration
```bash
INFLUXDB_GRAFANA_TOKEN=admin-token-123
INFLUXDB_PROVIDER_CROSS_TENANT_TOKEN=admin-token-123
```

#### Optional Configuration
```bash
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin123
SIMULATION_INTERVAL=10
LOG_LEVEL=INFO
```

### Production Security

In production environments:
1. **Generate unique tokens** for each customer datasource
2. **Use secure password management** for sensitive credentials
3. **Enable TLS encryption** for data transmission
4. **Implement proper access controls** for dashboard viewing
5. **Regular token rotation** for enhanced security

## Step-by-Step Verification Process

### For New Deployments

1. **Start the System**:
   ```bash
   docker-compose up -d
   ```

2. **Wait for Services to be Healthy**:
   ```bash
   docker-compose ps
   # All services should show "healthy" status
   ```

3. **Run Complete Verification**:
   ```bash
   ./test-data-flow.sh
   ```

4. **Address Any Issues**:
   - Follow recommendations in verification reports
   - Check service logs for specific errors
   - Verify environment variable configuration

5. **Test Dashboard Access**:
   ```bash
   # Open browser to http://localhost:3010
   # Login: admin/admin123
   # Verify dashboards display data
   ```

6. **Validate Customer Isolation**:
   ```bash
   python3 scripts/test-grafana-connectivity.py
   ```

### For System Updates

1. **Before Changes**: Run verification to establish baseline
2. **After Changes**: Re-run verification to confirm functionality
3. **Compare Results**: Address any newly introduced issues
4. **Update Documentation**: Record any configuration changes

### Continuous Monitoring

1. **Regular Verification**: Run verification scripts weekly
2. **Performance Monitoring**: Track dashboard load times
3. **Data Quality Checks**: Monitor data generation consistency
4. **Alert Validation**: Test alert rules periodically

## Conclusion

This verification guide provides a comprehensive framework for ensuring the Bhashini QoS monitoring system operates correctly with proper data flow, schema consistency, and multi-tenant isolation. The verification scripts and troubleshooting steps enable systematic diagnosis and resolution of issues at any stage of the data pipeline.

For additional support or questions, review the verification script outputs for detailed recommendations and specific resolution steps.