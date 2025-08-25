#!/usr/bin/env python3
"""
Data Flow Verification Script for Bhashini QoS Monitoring
Tests connectivity, data ingestion, and multi-tenant isolation
"""

import os
import sys
import time
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data-simulator'))

from config import Config

def load_environment():
    """Load environment variables from .env file and secrets"""
    try:
        # Load main .env file
        load_dotenv()
        
        # Load secrets file if it exists
        secrets_path = os.path.join(os.path.dirname(__file__), '..', 'secrets', 'influxdb_tokens.env')
        if os.path.exists(secrets_path):
            load_dotenv(secrets_path)
            print("✅ Secrets file loaded successfully")
        
        # Resolve token from multiple possible sources
        token = os.getenv('INFLUXDB_TOKEN') or os.getenv('INFLUXDB_VERIFICATION_TOKEN')
        if token:
            os.environ['INFLUXDB_TOKEN'] = token
            print("✅ Token resolved successfully")
        else:
            print("❌ No valid token found in environment or secrets")
            return False
        
        # Check for required environment variables
        required_vars = [
            'INFLUXDB_URL',
            'INFLUXDB_TOKEN',
            'INFLUXDB_ORG',
            'INFLUXDB_BUCKET'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            print("Please check your .env file and secrets")
            return False
        
        print("✅ Environment configuration loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error loading environment: {str(e)}")
        return False

def test_influxdb_connectivity():
    """Test basic InfluxDB connectivity"""
    print("🔌 Testing InfluxDB connectivity...")
    
    try:
        client = InfluxDBClient(
            url=os.getenv('INFLUXDB_URL'),
            token=os.getenv('INFLUXDB_TOKEN'),
            org=os.getenv('INFLUXDB_ORG'),
            timeout=10_000
        )
        
        # Test ping
        client.ping()
        print("✅ InfluxDB connection successful")
        
        # Test query API
        query_api = client.query_api()
        result = query_api.query('buckets()', org=os.getenv('INFLUXDB_ORG'))
        
        buckets = []
        for table in result:
            for record in table.records:
                buckets.append(record.get_value())
        print(f"✅ Found {len(buckets)} buckets: {buckets}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ InfluxDB connectivity test failed: {str(e)}")
        return False

def test_data_ingestion():
    """Test data ingestion and retrieval"""
    print("\n📊 Testing data ingestion...")
    
    try:
        client = InfluxDBClient(
            url=os.getenv('INFLUXDB_URL'),
            token=os.getenv('INFLUXDB_TOKEN'),
            org=os.getenv('INFLUXDB_ORG'),
            timeout=10_000
        )
        
        query_api = client.query_api()
        
        # Check for recent metrics
        query = f'''
        from(bucket: "{os.getenv('INFLUXDB_BUCKET')}")
            |> range(start: -10m)
            |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
            |> count()
        '''
        
        result = query_api.query(query, org=os.getenv('INFLUXDB_ORG'))
        
        if result:
            count = sum(rec.get_value() for tbl in result for rec in tbl.records)
            print(f"✅ Found {count} metrics in the last 10 minutes")
            
            if count > 0:
                print("✅ Data ingestion is working")
                return True
            else:
                print("⚠️  No recent metrics found - simulator may not be running")
                return False
        else:
            print("❌ No results from query")
            return False
            
    except Exception as e:
        print(f"❌ Data ingestion test failed: {str(e)}")
        return False
    finally:
        if 'client' in locals():
            client.close()

def test_schema_validation():
    """Test that metrics have the correct schema (tags and fields)"""
    print("\n📋 Testing schema validation...")
    
    try:
        client = InfluxDBClient(
            url=os.getenv('INFLUXDB_URL'),
            token=os.getenv('INFLUXDB_TOKEN'),
            org=os.getenv('INFLUXDB_ORG'),
            timeout=10_000
        )
        
        query_api = client.query_api()
        
        # Query tag keys
        tag_query = f'''
        from(bucket: "{os.getenv('INFLUXDB_BUCKET')}")
            |> range(start: -5m)
            |> filter(fn: (r) => r._measurement == "qos_metrics")
            |> schema.tagKeys()
        '''
        
        tag_result = query_api.query(tag_query, org=os.getenv('INFLUXDB_ORG'))
        tag_keys = []
        for table in tag_result:
            for record in table.records:
                tag_keys.append(record.get_value())
        
        # Query field keys
        field_query = f'''
        from(bucket: "{os.getenv('INFLUXDB_BUCKET')}")
            |> range(start: -5m)
            |> filter(fn: (r) => r._measurement == "qos_metrics")
            |> schema.fieldKeys()
        '''
        
        field_result = query_api.query(field_query, org=os.getenv('INFLUXDB_ORG'))
        field_keys = []
        for table in field_result:
            for record in table.records:
                field_keys.append(record.get_value())
        
        print(f"✅ Found tag keys: {tag_keys}")
        print(f"✅ Found field keys: {field_keys}")
        
        # Validate required tags
        required_tags = ['tenant_id', 'service_name', 'metric_type', 'sla_tier']
        missing_tags = [tag for tag in required_tags if tag not in tag_keys]
        
        if missing_tags:
            print(f"❌ Missing required tags: {missing_tags}")
            return False
        else:
            print("✅ All required tags present")
        
        # Validate required fields
        required_fields = ['value', 'unit']
        missing_fields = [field for field in required_fields if field not in field_keys]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        else:
            print("✅ All required fields present")
        
        # Test a sample record to ensure data structure
        sample_query = f'''
        from(bucket: "{os.getenv('INFLUXDB_BUCKET')}")
            |> range(start: -5m)
            |> filter(fn: (r) => r._measurement == "qos_metrics")
            |> limit(n: 1)
        '''
        
        sample_result = query_api.query(sample_query, org=os.getenv('INFLUXDB_ORG'))
        if sample_result:
            for table in sample_result:
                for record in table.records:
                    # Check that value field is numeric
                    if record.get_field() == "value":
                        try:
                            float(record.get_value())
                            print("✅ Value field contains numeric data")
                        except (ValueError, TypeError):
                            print("❌ Value field is not numeric")
                            return False
                    
                    # Check that unit field is present
                    if record.get_field() == "unit":
                        unit_value = record.get_value()
                        if unit_value in ['ms', 'percentage', 'requests_per_minute']:
                            print("✅ Unit field contains valid values")
                        else:
                            print(f"⚠️  Unexpected unit value: {unit_value}")
        
        print("✅ Schema validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Schema validation test failed: {str(e)}")
        return False
    finally:
        if 'client' in locals():
            client.close()

def test_multi_tenant_isolation():
    """Test multi-tenant data isolation"""
    print("\n🏢 Testing multi-tenant isolation...")
    
    try:
        client = InfluxDBClient(
            url=os.getenv('INFLUXDB_URL'),
            token=os.getenv('INFLUXDB_TOKEN'),
            org=os.getenv('INFLUXDB_ORG'),
            timeout=10_000
        )
        
        query_api = client.query_api()
        
        # Get unique tenants
        tenant_query = f'''
        from(bucket: "{os.getenv('INFLUXDB_BUCKET')}")
            |> range(start: -1h)
            |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
            |> group(columns: ["tenant_id"])
            |> distinct(column: "tenant_id")
        '''
        
        tenant_result = query_api.query(tenant_query, org=os.getenv('INFLUXDB_ORG'))
        
        if tenant_result:
            tenants = []
            for table in tenant_result:
                for record in table.records:
                    tenants.append(record.get_value())
            print(f"✅ Found {len(tenants)} tenants: {tenants}")
            
            # Check that each tenant has data
            for tenant in tenants[:3]:  # Check first 3 tenants
                tenant_data_query = f'''
                from(bucket: "{os.getenv('INFLUXDB_BUCKET')}")
                    |> range(start: -1h)
                    |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
                    |> filter(fn: (r) => r["tenant_id"] == "{tenant}")
                    |> count()
                '''
                
                tenant_result = query_api.query(tenant_data_query, org=os.getenv('INFLUXDB_ORG'))
                if tenant_result:
                    count = sum(rec.get_value() for tbl in tenant_result for rec in tbl.records)
                    print(f"   {tenant}: {count} metrics")
            
            return True
        else:
            print("❌ No tenant data found")
            return False
            
    except Exception as e:
        print(f"❌ Multi-tenant isolation test failed: {str(e)}")
        return False
    finally:
        if 'client' in locals():
            client.close()

def test_service_coverage():
    """Test that all expected services have metrics"""
    print("\n🔧 Testing service coverage...")
    
    try:
        client = InfluxDBClient(
            url=os.getenv('INFLUXDB_URL'),
            token=os.getenv('INFLUXDB_TOKEN'),
            org=os.getenv('INFLUXDB_ORG'),
            timeout=10_000
        )
        
        query_api = client.query_api()
        
        # Get unique services
        service_query = f'''
        from(bucket: "{os.getenv('INFLUXDB_BUCKET')}")
            |> range(start: -1h)
            |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
            |> group(columns: ["service_name"])
            |> distinct(column: "service_name")
        '''
        
        service_result = query_api.query(service_query, org=os.getenv('INFLUXDB_ORG'))
        
        if service_result:
            services = []
            for table in service_result:
                for record in table.records:
                    services.append(record.get_value())
            expected_services = ['translation', 'tts', 'asr']
            
            print(f"✅ Found {len(services)} services: {services}")
            
            missing_services = [s for s in expected_services if s not in services]
            if missing_services:
                print(f"⚠️  Missing services: {missing_services}")
                return False
            else:
                print("✅ All expected services have metrics")
                return True
        else:
            print("❌ No service data found")
            return False
            
    except Exception as e:
        print(f"❌ Service coverage test failed: {str(e)}")
        return False
    finally:
        if 'client' in locals():
            client.close()

def main():
    """Run all verification tests"""
    print("🚀 Bhashini QoS Monitoring - Data Flow Verification")
    print("=" * 60)
    
    # Load environment
    if not load_environment():
        sys.exit(1)
    
    # Run tests
    tests = [
        test_influxdb_connectivity,
        test_data_ingestion,
        test_schema_validation,
        test_multi_tenant_isolation,
        test_service_coverage
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 Verification Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Data flow is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration and services.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
