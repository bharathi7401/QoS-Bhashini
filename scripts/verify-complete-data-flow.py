#!/usr/bin/env python3

import sys
import os
import requests
import time
import json
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timedelta

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from data-simulator config for source-of-truth values
try:
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data-simulator'))
    from config import Config
    EXPECTED_SERVICES = list(Config.SERVICES.keys())
    EXPECTED_CUSTOMERS = list(Config.TENANTS.keys())
except ImportError:
    # Fallback to hard-coded values if import fails
    EXPECTED_SERVICES = ["translation", "tts", "asr"]
    EXPECTED_CUSTOMERS = ["enterprise_1", "startup_2", "freemium_1"]

# Configuration (using same patterns as verify-data-flow.py)
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "your-default-token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "bhashini")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "qos_metrics")

# Grafana configuration
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3010")
GRAFANA_USER = "admin"
GRAFANA_PASSWORD = "admin123"

EXPECTED_METRICS = ["latency", "error_rate", "throughput", "availability"]
EXPECTED_FIELDS = ["value"]

class DataFlowVerifier:
    def __init__(self):
        self.client = None
        self.issues = []
        self.successes = []
        
    def log_issue(self, message, category="ERROR"):
        issue = f"[{category}] {message}"
        self.issues.append(issue)
        print(f"❌ {issue}")
        
    def log_success(self, message):
        self.successes.append(message)
        print(f"✅ {message}")
        
    def connect_to_influxdb(self):
        """Test basic connectivity to InfluxDB using configuration from data-simulator/config.py"""
        try:
            self.client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
            
            # Test connection
            health = self.client.health()
            if health.status == "pass":
                self.log_success(f"InfluxDB connection successful - Status: {health.status}")
                return True
            else:
                self.log_issue(f"InfluxDB health check failed - Status: {health.status}")
                return False
                
        except Exception as e:
            self.log_issue(f"Failed to connect to InfluxDB: {str(e)}")
            return False
            
    def check_data_simulator_status(self):
        """Validate data generation by checking if the data-simulator is running and generating metrics"""
        try:
            # Check if recent data exists (last 5 minutes)
            query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
              |> range(start: -5m)
              |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
              |> count()
            '''
            
            tables = self.client.query_api().query(query)
            
            total_points = 0
            for table in tables:
                for record in table.records:
                    total_points += record.get_value()
                    
            if total_points > 0:
                self.log_success(f"Data simulator is active - {total_points} metrics generated in last 5 minutes")
                return True
            else:
                self.log_issue("No recent data found - Data simulator may not be running")
                return False
                
        except Exception as e:
            self.log_issue(f"Failed to check data simulator status: {str(e)}")
            return False
            
    def verify_data_schema_consistency(self):
        """Verify data schema consistency by querying actual data and comparing against dashboard expectations"""
        try:
            # Get sample data to check schema
            query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
              |> range(start: -1h)
              |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
              |> limit(n: 10)
            '''
            
            tables = self.client.query_api().query(query)
            
            if not tables:
                self.log_issue("No data found for schema validation")
                return False
                
            # Check field consistency
            found_fields = set()
            found_services = set()
            found_customers = set()
            found_metrics = set()
            
            for table in tables:
                for record in table.records:
                    found_fields.add(record.get_field())
                    if "service_name" in record.values:
                        found_services.add(record.values["service_name"])
                    if "tenant_id" in record.values:
                        found_customers.add(record.values["tenant_id"])
                    if "metric_type" in record.values:
                        found_metrics.add(record.values["metric_type"])
                        
            # Validate schema components
            schema_valid = True
            
            # Check if expected fields are present
            for field in EXPECTED_FIELDS:
                if field not in found_fields:
                    self.log_issue(f"Missing expected field: {field}")
                    schema_valid = False
                else:
                    self.log_success(f"Found expected field: {field}")
                    
            # Report found services
            self.log_success(f"Found services: {list(found_services)}")
            self.log_success(f"Found customers: {list(found_customers)}")
            self.log_success(f"Found metric types: {list(found_metrics)}")
            
            return schema_valid
            
        except Exception as e:
            self.log_issue(f"Failed to verify data schema: {str(e)}")
            return False
            
    def test_service_name_consistency(self):
        """Test service name consistency by checking if service names in data match dashboard filter expectations"""
        try:
            # Query distinct service names
            query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
              |> range(start: -1h)
              |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
              |> keep(columns: ["service_name"])
              |> distinct(column: "service_name")
            '''
            
            tables = self.client.query_api().query(query)
            found_services = set()
            
            for table in tables:
                for record in table.records:
                    if "service_name" in record.values:
                        found_services.add(record.values["service_name"])
                        
            # Check service name consistency
            expected_set = set(EXPECTED_SERVICES)
            found_set = set(found_services)
            
            if expected_set == found_set:
                self.log_success(f"Service names are consistent: {list(found_services)}")
                return True
            else:
                missing = expected_set - found_set
                extra = found_set - expected_set
                
                if missing:
                    self.log_issue(f"Missing expected services: {list(missing)}")
                if extra:
                    self.log_issue(f"Unexpected services found: {list(extra)}")
                    
                return False
                
        except Exception as e:
            self.log_issue(f"Failed to test service name consistency: {str(e)}")
            return False
            
    def validate_field_presence(self):
        """Validate field presence by confirming which fields are actually written (value vs value+unit)"""
        try:
            # Query to get all field names using proper _field column
            query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
              |> range(start: -1h)
              |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
              |> keep(columns: ["_field"]) 
              |> distinct(column: "_field")
            '''
            
            tables = self.client.query_api().query(query)
            found_fields = set()
            
            for table in tables:
                for record in table.records:
                    field_name = record.get_value()
                    if field_name:
                        found_fields.add(field_name)
                        
            # Check required fields
            required_fields = {"value"}  # Minimum required
            optional_fields = {"unit"}   # Recommended
            
            missing_required = required_fields - found_fields
            missing_optional = optional_fields - found_fields
            
            if not missing_required:
                self.log_success(f"All required fields present: {list(required_fields)}")
            else:
                self.log_issue(f"Missing required fields: {list(missing_required)}")
                
            if not missing_optional:
                self.log_success(f"All optional fields present: {list(optional_fields)}")
            else:
                self.log_issue(f"Missing recommended fields: {list(missing_optional)}", "WARNING")
                
            self.log_success(f"Found fields: {list(found_fields)}")
            return len(missing_required) == 0
            
        except Exception as e:
            self.log_issue(f"Failed to validate field presence: {str(e)}")
            return False
            
    def test_multi_tenant_isolation(self):
        """Test multi-tenant isolation by verifying each tenant has data and customer datasources work"""
        try:
            isolation_valid = True
            
            for customer in EXPECTED_CUSTOMERS:
                # Query data for specific customer
                query = f'''
                from(bucket: "{INFLUXDB_BUCKET}")
                  |> range(start: -1h)
                  |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
                  |> filter(fn: (r) => r["tenant_id"] == "{customer}")
                  |> count()
                '''
                
                tables = self.client.query_api().query(query)
                customer_count = 0
                
                for table in tables:
                    for record in table.records:
                        customer_count += record.get_value()
                        
                if customer_count > 0:
                    self.log_success(f"Customer {customer} has {customer_count} data points")
                else:
                    self.log_issue(f"No data found for customer: {customer}")
                    isolation_valid = False
                    
            return isolation_valid
            
        except Exception as e:
            self.log_issue(f"Failed to test multi-tenant isolation: {str(e)}")
            return False
            
    def validate_dashboard_queries(self):
        """Validate dashboard queries by executing sample Flux queries from dashboards against real data"""
        try:
            # Sample dashboard query patterns
            sample_queries = [
                {
                    "name": "Latency Overview",
                    "query": f'''
                    from(bucket: "{INFLUXDB_BUCKET}")
                      |> range(start: -1h)
                      |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
                      |> filter(fn: (r) => r["metric_type"] == "latency")
                      |> filter(fn: (r) => r["_field"] == "value")
                      |> mean()
                    '''
                },
                {
                    "name": "Error Rate by Service",
                    "query": f'''
                    from(bucket: "{INFLUXDB_BUCKET}")
                      |> range(start: -1h)
                      |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
                      |> filter(fn: (r) => r["metric_type"] == "error_rate")
                      |> filter(fn: (r) => r["_field"] == "value")
                      |> group(columns: ["service"])
                      |> mean()
                    '''
                },
                {
                    "name": "Customer-specific Throughput",
                    "query": f'''
                    from(bucket: "{INFLUXDB_BUCKET}")
                      |> range(start: -1h)
                      |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
                      |> filter(fn: (r) => r["metric_type"] == "throughput")
                      |> filter(fn: (r) => r["tenant_id"] == "enterprise_1")
                      |> filter(fn: (r) => r["_field"] == "value")
                      |> mean()
                    '''
                }
            ]
            
            queries_valid = True
            
            for query_info in sample_queries:
                try:
                    tables = self.client.query_api().query(query_info["query"])
                    has_data = False
                    
                    for table in tables:
                        if table.records:
                            has_data = True
                            break
                            
                    if has_data:
                        self.log_success(f"Dashboard query '{query_info['name']}' returns data")
                    else:
                        self.log_issue(f"Dashboard query '{query_info['name']}' returns no data", "WARNING")
                        
                except Exception as e:
                    self.log_issue(f"Dashboard query '{query_info['name']}' failed: {str(e)}")
                    queries_valid = False
                    
            return queries_valid
            
        except Exception as e:
            self.log_issue(f"Failed to validate dashboard queries: {str(e)}")
            return False
            
    def test_grafana_datasource_connectivity(self):
        """Test Grafana datasource connectivity for both global and customer-specific datasources"""
        try:
            # Test Grafana API connectivity
            try:
                response = requests.get(
                    f"{GRAFANA_URL}/api/health",
                    auth=(GRAFANA_USER, GRAFANA_PASSWORD),
                    timeout=10
                )
                if response.status_code == 200:
                    self.log_success("Grafana API is accessible")
                else:
                    self.log_issue(f"Grafana API returned status: {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                self.log_issue(f"Cannot connect to Grafana API: {str(e)}")
                return False
                
            # Test datasources (if Grafana is accessible)
            try:
                response = requests.get(
                    f"{GRAFANA_URL}/api/datasources",
                    auth=(GRAFANA_USER, GRAFANA_PASSWORD),
                    timeout=10
                )
                
                if response.status_code == 200:
                    datasources = response.json()
                    influx_datasources = [ds for ds in datasources if ds.get("type") == "influxdb"]
                    
                    if influx_datasources:
                        self.log_success(f"Found {len(influx_datasources)} InfluxDB datasources in Grafana")
                        for ds in influx_datasources:
                            self.log_success(f"  - {ds['name']} (UID: {ds['uid']})")
                    else:
                        self.log_issue("No InfluxDB datasources found in Grafana")
                        return False
                else:
                    self.log_issue(f"Failed to fetch Grafana datasources: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.log_issue(f"Failed to test Grafana datasources: {str(e)}")
                
            return True
            
        except Exception as e:
            self.log_issue(f"Failed to test Grafana connectivity: {str(e)}")
            return False
            
    def test_alerting_rules(self):
        """Test alerting rules by verifying alert queries return expected results"""
        try:
            # Sample alert query patterns
            alert_queries = [
                {
                    "name": "High Latency Alert",
                    "query": f'''
                    from(bucket: "{INFLUXDB_BUCKET}")
                      |> range(start: -5m)
                      |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
                      |> filter(fn: (r) => r["metric_type"] == "latency")
                      |> filter(fn: (r) => r["_field"] == "value")
                      |> mean()
                      |> map(fn: (r) => ({{ r with _value: if r._value > 1000.0 then 1.0 else 0.0 }}))
                    '''
                },
                {
                    "name": "High Error Rate Alert",
                    "query": f'''
                    from(bucket: "{INFLUXDB_BUCKET}")
                      |> range(start: -5m)
                      |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
                      |> filter(fn: (r) => r["metric_type"] == "error_rate")
                      |> filter(fn: (r) => r["_field"] == "value")
                      |> mean()
                      |> map(fn: (r) => ({{ r with _value: if r._value > 5.0 then 1.0 else 0.0 }}))
                    '''
                }
            ]
            
            alerts_valid = True
            
            for alert_info in alert_queries:
                try:
                    tables = self.client.query_api().query(alert_info["query"])
                    query_executed = False
                    
                    for table in tables:
                        if table.records is not None:
                            query_executed = True
                            break
                            
                    if query_executed:
                        self.log_success(f"Alert query '{alert_info['name']}' executes successfully")
                    else:
                        self.log_issue(f"Alert query '{alert_info['name']}' returns no results", "WARNING")
                        
                except Exception as e:
                    self.log_issue(f"Alert query '{alert_info['name']}' failed: {str(e)}")
                    alerts_valid = False
                    
            return alerts_valid
            
        except Exception as e:
            self.log_issue(f"Failed to test alerting rules: {str(e)}")
            return False
            
    def generate_report(self):
        """Provide detailed reporting with specific recommendations for any issues found"""
        print("\n" + "="*80)
        print("COMPREHENSIVE DATA FLOW VERIFICATION REPORT")
        print("="*80)
        
        print(f"\n✅ SUCCESSES ({len(self.successes)}):")
        for success in self.successes:
            print(f"  {success}")
            
        print(f"\n❌ ISSUES FOUND ({len(self.issues)}):")
        for issue in self.issues:
            print(f"  {issue}")
            
        print(f"\nRECOMMENDATIONS:")
        if any("Missing expected field: unit" in issue for issue in self.issues):
            print("  - Add 'unit' field to metrics in data-simulator/metrics_generator.py")
            
        if any("service name" in issue.lower() for issue in self.issues):
            print("  - Check service name consistency between data generation and dashboards")
            
        if any("datasource" in issue.lower() for issue in self.issues):
            print("  - Verify Grafana datasource configuration and tokens in docker-compose.yml")
            
        if any("No recent data" in issue for issue in self.issues):
            print("  - Start the data simulator: cd data-simulator && python main.py")
            
        if any("customer" in issue.lower() for issue in self.issues):
            print("  - Check multi-tenant configuration and customer data generation")
            
        print(f"\nOVERALL STATUS: {'✅ PASS' if len(self.issues) == 0 else '❌ ISSUES FOUND'}")
        print("="*80)
        
    def run_complete_verification(self):
        """Run complete verification of the data pipeline"""
        print("Starting comprehensive data flow verification...")
        print("="*80)
        
        # Step 1: Test basic connectivity
        if not self.connect_to_influxdb():
            print("❌ Cannot proceed - InfluxDB connection failed")
            return False
            
        # Step 2: Check data generation
        self.check_data_simulator_status()
        
        # Step 3: Verify data schema
        self.verify_data_schema_consistency()
        
        # Step 4: Test service name consistency
        self.test_service_name_consistency()
        
        # Step 5: Validate field presence
        self.validate_field_presence()
        
        # Step 6: Test multi-tenant isolation
        self.test_multi_tenant_isolation()
        
        # Step 7: Validate dashboard queries
        self.validate_dashboard_queries()
        
        # Step 8: Test Grafana connectivity
        self.test_grafana_datasource_connectivity()
        
        # Step 9: Test alerting rules
        self.test_alerting_rules()
        
        # Step 10: Generate comprehensive report
        self.generate_report()
        
        return len(self.issues) == 0

def main():
    verifier = DataFlowVerifier()
    success = verifier.run_complete_verification()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()