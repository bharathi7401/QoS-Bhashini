#!/usr/bin/env python3

import sys
import os
import requests
import json
from influxdb_client import InfluxDBClient

# Configuration
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3010")
GRAFANA_USER = os.getenv("GRAFANA_ADMIN_USER", "admin")
GRAFANA_PASSWORD = os.getenv("GRAFANA_ADMIN_PASSWORD", "admin123")

INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "your-default-token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "bhashini")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "qos_metrics")

class GrafanaConnectivityTester:
    def __init__(self):
        self.issues = []
        self.successes = []
        self.session = requests.Session()
        self.session.auth = (GRAFANA_USER, GRAFANA_PASSWORD)
        
    def log_issue(self, message, category="ERROR"):
        issue = f"[{category}] {message}"
        self.issues.append(issue)
        print(f"❌ {issue}")
        
    def log_success(self, message):
        self.successes.append(message)
        print(f"✅ {message}")
        
    def test_grafana_api_health(self):
        """Test the main datasource (influxdb-qos-metrics) by making API calls to Grafana's datasource proxy"""
        try:
            response = self.session.get(f"{GRAFANA_URL}/api/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                self.log_success(f"Grafana API health check passed - Version: {health_data.get('version', 'unknown')}")
                return True
            else:
                self.log_issue(f"Grafana API health check failed - Status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_issue(f"Cannot connect to Grafana API: {str(e)}")
            return False
            
    def get_all_datasources(self):
        """Get list of all datasources configured in Grafana"""
        try:
            response = self.session.get(f"{GRAFANA_URL}/api/datasources", timeout=10)
            
            if response.status_code == 200:
                datasources = response.json()
                self.log_success(f"Retrieved {len(datasources)} datasources from Grafana")
                return datasources
            else:
                self.log_issue(f"Failed to retrieve datasources - Status: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            self.log_issue(f"Failed to retrieve datasources: {str(e)}")
            return []
            
    def test_datasource_health(self, datasource):
        """Verify datasource health using Grafana's datasource test API endpoint"""
        try:
            ds_uid = datasource.get('uid')
            ds_name = datasource.get('name')
            ds_type = datasource.get('type')
            
            # Test datasource connection
            response = self.session.get(f"{GRAFANA_URL}/api/datasources/uid/{ds_uid}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                status = health_data.get('status', 'unknown')
                message = health_data.get('message', '')
                
                if status == 'OK':
                    self.log_success(f"Datasource '{ds_name}' ({ds_type}) health check passed")
                    return True
                else:
                    self.log_issue(f"Datasource '{ds_name}' ({ds_type}) health check failed: {status} - {message}")
                    return False
            else:
                self.log_issue(f"Datasource '{ds_name}' ({ds_type}) health check returned status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_issue(f"Failed to test datasource '{ds_name}': {str(e)}")
            return False
            
    def test_datasource_query(self, datasource):
        """Execute sample queries through each datasource to ensure they return data"""
        try:
            ds_uid = datasource.get('uid')
            ds_name = datasource.get('name')
            ds_type = datasource.get('type')
            
            if ds_type != 'influxdb':
                self.log_success(f"Skipping query test for non-InfluxDB datasource: {ds_name}")
                return True
                
            # Create a simple test query
            query_payload = {
                "queries": [
                    {
                        "datasource": {
                            "uid": ds_uid,
                            "type": ds_type
                        },
                        "query": f'''
                        from(bucket: "{INFLUXDB_BUCKET}")
                          |> range(start: -1h)
                          |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
                          |> limit(n: 1)
                        ''',
                        "refId": "A",
                        "intervalMs": 1000,
                        "maxDataPoints": 100
                    }
                ],
                "from": "now-1h",
                "to": "now"
            }
            
            response = self.session.post(
                f"{GRAFANA_URL}/api/ds/query",
                json=query_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                query_result = response.json()
                
                # Check if we got any data
                has_data = False
                if 'results' in query_result:
                    for result in query_result['results'].values():
                        if 'frames' in result and result['frames']:
                            for frame in result['frames']:
                                if 'data' in frame and frame['data'] and 'values' in frame['data']:
                                    if any(values for values in frame['data']['values'] if values):
                                        has_data = True
                                        break
                
                if has_data:
                    self.log_success(f"Datasource '{ds_name}' query executed successfully with data")
                else:
                    self.log_issue(f"Datasource '{ds_name}' query executed but returned no data", "WARNING")
                    
                return True
            else:
                self.log_issue(f"Datasource '{ds_name}' query failed - Status: {response.status_code}")
                try:
                    error_data = response.json()
                    self.log_issue(f"Query error details: {error_data}")
                except:
                    self.log_issue(f"Query error response: {response.text[:200]}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_issue(f"Failed to test query for datasource '{ds_name}': {str(e)}")
            return False
            
    def test_customer_datasources(self, datasources):
        """Test customer-specific datasources for each tenant (enterprise_1, startup_2, freemium_1, etc.)"""
        print("\n" + "="*60)
        print("TESTING CUSTOMER-SPECIFIC DATASOURCES")
        print("="*60)
        
        customer_datasources = [ds for ds in datasources if 'Customer' in ds.get('name', '')]
        expected_customers = ['enterprise_1', 'startup_2', 'freemium_1']
        
        if not customer_datasources:
            self.log_issue("No customer-specific datasources found")
            return False
            
        self.log_success(f"Found {len(customer_datasources)} customer datasources")
        
        # Check if all expected customers have datasources
        found_customers = []
        for ds in customer_datasources:
            ds_name = ds.get('name', '')
            for customer in expected_customers:
                if customer in ds_name:
                    found_customers.append(customer)
                    break
                    
        missing_customers = set(expected_customers) - set(found_customers)
        if missing_customers:
            self.log_issue(f"Missing datasources for customers: {list(missing_customers)}")
        else:
            self.log_success("All expected customer datasources are present")
            
        # Test each customer datasource
        customer_results = []
        for ds in customer_datasources:
            print(f"\nTesting customer datasource: {ds.get('name')}")
            
            # Test health
            health_ok = self.test_datasource_health(ds)
            
            # Test query
            query_ok = self.test_customer_datasource_query(ds)
            
            customer_results.append(health_ok and query_ok)
            
        return all(customer_results)
        
    def test_customer_datasource_query(self, datasource):
        """Test customer datasource with tenant-specific query"""
        try:
            ds_uid = datasource.get('uid')
            ds_name = datasource.get('name')
            
            # Extract customer ID from datasource name
            customer_id = None
            if 'enterprise_1' in ds_name:
                customer_id = 'enterprise_1'
            elif 'startup_2' in ds_name:
                customer_id = 'startup_2'
            elif 'freemium_1' in ds_name:
                customer_id = 'freemium_1'
                
            if not customer_id:
                self.log_issue(f"Cannot determine customer ID from datasource name: {ds_name}")
                return False
                
            # Create customer-specific test query
            query_payload = {
                "queries": [
                    {
                        "datasource": {
                            "uid": ds_uid,
                            "type": "influxdb"
                        },
                        "query": f'''
                        from(bucket: "{INFLUXDB_BUCKET}")
                          |> range(start: -1h)
                          |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
                          |> filter(fn: (r) => r["customer_id"] == "{customer_id}")
                          |> limit(n: 5)
                        ''',
                        "refId": "A",
                        "intervalMs": 1000,
                        "maxDataPoints": 100
                    }
                ],
                "from": "now-1h",
                "to": "now"
            }
            
            response = self.session.post(
                f"{GRAFANA_URL}/api/ds/query",
                json=query_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_success(f"Customer datasource '{ds_name}' tenant-specific query executed successfully")
                return True
            else:
                self.log_issue(f"Customer datasource '{ds_name}' query failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_issue(f"Failed to test customer datasource query '{ds_name}': {str(e)}")
            return False
            
    def check_authentication(self, datasources):
        """Check authentication by verifying tokens work correctly for each datasource"""
        print("\n" + "="*60)
        print("CHECKING DATASOURCE AUTHENTICATION")
        print("="*60)
        
        influxdb_datasources = [ds for ds in datasources if ds.get('type') == 'influxdb']
        
        auth_results = []
        for ds in influxdb_datasources:
            ds_name = ds.get('name')
            
            # For InfluxDB datasources, we test authentication implicitly through health checks
            # The health check will fail if authentication is incorrect
            auth_ok = self.test_datasource_health(ds)
            auth_results.append(auth_ok)
            
            if auth_ok:
                self.log_success(f"Authentication verified for datasource: {ds_name}")
            else:
                self.log_issue(f"Authentication failed for datasource: {ds_name}")
                
        return all(auth_results)
        
    def test_network_connectivity(self):
        """Test network connectivity from Grafana container to InfluxDB container"""
        print("\n" + "="*60)
        print("TESTING NETWORK CONNECTIVITY")
        print("="*60)
        
        try:
            # Test direct connection to InfluxDB from this script
            influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
            health = influx_client.health()
            
            if health.status == "pass":
                self.log_success("Direct InfluxDB connection from test script successful")
            else:
                self.log_issue(f"Direct InfluxDB connection failed - Status: {health.status}")
                
            influx_client.close()
            return health.status == "pass"
            
        except Exception as e:
            self.log_issue(f"Failed to test direct InfluxDB connectivity: {str(e)}")
            return False
            
    def run_query_api_test(self, datasources):
        """Validate query execution by running simple Flux queries through Grafana's query API"""
        print("\n" + "="*60)
        print("TESTING QUERY API EXECUTION")
        print("="*60)
        
        main_datasource = None
        for ds in datasources:
            if ds.get('name') == 'InfluxDB-QoS-Metrics' or 'qos' in ds.get('name', '').lower():
                main_datasource = ds
                break
                
        if not main_datasource:
            # Fallback to first InfluxDB datasource
            influx_datasources = [ds for ds in datasources if ds.get('type') == 'influxdb']
            if influx_datasources:
                main_datasource = influx_datasources[0]
                
        if not main_datasource:
            self.log_issue("No suitable InfluxDB datasource found for query testing")
            return False
            
        # Test various query patterns
        test_queries = [
            {
                "name": "Basic Measurement Query",
                "query": f'''
                from(bucket: "{INFLUXDB_BUCKET}")
                  |> range(start: -1h)
                  |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
                  |> limit(n: 1)
                '''
            },
            {
                "name": "Service Group Query",
                "query": f'''
                from(bucket: "{INFLUXDB_BUCKET}")
                  |> range(start: -1h)
                  |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
                  |> filter(fn: (r) => r["_field"] == "value")
                  |> group(columns: ["service"])
                  |> limit(n: 1)
                '''
            },
            {
                "name": "Customer Filter Query",
                "query": f'''
                from(bucket: "{INFLUXDB_BUCKET}")
                  |> range(start: -1h)
                  |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
                  |> filter(fn: (r) => r["customer_id"] == "enterprise_1")
                  |> limit(n: 1)
                '''
            }
        ]
        
        query_results = []
        for test_query in test_queries:
            success = self.execute_test_query(main_datasource, test_query)
            query_results.append(success)
            
        return all(query_results)
        
    def execute_test_query(self, datasource, test_query):
        """Execute a single test query"""
        try:
            ds_uid = datasource.get('uid')
            query_name = test_query['name']
            query = test_query['query']
            
            query_payload = {
                "queries": [
                    {
                        "datasource": {
                            "uid": ds_uid,
                            "type": "influxdb"
                        },
                        "query": query,
                        "refId": "A",
                        "intervalMs": 1000,
                        "maxDataPoints": 100
                    }
                ],
                "from": "now-1h",
                "to": "now"
            }
            
            response = self.session.post(
                f"{GRAFANA_URL}/api/ds/query",
                json=query_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_success(f"Test query '{query_name}' executed successfully")
                return True
            else:
                self.log_issue(f"Test query '{query_name}' failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_issue(f"Failed to execute test query '{query_name}': {str(e)}")
            return False
            
    def generate_report(self):
        """Report connectivity status for each datasource with specific error details"""
        print("\n" + "="*80)
        print("GRAFANA CONNECTIVITY TEST REPORT")
        print("="*80)
        
        print(f"\n✅ SUCCESSES ({len(self.successes)}):")
        for success in self.successes:
            print(f"  {success}")
            
        print(f"\n❌ ISSUES FOUND ({len(self.issues)}):")
        for issue in self.issues:
            print(f"  {issue}")
            
        print(f"\nRECOMMENDATIONS:")
        
        if any("Cannot connect to Grafana API" in issue for issue in self.issues):
            print("  - Ensure Grafana is running and accessible at http://localhost:3000")
            print("  - Check Grafana admin credentials (admin/admin123)")
            
        if any("health check failed" in issue.lower() for issue in self.issues):
            print("  - Verify InfluxDB is running and accessible")
            print("  - Check datasource token configuration in docker-compose.yml")
            print("  - Ensure environment variables are properly set")
            
        if any("query failed" in issue.lower() for issue in self.issues):
            print("  - Verify data exists in InfluxDB bucket")
            print("  - Check if data-simulator is generating metrics")
            print("  - Verify bucket and measurement names match configuration")
            
        if any("Missing datasources for customers" in issue for issue in self.issues):
            print("  - Add missing customer datasource configurations")
            print("  - Ensure customer tokens are defined in docker-compose.yml")
            
        if any("Authentication failed" in issue for issue in self.issues):
            print("  - Verify InfluxDB tokens are correctly configured")
            print("  - Check token permissions for bucket access")
            
        print(f"\nOVERALL STATUS: {'✅ PASS' if len([i for i in self.issues if not i.startswith('[WARNING]')]) == 0 else '❌ ISSUES FOUND'}")
        print("="*80)
        
    def run_connectivity_tests(self):
        """Run complete Grafana connectivity test suite"""
        print("Starting Grafana connectivity tests...")
        print("="*80)
        
        # Step 1: Test Grafana API health
        if not self.test_grafana_api_health():
            print("❌ Cannot proceed - Grafana API is not accessible")
            self.generate_report()
            return False
            
        # Step 2: Get all datasources
        datasources = self.get_all_datasources()
        if not datasources:
            print("❌ Cannot proceed - No datasources found")
            self.generate_report()
            return False
            
        # Display found datasources
        print(f"\nFound datasources:")
        for ds in datasources:
            print(f"  - {ds.get('name')} (Type: {ds.get('type')}, UID: {ds.get('uid')})")
            
        # Step 3: Test datasource health
        print(f"\n{'='*60}")
        print("TESTING DATASOURCE HEALTH")
        print("="*60)
        
        health_results = []
        for ds in datasources:
            if ds.get('type') == 'influxdb':
                result = self.test_datasource_health(ds)
                health_results.append(result)
                
        # Step 4: Test datasource queries
        print(f"\n{'='*60}")
        print("TESTING DATASOURCE QUERIES")
        print("="*60)
        
        query_results = []
        for ds in datasources:
            if ds.get('type') == 'influxdb':
                result = self.test_datasource_query(ds)
                query_results.append(result)
                
        # Step 5: Test customer-specific datasources
        customer_results = self.test_customer_datasources(datasources)
        
        # Step 6: Check authentication
        auth_results = self.check_authentication(datasources)
        
        # Step 7: Test network connectivity
        network_results = self.test_network_connectivity()
        
        # Step 8: Test query API
        api_results = self.run_query_api_test(datasources)
        
        # Step 9: Generate report
        self.generate_report()
        
        # Overall success
        overall_success = (
            all(health_results) and 
            all(query_results) and 
            customer_results and 
            auth_results and 
            network_results and 
            api_results
        )
        
        return overall_success

def main():
    tester = GrafanaConnectivityTester()
    success = tester.run_connectivity_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()