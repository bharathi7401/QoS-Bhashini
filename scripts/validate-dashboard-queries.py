#!/usr/bin/env python3

import sys
import os
import json
import re
from influxdb_client import InfluxDBClient
import glob
import yaml

# Configuration (using same patterns as verify-data-flow.py)
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "your-default-token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "bhashini")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "qos_metrics")
EXPECTED_MEASUREMENT = "qos_metrics"  # Standard measurement name

class DashboardQueryValidator:
    def __init__(self):
        self.client = None
        self.issues = []
        self.successes = []
        self.dashboard_files = []
        self.alert_files = []
        
    def log_issue(self, message, category="ERROR"):
        issue = f"[{category}] {message}"
        self.issues.append(issue)
        print(f"❌ {issue}")
        
    def log_success(self, message):
        self.successes.append(message)
        print(f"✅ {message}")
        
    def connect_to_influxdb(self):
        """Connect to InfluxDB for query testing"""
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
            
    def discover_dashboard_files(self):
        """Extract queries from dashboard JSON files in grafana/provisioning/dashboards/ directories"""
        try:
            # Find all dashboard JSON files
            dashboard_pattern = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "grafana/provisioning/dashboards/**/*.json"
            )
            
            self.dashboard_files = glob.glob(dashboard_pattern, recursive=True)
            
            if self.dashboard_files:
                self.log_success(f"Found {len(self.dashboard_files)} dashboard files")
                for file in self.dashboard_files:
                    rel_path = os.path.relpath(file, os.path.dirname(os.path.dirname(__file__)))
                    self.log_success(f"  - {rel_path}")
            else:
                self.log_issue("No dashboard files found in grafana/provisioning/dashboards/")
                
            return len(self.dashboard_files) > 0
            
        except Exception as e:
            self.log_issue(f"Failed to discover dashboard files: {str(e)}")
            return False
            
    def discover_alert_files(self):
        """Find alerting configuration files"""
        try:
            # Find alert files
            alert_pattern = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "grafana/provisioning/alerting/**/*.yml"
            )
            
            self.alert_files = glob.glob(alert_pattern, recursive=True)
            
            if self.alert_files:
                self.log_success(f"Found {len(self.alert_files)} alert configuration files")
                for file in self.alert_files:
                    rel_path = os.path.relpath(file, os.path.dirname(os.path.dirname(__file__)))
                    self.log_success(f"  - {rel_path}")
            else:
                self.log_issue("No alert files found in grafana/provisioning/alerting/", "WARNING")
                
            return True
            
        except Exception as e:
            self.log_issue(f"Failed to discover alert files: {str(e)}")
            return False
            
    def extract_queries_from_dashboard(self, dashboard_file):
        """Extract Flux queries from a dashboard JSON file"""
        queries = []
        
        try:
            with open(dashboard_file, 'r') as f:
                dashboard = json.load(f)
                
            dashboard_title = dashboard.get('title', os.path.basename(dashboard_file))
            
            # Navigate through panels
            panels = dashboard.get('panels', [])
            
            for panel in panels:
                panel_title = panel.get('title', 'Untitled Panel')
                
                # Check for targets (queries)
                targets = panel.get('targets', [])
                
                for i, target in enumerate(targets):
                    # Look for Flux query
                    query = target.get('query', '')
                    
                    if query and 'from(bucket:' in query:
                        queries.append({
                            'dashboard': dashboard_title,
                            'panel': panel_title,
                            'target_index': i,
                            'query': query,
                            'datasource_uid': target.get('datasource', {}).get('uid', 'unknown')
                        })
                        
        except Exception as e:
            self.log_issue(f"Failed to parse dashboard {dashboard_file}: {str(e)}")
            
        return queries
        
    def extract_queries_from_alerts(self, alert_file):
        """Extract queries from alerting configuration YAML files"""
        queries = []
        
        try:
            with open(alert_file, 'r') as f:
                alert_config = yaml.safe_load(f)
                
            if not alert_config:
                return queries
                
            # Navigate through alert groups
            groups = alert_config.get('groups', [])
            
            for group in groups:
                group_name = group.get('name', 'Unknown Group')
                rules = group.get('rules', [])
                
                for rule in rules:
                    rule_name = rule.get('alert', 'Unknown Rule')
                    expr = rule.get('expr', '')
                    
                    if expr and ('from(bucket:' in expr or 'qos_metrics' in expr):
                        queries.append({
                            'alert_file': os.path.basename(alert_file),
                            'group': group_name,
                            'rule': rule_name,
                            'query': expr
                        })
                        
        except Exception as e:
            self.log_issue(f"Failed to parse alert file {alert_file}: {str(e)}")
            
        return queries
        
    def validate_query(self, query_info, query_type="dashboard"):
        """Test each query against InfluxDB using the same connection configuration"""
        try:
            query = query_info['query']
            
            # Clean up the query - remove any Grafana variables and replace with reasonable defaults
            cleaned_query = self.clean_grafana_query(query)
            
            # Execute the query
            tables = self.client.query_api().query(cleaned_query)
            
            # Check if we got any results
            has_data = False
            record_count = 0
            
            for table in tables:
                if table.records:
                    has_data = True
                    record_count += len(table.records)
                    
            if query_type == "dashboard":
                context = f"Dashboard '{query_info['dashboard']}' - Panel '{query_info['panel']}'"
            else:
                context = f"Alert '{query_info['group']}' - Rule '{query_info['rule']}'"
                
            if has_data:
                self.log_success(f"{context}: Query executed successfully ({record_count} records)")
                return True
            else:
                self.log_issue(f"{context}: Query executed but returned no data", "WARNING")
                return True  # Query syntax is valid even if no data
                
        except Exception as e:
            error_msg = str(e)
            if query_type == "dashboard":
                context = f"Dashboard '{query_info['dashboard']}' - Panel '{query_info['panel']}'"
            else:
                context = f"Alert '{query_info['group']}' - Rule '{query_info['rule']}'"
                
            self.log_issue(f"{context}: Query failed - {error_msg}")
            return False
            
    def clean_grafana_query(self, query):
        """Clean up Grafana-specific variables and syntax in queries"""
        # Replace common Grafana variables with defaults
        # Note: These substitutions are for validation context only
        replacements = {
            r'\$__interval': '1m',
            r'\$__timeFilter\([^)]+\)': 'range(start: -1h)',
            r'\${([^}]+)}': r'"\1"',  # Replace ${variable} with "variable"
            r'\$([a-zA-Z_][a-zA-Z0-9_]*)': r'"\1"',  # Replace $variable with "variable"
            r'range\(start: -\$__range\)': 'range(start: -1h)',
            r'range\(start: \$__timeFrom, stop: \$__timeTo\)': 'range(start: -1h)',
            # Normalize v.timeRange variables for validation
            r'range\(start: v\.timeRangeStart, stop: v\.timeRangeStop\)': 'range(start: -1h)',
            r'aggregateWindow\(every: v\.windowPeriod': 'aggregateWindow(every: 1m',
            # Normalize contains functions for validation context
            r'contains\(value: "\$__all", set: v\.service_filter\)': 'true',
            r'contains\(value: r\["service"\], set: v\.service_filter\)': 'true',
        }
        
        cleaned_query = query
        for pattern, replacement in replacements.items():
            cleaned_query = re.sub(pattern, replacement, cleaned_query)
            
        return cleaned_query
        
    def check_common_issues(self, queries):
        """Check for common issues across all queries"""
        print("\n" + "="*60)
        print("CHECKING FOR COMMON QUERY ISSUES")
        print("="*60)
        
        # Check for service name case mismatches
        service_cases = set()
        bucket_names = set()
        measurement_names = set()
        field_references = set()
        
        # Track schema errors (deprecated field usage)
        schema_errors = []
        
        for query_info in queries:
            query = query_info['query']
            
            # Check for deprecated tenant_id usage (should be customer_id)
            if 'tenant_id' in query:
                context = f"Dashboard '{query_info.get('dashboard', 'Unknown')}' - Panel '{query_info.get('panel', 'Unknown')}'"
                schema_errors.append(f"MAJOR: {context} uses deprecated 'tenant_id' - should be 'customer_id'")
                
            # Check for deprecated service_name usage (should be service)
            if 'service_name' in query:
                context = f"Dashboard '{query_info.get('dashboard', 'Unknown')}' - Panel '{query_info.get('panel', 'Unknown')}'"
                schema_errors.append(f"MAJOR: {context} uses deprecated 'service_name' - should be 'service'")
                
            # Validate service values are lowercase
            titlecase_services = re.findall(r'r\["service"\] == "([A-Z][^"]+)"', query)
            if titlecase_services:
                context = f"Dashboard '{query_info.get('dashboard', 'Unknown')}' - Panel '{query_info.get('panel', 'Unknown')}'"
                schema_errors.append(f"MAJOR: {context} uses TitleCase service names {titlecase_services} - should be lowercase")
            
            # Extract service name patterns
            service_matches = re.findall(r'r\["service"\] == "([^"]+)"', query)
            service_cases.update(service_matches)
            
            # Extract bucket names
            bucket_matches = re.findall(r'from\(bucket: "([^"]+)"\)', query)
            bucket_names.update(bucket_matches)
            
            # Extract measurement names
            measurement_matches = re.findall(r'r\["_measurement"\] == "([^"]+)"', query)
            measurement_names.update(measurement_matches)
            
            # Extract field references
            field_matches = re.findall(r'r\["_field"\] == "([^"]+)"', query)
            field_references.update(field_matches)
            
        # Report findings
        self.log_success(f"Found service names in queries: {list(service_cases)}")
        self.log_success(f"Found bucket names: {list(bucket_names)}")
        self.log_success(f"Found measurement names: {list(measurement_names)}")
        self.log_success(f"Found field references: {list(field_references)}")
        
        # Check for potential issues
        expected_services = {"translation", "tts", "asr"}
        expected_bucket = INFLUXDB_BUCKET  # Use environment-backed constant
        expected_measurement = EXPECTED_MEASUREMENT  # Use defined constant
        expected_fields = {"value", "unit"}
        
        if service_cases and not service_cases.issubset(expected_services):
            unexpected = service_cases - expected_services
            self.log_issue(f"Unexpected service names in queries: {list(unexpected)}")
            
        if bucket_names and expected_bucket not in bucket_names:
            self.log_issue(f"Expected bucket '{expected_bucket}' not found in queries")
            
        if measurement_names and expected_measurement not in measurement_names:
            self.log_issue(f"Expected measurement '{expected_measurement}' not found in queries")
            
        if not field_references.intersection(expected_fields):
            self.log_issue("No expected fields (value, unit) found in queries", "WARNING")
            
        # Report schema errors with high priority
        if schema_errors:
            self.log_issue(f"Found {len(schema_errors)} schema validation errors:", "MAJOR")
            for error in schema_errors:
                self.log_issue(error, "MAJOR")
                
        # Suggest automatic replacements
        if any('tenant_id' in error for error in schema_errors):
            self.log_issue("RECOMMENDATION: Replace all 'tenant_id' references with 'customer_id'", "MAJOR")
        if any('service_name' in error for error in schema_errors):
            self.log_issue("RECOMMENDATION: Replace all 'service_name' references with 'service'", "MAJOR")
        if any('TitleCase' in error for error in schema_errors):
            self.log_issue("RECOMMENDATION: Use lowercase service names: translation|tts|asr", "MAJOR")
            
    def validate_customer_specific_queries(self, queries):
        """Test customer-specific dashboards by testing queries that reference customer datasource UIDs"""
        print("\n" + "="*60)
        print("VALIDATING CUSTOMER-SPECIFIC QUERIES")
        print("="*60)
        
        customer_queries = []
        
        for query_info in queries:
            # Check if this query references a customer datasource UID
            datasource_uid = query_info.get('datasource_uid', '')
            
            if 'Customer' in datasource_uid or 'customer' in datasource_uid:
                customer_queries.append(query_info)
                
        if customer_queries:
            self.log_success(f"Found {len(customer_queries)} customer-specific queries")
            
            for query_info in customer_queries:
                # For customer queries, we need to check if they have proper tenant filtering
                query = query_info['query']
                
                # Check for customer_id filtering
                if 'customer_id' in query or 'tenant_id' in query:
                    self.log_success(f"Customer query has proper tenant filtering: {query_info['panel']}")
                else:
                    self.log_issue(f"Customer query missing tenant filtering: {query_info['panel']}", "WARNING")
        else:
            self.log_issue("No customer-specific queries found", "WARNING")
            
    def validate_template_variable_queries(self, queries):
        """Test template variable queries to ensure dropdown filters work correctly"""
        print("\n" + "="*60)
        print("VALIDATING TEMPLATE VARIABLE QUERIES")
        print("="*60)
        
        # Common template variable patterns
        template_patterns = [
            r'distinct\(column: "service"\)',
            r'distinct\(column: "customer_id"\)',
            r'distinct\(column: "metric_type"\)',
            r'distinct\(column: "sla_tier"\)'
        ]
        
        template_queries_found = []
        
        for query_info in queries:
            query = query_info['query']
            
            for pattern in template_patterns:
                if re.search(pattern, query):
                    template_queries_found.append({
                        'pattern': pattern,
                        'query_info': query_info
                    })
                    
        if template_queries_found:
            self.log_success(f"Found {len(template_queries_found)} template variable queries")
            
            # Test each template query
            for template_query in template_queries_found:
                try:
                    cleaned_query = self.clean_grafana_query(template_query['query_info']['query'])
                    tables = self.client.query_api().query(cleaned_query)
                    
                    values = []
                    for table in tables:
                        for record in table.records:
                            values.append(record.get_value())
                            
                    if values:
                        self.log_success(f"Template query returns {len(values)} values: {template_query['pattern']}")
                    else:
                        self.log_issue(f"Template query returns no values: {template_query['pattern']}", "WARNING")
                        
                except Exception as e:
                    self.log_issue(f"Template query failed: {template_query['pattern']} - {str(e)}")
        else:
            self.log_issue("No template variable queries found", "WARNING")
            
    def generate_report(self):
        """Report query execution results with specific error messages and suggested fixes"""
        print("\n" + "="*80)
        print("DASHBOARD QUERY VALIDATION REPORT")
        print("="*80)
        
        print(f"\n✅ SUCCESSES ({len(self.successes)}):")
        for success in self.successes:
            print(f"  {success}")
            
        print(f"\n❌ ISSUES FOUND ({len(self.issues)}):")
        for issue in self.issues:
            print(f"  {issue}")
            
        print(f"\nRECOMMENDATIONS:")
        
        if any("service name" in issue.lower() for issue in self.issues):
            print("  - Check service name consistency between dashboards and data generation")
            print("  - Ensure service names in queries match those in data-simulator/config.py")
            
        if any("bucket" in issue.lower() for issue in self.issues):
            print("  - Verify bucket names in dashboard queries match InfluxDB configuration")
            
        if any("field" in issue.lower() for issue in self.issues):
            print("  - Update dashboard queries to reference correct field names (value, unit)")
            
        if any("customer" in issue.lower() for issue in self.issues):
            print("  - Review customer-specific dashboard configurations")
            print("  - Ensure proper tenant filtering in customer queries")
            
        if any("template" in issue.lower() for issue in self.issues):
            print("  - Check template variable queries for proper distinct value selection")
            
        if any("Query failed" in issue for issue in self.issues):
            print("  - Review query syntax for Flux compatibility")
            print("  - Check for missing measurements, tags, or fields in data")
            
        print(f"\nOVERALL STATUS: {'✅ PASS' if len([i for i in self.issues if not i.startswith('[WARNING]')]) == 0 else '❌ ISSUES FOUND'}")
        print("="*80)
        
    def run_validation(self):
        """Run complete dashboard query validation"""
        print("Starting dashboard query validation...")
        print("="*80)
        
        # Step 1: Connect to InfluxDB
        if not self.connect_to_influxdb():
            print("❌ Cannot proceed - InfluxDB connection failed")
            return False
            
        # Step 2: Discover dashboard files
        if not self.discover_dashboard_files():
            print("❌ No dashboard files found")
            return False
            
        # Step 3: Discover alert files
        self.discover_alert_files()
        
        # Step 4: Extract and validate queries from dashboards
        all_queries = []
        
        for dashboard_file in self.dashboard_files:
            queries = self.extract_queries_from_dashboard(dashboard_file)
            all_queries.extend(queries)
            
            self.log_success(f"Extracted {len(queries)} queries from {os.path.basename(dashboard_file)}")
            
        # Step 5: Extract and validate queries from alerts
        for alert_file in self.alert_files:
            alert_queries = self.extract_queries_from_alerts(alert_file)
            all_queries.extend(alert_queries)
            
            self.log_success(f"Extracted {len(alert_queries)} alert queries from {os.path.basename(alert_file)}")
            
        if not all_queries:
            self.log_issue("No queries found in dashboard or alert files")
            return False
            
        self.log_success(f"Total queries to validate: {len(all_queries)}")
        
        # Step 6: Validate each query
        print(f"\n{'='*60}")
        print("VALIDATING INDIVIDUAL QUERIES")
        print("="*60)
        
        query_results = []
        for i, query_info in enumerate(all_queries, 1):
            print(f"\nValidating query {i}/{len(all_queries)}...")
            
            query_type = "alert" if 'rule' in query_info else "dashboard"
            result = self.validate_query(query_info, query_type)
            query_results.append(result)
            
        # Step 7: Check for common issues
        self.check_common_issues(all_queries)
        
        # Step 8: Validate customer-specific queries
        self.validate_customer_specific_queries(all_queries)
        
        # Step 9: Validate template variable queries
        self.validate_template_variable_queries(all_queries)
        
        # Step 10: Generate report
        self.generate_report()
        
        return all(query_results)

def main():
    validator = DashboardQueryValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()