#!/usr/bin/env python3
"""
Query Validator
Validates InfluxDB queries in dashboard panels for proper structure and best practices
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

class QueryValidator:
    """Validates InfluxDB queries in dashboard panels"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate_dashboard_queries(self, file_path: Path) -> Tuple[bool, List[str], List[str], List[str]]:
        """Validate all queries in a dashboard file"""
        print(f"\n🔍 Validating queries in {file_path.name}...")
        
        # Reset for this file
        self.errors = []
        self.warnings = []
        self.info = []
        
        try:
            with open(file_path) as f:
                dashboard = json.load(f)
            
            panels = dashboard.get('panels', [])
            if not panels:
                self.warnings.append("Dashboard has no panels to validate")
                return True, self.errors, self.warnings, self.info
            
            # Validate each panel's queries
            for i, panel in enumerate(panels):
                panel_title = panel.get('title', f'Panel {i}')
                targets = panel.get('targets', [])
                
                if not targets:
                    self.warnings.append(f"Panel '{panel_title}': No query targets found")
                    continue
                
                for j, target in enumerate(targets):
                    self._validate_single_query(target, panel_title, j + 1)
            
            # Report results
            if self.errors:
                print("❌ Query validation failed:")
                for error in self.errors:
                    print(f"  - {error}")
            else:
                if self.warnings:
                    print("⚠️  Query validation passed with warnings:")
                    for warning in self.warnings:
                        print(f"  - {warning}")
                else:
                    print("✅ Query validation passed")
                
                if self.info:
                    print("ℹ️  Query information:")
                    for info in self.info:
                        print(f"  - {info}")
            
            return len(self.errors) == 0, self.errors, self.warnings, self.info
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return False, [f"Invalid JSON: {e}"], [], []
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False, [f"Validation error: {e}"], [], []
    
    def _validate_single_query(self, target: Dict, panel_title: str, target_num: int) -> None:
        """Validate a single query target"""
        query = target.get('query', '')
        query_type = target.get('queryType', 'flux')
        
        if not query:
            self.warnings.append(f"Panel '{panel_title}' target {target_num}: Empty query")
            return
        
        # Basic query structure validation
        self._validate_query_structure(query, panel_title, target_num, query_type)
        
        # InfluxDB specific validation
        if query_type == 'flux' or 'from(bucket:' in query:
            self._validate_flux_query(query, panel_title, target_num)
        
        # Performance validation
        self._validate_query_performance(query, panel_title, target_num)
    
    def _validate_query_structure(self, query: str, panel_title: str, target_num: int, query_type: str) -> None:
        """Validate basic query structure"""
        # Check for common patterns
        if 'from(' in query:
            self.info.append(f"Panel '{panel_title}' target {target_num}: Flux query detected ✓")
        elif 'SELECT' in query.upper():
            self.info.append(f"Panel '{panel_title}' target {target_num}: SQL query detected")
        else:
            self.warnings.append(f"Panel '{panel_title}' target {target_num}: Query format unclear")
        
        # Check for proper filtering
        if 'filter(' in query:
            self.info.append(f"Panel '{panel_title}' target {target_num}: Has filters ✓")
        else:
            self.warnings.append(f"Panel '{panel_title}' target {target_num}: No filters found (may impact performance)")
        
        # Check for aggregation
        if any(agg in query for agg in ['mean(', 'sum(', 'count(', 'max(', 'min(', 'aggregateWindow(']):
            self.info.append(f"Panel '{panel_title}' target {target_num}: Has aggregation ✓")
        else:
            self.warnings.append(f"Panel '{panel_title}' target {target_num}: No aggregation found (may return too many data points)")
    
    def _validate_flux_query(self, query: str, panel_title: str, target_num: int) -> None:
        """Validate Flux query specific patterns"""
        # Check for proper bucket reference
        if 'from(bucket:' in query:
            self.info.append(f"Panel '{panel_title}' target {target_num}: Proper bucket reference ✓")
        else:
            self.warnings.append(f"Panel '{panel_title}' target {target_num}: Bucket reference not found")
        
        # Check for time range
        if 'range(' in query:
            self.info.append(f"Panel '{panel_title}' target {target_num}: Time range specified ✓")
        else:
            self.warnings.append(f"Panel '{panel_title}' target {target_num}: No time range specified (may use default)")
        
        # Check for measurement filter
        if 'r["_measurement"]' in query:
            self.info.append(f"Panel '{panel_title}' target {target_num}: Measurement filter present ✓")
        else:
            self.warnings.append(f"Panel '{panel_title}' target {target_num}: No measurement filter (may query all measurements)")
        
        # Check for proper field selection
        if 'r["_field"]' in query or 'r["_value"]' in query:
            self.info.append(f"Panel '{panel_title}' target {target_num}: Field selection present ✓")
        else:
            self.warnings.append(f"Panel '{panel_title}' target {target_num}: Field selection not clear")
    
    def _validate_query_performance(self, query: str, panel_title: str, target_num: int) -> None:
        """Validate query performance characteristics"""
        # Check for time-based aggregation
        if 'aggregateWindow(' in query:
            self.info.append(f"Panel '{panel_title}' target {target_num}: Time-based aggregation ✓")
        else:
            self.warnings.append(f"Panel '{panel_title}' target {target_num}: No time aggregation (may return raw data)")
        
        # Check for limit clauses
        if 'limit(' in query:
            self.info.append(f"Panel '{panel_title}' target {target_num}: Query limit specified ✓")
        else:
            self.warnings.append(f"Panel '{panel_title}' target {target_num}: No query limit (may return large datasets)")
        
        # Check for complex regex patterns
        regex_patterns = re.findall(r'regexp\([^)]*\)', query)
        if regex_patterns:
            self.warnings.append(f"Panel '{panel_title}' target {target_num}: Complex regex patterns detected (may impact performance)")
        
        # Check for nested queries
        if query.count('from(') > 1:
            self.warnings.append(f"Panel '{panel_title}' target {target_num}: Nested queries detected (may impact performance)")

