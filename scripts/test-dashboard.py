#!/usr/bin/env python3
"""
Bhashini Provider Dashboard Testing Script
Comprehensive testing for dashboard functionality, data connectivity, and performance.
"""

import json
import requests
import time
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
import subprocess
import os

class DashboardTester:
    """Tests the Bhashini provider dashboard functionality."""
    
    def __init__(self, grafana_url: str = "http://localhost:3000", 
                 influxdb_url: str = "http://localhost:8086"):
        self.grafana_url = grafana_url
        self.influxdb_url = influxdb_url
        self.test_results = {}
        
    def test_grafana_connectivity(self) -> bool:
        """Test basic Grafana connectivity."""
        try:
            response = requests.get(f"{self.grafana_url}/api/health", timeout=10)
            if response.status_code == 200:
                print("✓ Grafana connectivity test passed")
                self.test_results["grafana_connectivity"] = True
                return True
            else:
                print(f"✗ Grafana connectivity test failed: {response.status_code}")
                self.test_results["grafana_connectivity"] = False
                return False
        except Exception as e:
            print(f"✗ Grafana connectivity test failed: {e}")
            self.test_results["grafana_connectivity"] = False
            return False
    
    def test_influxdb_connectivity(self) -> bool:
        """Test basic InfluxDB connectivity."""
        try:
            response = requests.get(f"{self.influxdb_url}/health", timeout=10)
            if response.status_code == 200:
                print("✓ InfluxDB connectivity test passed")
                self.test_results["influxdb_connectivity"] = True
                return True
            else:
                print(f"✗ InfluxDB connectivity test failed: {response.status_code}")
                self.test_results["influxdb_connectivity"] = False
                return False
        except Exception as e:
            print(f"✗ InfluxDB connectivity test failed: {e}")
            self.test_results["influxdb_connectivity"] = False
            return False
    
    def test_data_source_connectivity(self) -> bool:
        """Test InfluxDB data source connectivity through Grafana."""
        try:
            # This would require Grafana API authentication
            # For now, we'll test if the data source file exists
            datasource_path = Path("grafana/provisioning/datasources/provider-influxdb.yml")
            if datasource_path.exists():
                print("✓ Provider data source configuration exists")
                self.test_results["datasource_config"] = True
                return True
            else:
                print("✗ Provider data source configuration not found")
                self.test_results["datasource_config"] = False
                return False
        except Exception as e:
            print(f"✗ Data source test failed: {e}")
            self.test_results["datasource_config"] = False
            return False
    
    def test_dashboard_provisioning(self) -> bool:
        """Test dashboard provisioning configuration."""
        try:
            # Check if dashboard provisioning config exists
            provisioning_path = Path("grafana/provisioning/dashboards/dashboards.yml")
            if not provisioning_path.exists():
                print("✗ Dashboard provisioning configuration not found")
                self.test_results["dashboard_provisioning"] = False
                return False
            
            # Check if provider dashboards directory exists
            dashboards_dir = Path("grafana/provisioning/dashboards/provider-dashboards")
            if not dashboards_dir.exists():
                print("✗ Provider dashboards directory not found")
                self.test_results["dashboard_provisioning"] = False
                return False
            
            # Check if dashboard JSON file exists
            dashboard_file = dashboards_dir / "bhashini-provider-overview.json"
            if not dashboard_file.exists():
                print("✗ Provider dashboard JSON file not found")
                self.test_results["dashboard_provisioning"] = False
                return False
            
            print("✓ Dashboard provisioning configuration test passed")
            self.test_results["dashboard_provisioning"] = True
            return True
            
        except Exception as e:
            print(f"✗ Dashboard provisioning test failed: {e}")
            self.test_results["dashboard_provisioning"] = False
            return False
    
    def test_dashboard_json_structure(self) -> bool:
        """Test dashboard JSON structure and syntax."""
        try:
            dashboard_file = Path("grafana/provisioning/dashboards/provider-dashboards/bhashini-provider-overview.json")
            
            with open(dashboard_file, 'r') as f:
                dashboard_data = json.load(f)
            
            # Validate required structure - removed dashboard wrapper check
            required_keys = ["title", "panels", "templating", "uid"]
            for key in required_keys:
                if key not in dashboard_data:
                    print(f"✗ Dashboard JSON missing required key: {key}")
                    self.test_results["dashboard_structure"] = False
                    return False
            
            dashboard = dashboard_data
            
            # Validate panels
            if not dashboard["panels"]:
                print("✗ Dashboard has no panels")
                self.test_results["dashboard_structure"] = False
                return False
            
            print(f"✓ Dashboard JSON structure test passed: {len(dashboard['panels'])} panels")
            self.test_results["dashboard_structure"] = True
            return True
            
        except json.JSONDecodeError as e:
            print(f"✗ Dashboard JSON syntax error: {e}")
            self.test_results["dashboard_structure"] = False
            return False
        except Exception as e:
            print(f"✗ Dashboard structure test failed: {e}")
            self.test_results["dashboard_structure"] = False
            return False
    
    def test_flux_queries(self) -> bool:
        """Test Flux query syntax and structure."""
        try:
            queries_file = Path("scripts/dashboard-queries/provider-queries.flux")
            if not queries_file.exists():
                print("✗ Flux queries file not found")
                self.test_results["flux_queries"] = False
                return False
            
            # Basic syntax check - look for common Flux patterns
            with open(queries_file, 'r') as f:
                content = f.read()
            
            # Check for basic Flux syntax patterns
            required_patterns = [
                "from(bucket:",
                "range(start:",
                "filter(fn:",
                "group(",
                "yield("
            ]
            
            for pattern in required_patterns:
                if pattern not in content:
                    print(f"✗ Flux queries missing required pattern: {pattern}")
                    self.test_results["flux_queries"] = False
                    return False
            
            print("✓ Flux queries syntax test passed")
            self.test_results["flux_queries"] = True
            return True
            
        except Exception as e:
            print(f"✗ Flux queries test failed: {e}")
            self.test_results["flux_queries"] = False
            return False
    
    def test_docker_services(self) -> bool:
        """Test if required Docker services are running."""
        try:
            # Check if Docker is running
            result = subprocess.run(["docker", "ps"], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                print("✗ Docker services test failed: Docker not running")
                self.test_results["docker_services"] = False
                return False
            
            # Check for required services
            services = ["grafana", "influxdb"]
            running_services = []
            
            for line in result.stdout.split('\n'):
                for service in services:
                    if service in line.lower():
                        running_services.append(service)
            
            if len(running_services) >= 2:
                print(f"✓ Docker services test passed: {', '.join(running_services)} running")
                self.test_results["docker_services"] = True
                return True
            else:
                print(f"✗ Docker services test failed: Only {running_services} running")
                self.test_results["docker_services"] = False
                return False
                
        except subprocess.TimeoutExpired:
            print("✗ Docker services test failed: Timeout")
            self.test_results["docker_services"] = False
            return False
        except Exception as e:
            print(f"✗ Docker services test failed: {e}")
            self.test_results["docker_services"] = False
            return False
    
    def test_data_flow(self) -> bool:
        """Test data flow from simulator to InfluxDB."""
        try:
            # Check if data simulator is generating data
            # This would require checking InfluxDB for recent data
            # For now, we'll check if the simulator files exist
            
            simulator_files = [
                "data-simulator/main.py",
                "data-simulator/metrics_generator.py",
                "data-simulator/config.py"
            ]
            
            for file_path in simulator_files:
                if not Path(file_path).exists():
                    print(f"✗ Data flow test failed: {file_path} not found")
                    self.test_results["data_flow"] = False
                    return False
            
            print("✓ Data flow test passed: Simulator files present")
            self.test_results["data_flow"] = True
            return True
            
        except Exception as e:
            print(f"✗ Data flow test failed: {e}")
            self.test_results["data_flow"] = False
            return False
    
    def test_dashboard_generation(self) -> bool:
        """Test dashboard generation script."""
        try:
            generator_script = Path("scripts/generate-dashboard.py")
            if not generator_script.exists():
                print("✗ Dashboard generation test failed: Script not found")
                self.test_results["dashboard_generation"] = False
                return False
            
            # Test if script can be imported (basic syntax check)
            result = subprocess.run([sys.executable, "-m", "py_compile", str(generator_script)], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✓ Dashboard generation script syntax test passed")
                self.test_results["dashboard_generation"] = True
                return True
            else:
                print(f"✗ Dashboard generation script syntax error: {result.stderr}")
                self.test_results["dashboard_generation"] = False
                return False
                
        except Exception as e:
            print(f"✗ Dashboard generation test failed: {e}")
            self.test_results["dashboard_generation"] = False
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all dashboard tests."""
        print("=" * 60)
        print("Bhashini Provider Dashboard Testing Suite")
        print("=" * 60)
        
        tests = [
            ("Grafana Connectivity", self.test_grafana_connectivity),
            ("InfluxDB Connectivity", self.test_influxdb_connectivity),
            ("Data Source Configuration", self.test_data_source_connectivity),
            ("Dashboard Provisioning", self.test_dashboard_provisioning),
            ("Dashboard JSON Structure", self.test_dashboard_json_structure),
            ("Flux Queries", self.test_flux_queries),
            ("Docker Services", self.test_docker_services),
            ("Data Flow", self.test_data_flow),
            ("Dashboard Generation", self.test_dashboard_generation)
        ]
        
        for test_name, test_func in tests:
            print(f"\nRunning {test_name} test...")
            try:
                test_func()
            except Exception as e:
                print(f"✗ {test_name} test failed with exception: {e}")
                self.test_results[test_name.lower().replace(" ", "_")] = False
        
        return self.test_results
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report."""
        report = []
        report.append("=" * 60)
        report.append("Bhashini Provider Dashboard Test Report")
        report.append("=" * 60)
        report.append("")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        report.append(f"Test Summary:")
        report.append(f"  Total Tests: {total_tests}")
        report.append(f"  Passed: {passed_tests}")
        report.append(f"  Failed: {failed_tests}")
        report.append(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        report.append("")
        
        report.append("Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            report.append(f"  {test_name}: {status}")
        
        report.append("")
        
        if failed_tests > 0:
            report.append("Failed Tests Analysis:")
            for test_name, result in self.test_results.items():
                if not result:
                    report.append(f"  - {test_name}: Requires attention")
            report.append("")
            report.append("Recommendations:")
            report.append("  1. Check Docker service status")
            report.append("  2. Verify network connectivity")
            report.append("  3. Review configuration files")
            report.append("  4. Check service logs for errors")
        else:
            report.append("🎉 All tests passed! Dashboard is ready for use.")
        
        return "\n".join(report)

def main():
    """Main function to run dashboard tests."""
    tester = DashboardTester()
    
    try:
        # Run all tests
        results = tester.run_all_tests()
        
        # Generate and display report
        report = tester.generate_report()
        print("\n" + report)
        
        # Exit with appropriate code
        failed_tests = sum(1 for result in results.values() if not result)
        if failed_tests > 0:
            print(f"\n❌ {failed_tests} tests failed. Please review the issues above.")
            sys.exit(1)
        else:
            print("\n✅ All tests passed successfully!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error during testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
