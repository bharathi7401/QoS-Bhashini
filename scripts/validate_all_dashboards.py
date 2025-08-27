#!/usr/bin/env python3
"""
Comprehensive Dashboard Validator
Runs all validation checks and provides a comprehensive report
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple
import subprocess

class ComprehensiveValidator:
    """Runs all dashboard validation checks"""
    
    def __init__(self):
        self.results = {}
        self.start_time = time.time()
    
    def run_all_validations(self) -> Dict[str, bool]:
        """Run all validation checks"""
        print("🚀 Comprehensive Dashboard Validation")
        print("=" * 60)
        
        # Find dashboard files
        dashboard_files = self._find_dashboard_files()
        if not dashboard_files:
            print("❌ No dashboard JSON files found")
            return {}
        
        print(f"Found {len(dashboard_files)} dashboard file(s)")
        print()
        
        # Run each validation
        validations = [
            ("JSON Syntax", self._validate_json_syntax),
            ("Dashboard Structure", self._validate_dashboard_structure),
            ("Panel Count", self._validate_panel_count),
            ("Query Validation", self._validate_queries),
            ("Best Practices", self._validate_best_practices)
        ]
        
        for validation_name, validation_func in validations:
            print(f"🔍 Running {validation_name} validation...")
            result = validation_func(dashboard_files)
            self.results[validation_name] = result
            print()
        
        return self.results
    
    def _find_dashboard_files(self) -> List[Path]:
        """Find all dashboard JSON files"""
        current_dir = Path('.')
        dashboard_files = list(current_dir.glob('**/*.json'))
        return [f for f in dashboard_files if 'dashboard' in f.name.lower()]
    
    def _validate_json_syntax(self, dashboard_files: List[Path]) -> bool:
        """Validate JSON syntax for all dashboards"""
        all_valid = True
        
        for file_path in dashboard_files:
            try:
                with open(file_path) as f:
                    json.load(f)
                print(f"  ✅ {file_path.name}: Valid JSON")
            except json.JSONDecodeError as e:
                print(f"  ❌ {file_path.name}: Invalid JSON - {e}")
                all_valid = False
        
        return all_valid
    
    def _validate_dashboard_structure(self, dashboard_files: List[Path]) -> bool:
        """Validate dashboard structure and required fields"""
        all_valid = True
        
        for file_path in dashboard_files:
            try:
                with open(file_path) as f:
                    data = json.load(f)
                
                # Handle both direct dashboard structure and nested dashboard structure
                dashboard = data if 'panels' in data else data.get('dashboard', {})
                
                errors = []
                
                # Check required fields
                required_fields = ['title', 'uid', 'version', 'panels']
                for field in required_fields:
                    if field not in dashboard:
                        errors.append(f"Missing {field}")
                
                # Check panel structure
                panels = dashboard.get('panels', [])
                for i, panel in enumerate(panels):
                    panel_title = panel.get('title', f'Panel {i}')
                    if 'type' not in panel:
                        errors.append(f"Panel '{panel_title}' missing type")
                    if 'gridPos' not in panel:
                        errors.append(f"Panel '{panel_title}' missing gridPos")
                
                if errors:
                    print(f"  ❌ {file_path.name}: Structure issues")
                    for error in errors:
                        print(f"    - {error}")
                    all_valid = False
                else:
                    print(f"  ✅ {file_path.name}: Structure valid")
                    
            except Exception as e:
                print(f"  ❌ {file_path.name}: Error - {e}")
                all_valid = False
        
        return all_valid
    
    def _validate_panel_count(self, dashboard_files: List[Path]) -> bool:
        """Validate panel count limits"""
        all_valid = True
        
        for file_path in dashboard_files:
            try:
                with open(file_path) as f:
                    data = json.load(f)
                
                # Handle both direct dashboard structure and nested dashboard structure
                dashboard = data if 'panels' in data else data.get('dashboard', {})
                
                panel_count = len(dashboard.get('panels', []))
                dashboard_title = dashboard.get('title', file_path.name)
                
                if panel_count > 20:
                    print(f"  ❌ {dashboard_title}: Too many panels ({panel_count})")
                    all_valid = False
                elif panel_count == 0:
                    print(f"  ⚠️  {dashboard_title}: No panels")
                else:
                    print(f"  ✅ {dashboard_title}: {panel_count} panels")
                    
            except Exception as e:
                print(f"  ❌ {file_path.name}: Error - {e}")
                all_valid = False
        
        return all_valid
    
    def _validate_queries(self, dashboard_files: List[Path]) -> bool:
        """Validate panel queries"""
        all_valid = True
        
        for file_path in dashboard_files:
            try:
                with open(file_path) as f:
                    data = json.load(f)
                
                # Handle both direct dashboard structure and nested dashboard structure
                dashboard = data if 'panels' in data else data.get('dashboard', {})
                
                dashboard_title = dashboard.get('title', file_path.name)
                panels = dashboard.get('panels', [])
                
                query_issues = 0
                for panel in panels:
                    targets = panel.get('targets', [])
                    for target in targets:
                        query = target.get('query', '')
                        if not query:
                            query_issues += 1
                        elif 'from(bucket:' not in query and 'from(' not in query:
                            query_issues += 1
                
                if query_issues > 0:
                    print(f"  ⚠️  {dashboard_title}: {query_issues} query issues")
                else:
                    print(f"  ✅ {dashboard_title}: Queries valid")
                    
            except Exception as e:
                print(f"  ❌ {file_path.name}: Error - {e}")
                all_valid = False
        
        return all_valid
    
    def _validate_best_practices(self, dashboard_files: List[Path]) -> bool:
        """Validate best practices compliance"""
        all_valid = True
        
        for file_path in dashboard_files:
            try:
                with open(file_path) as f:
                    data = json.load(f)
                
                # Handle both direct dashboard structure and nested dashboard structure
                dashboard = data if 'panels' in data else data.get('dashboard', {})
                
                dashboard_title = dashboard.get('title', file_path.name)
                issues = []
                
                # Check refresh rate
                refresh = dashboard.get('refresh', '')
                if refresh and refresh != 'false':
                    try:
                        if refresh.endswith('s'):
                            seconds = int(refresh[:-1])
                            if seconds < 30:
                                issues.append(f"Refresh rate {refresh} too frequent")
                        elif refresh.endswith('m'):
                            minutes = int(refresh[:-1])
                            if minutes < 1:
                                issues.append(f"Refresh rate {refresh} too frequent")
                    except ValueError:
                        pass
                
                # Check for template variables
                variables = dashboard.get('templating', {}).get('list', [])
                if not variables:
                    issues.append("No template variables (consider adding for dynamic filtering)")
                
                # Check time configuration
                time_config = dashboard.get('time', {})
                if not time_config:
                    issues.append("No time configuration specified")
                
                if issues:
                    print(f"  ⚠️  {dashboard_title}: Best practice issues")
                    for issue in issues:
                        print(f"    - {issue}")
                else:
                    print(f"  ✅ {dashboard_title}: Best practices followed")
                    
            except Exception as e:
                print(f"  ❌ {file_path.name}: Error - {e}")
                all_valid = False
        
        return all_valid
    
    def generate_report(self) -> None:
        """Generate comprehensive validation report"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION REPORT")
        print("=" * 60)
        
        # Summary
        total_checks = len(self.results)
        passed_checks = sum(1 for result in self.results.values() if result)
        failed_checks = total_checks - passed_checks
        
        print(f"Total validation checks: {total_checks}")
        print(f"Passed: {passed_checks}")
        print(f"Failed: {failed_checks}")
        
        # Individual results
        print("\nDetailed Results:")
        for check_name, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {check_name}: {status}")
        
        # Overall status
        if failed_checks == 0:
            print("\n🎉 All validations passed! Dashboards are ready for production.")
        else:
            print(f"\n❌ {failed_checks} validation(s) failed. Please review and fix issues.")
        
        # Recommendations
        if failed_checks > 0:
            print("\n📋 Recommendations:")
            print("  - Review failed validations above")
            print("  - Fix critical issues before deployment")
            print("  - Consider running individual validation scripts for detailed feedback")
        
        # Performance metrics
        elapsed_time = time.time() - self.start_time
        print(f"\n⏱️  Validation completed in {elapsed_time:.2f} seconds")
    
    def run_individual_scripts(self) -> None:
        """Run the individual validation scripts for detailed output"""
        print("\n🔍 Running individual validation scripts for detailed feedback...")
        print("=" * 60)
        
        scripts = [
            "validate_dashboard.py",
            "check_panel_count.py", 
            "validate_queries.py"
        ]
        
        for script in scripts:
            script_path = Path("scripts") / script
            if script_path.exists():
                print(f"\n📜 Running {script}...")
                try:
                    result = subprocess.run([sys.executable, str(script_path)], 
                                          capture_output=True, text=True, cwd="..")
                    if result.stdout:
                        print(result.stdout)
                    if result.stderr:
                        print(f"Errors: {result.stderr}")
                except Exception as e:
                    print(f"Error running {script}: {e}")
            else:
                print(f"⚠️  Script {script} not found")

def main():
    """Main function"""
    validator = ComprehensiveValidator()
    
    # Run all validations
    results = validator.run_all_validations()
    
    if not results:
        print("❌ No validations could be completed")
        sys.exit(1)
    
    # Generate report
    validator.generate_report()
    
    # Optionally run individual scripts for detailed feedback
    if any(not result for result in results.values()):
        print("\nWould you like to run individual validation scripts for detailed feedback? (y/n)")
        try:
            response = input().lower().strip()
            if response in ['y', 'yes']:
                validator.run_individual_scripts()
        except KeyboardInterrupt:
            print("\nSkipping individual script execution")
    
    # Exit with appropriate code
    all_passed = all(results.values())
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