def main():
    """Main function to validate queries across all dashboards"""
    print("🔍 Query Validator")
    print("=" * 40)
    
    # Find dashboard files
    current_dir = Path('.')
    dashboard_files = list(current_dir.glob('**/*.json'))
    
    # Filter for dashboard files
    dashboard_files = [f for f in dashboard_files if 'dashboard' in f.name.lower()]
    
    if not dashboard_files:
        print("❌ No dashboard JSON files found")
        sys.exit(1)
    
    print(f"Found {len(dashboard_files)} dashboard file(s)")
    
    # Validate queries in each dashboard
    validator = QueryValidator()
    all_valid = True
    total_errors = 0
    total_warnings = 0
    
    for file_path in dashboard_files:
        is_valid, errors, warnings, info = validator.validate_dashboard_queries(file_path)
        if not is_valid:
            all_valid = False
        
        total_errors += len(errors)
        total_warnings += len(warnings)
    
    # Summary
    print("\n" + "=" * 40)
    print(f"Total dashboards processed: {len(dashboard_files)}")
    print(f"Total errors: {total_errors}")
    print(f"Total warnings: {total_warnings}")
    
    if total_errors == 0 and total_warnings == 0:
        print("\n🎉 All queries passed validation!")
    elif total_errors == 0:
        print(f"\n⚠️  All queries passed validation with {total_warnings} warnings")
    else:
        print(f"\n❌ Query validation failed with {total_errors} errors and {total_warnings} warnings")
    
    # Recommendations
    if total_warnings > 0:
        print("\n📋 Recommendations:")
        print("  - Review warnings for potential performance improvements")
        print("  - Consider adding filters and aggregations where missing")
        print("  - Ensure proper time ranges are specified")
    
    sys.exit(0 if all_valid else 1)

if __name__ == "__main__":
    main()
