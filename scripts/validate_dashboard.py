#!/usr/bin/env python3
"""
Grafana Dashboard Validator
Validates dashboard JSON structure and content according to best practices
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

class DashboardValidator:
    """Validates Grafana dashboard JSON files against best practices"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def validate_dashboard(self, file_path: Path) -> bool:
        """Validate a single dashboard file"""
        print(f"\n🔍 Validating {file_path.name}...")
        
        try:
            with open(file_path) as f:
                dashboard = json.load(f)
            
            # Reset errors for this file
            self.errors = []
            self.warnings = []
            
            # Run all validations
            self._validate_required_fields(dashboard)
            self._validate_panel_count(dashboard)
            self._validate_panel_structure(dashboard)
            self._validate_dashboard_properties(dashboard)
            self._validate_variables(dashboard)
            self._validate_queries(dashboard)
            
            # Report results
            if self.errors:
                print("❌ Dashboard validation failed:")
                for error in self.errors:
                    print(f"  - {error}")
                return False
            else:
                if self.warnings:
                    print("⚠️  Dashboard validation passed with warnings:")
                    for warning in self.warnings:
                        print(f"  - {warning}")
                else:
                    print("✅ Dashboard validation passed")
                return True
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return False
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False
    
    def _validate_required_fields(self, dashboard: Dict[str, Any]) -> None:
        """Check for required dashboard fields"""
        required_fields = ['title', 'uid', 'version', 'panels']
        for field in required_fields:
            if field not in dashboard:
                self.errors.append(f"Missing required field: {field}")
    
    def _validate_panel_count(self, dashboard: Dict[str, Any]) -> None:
        """Check panel count limit"""
        panel_count = len(dashboard.get('panels', []))
        if panel_count > 20:
            self.errors.append(f"Too many panels: {panel_count} (max: 20)")
        elif panel_count == 0:
            self.warnings.append("Dashboard has no panels")
        else:
            print(f"  📊 Panel count: {panel_count} ✓")
    
    def _validate_panel_structure(self, dashboard: Dict[str, Any]) -> None:
        """Validate individual panel structure"""
        for i, panel in enumerate(dashboard.get('panels', [])):
            panel_id = panel.get('id', i)
            panel_title = panel.get('title', f'Panel {i}')
            
            # Check required panel fields
            required_panel_fields = ['title', 'type', 'gridPos']
            for field in required_panel_fields:
                if field not in panel:
                    self.errors.append(f"Panel {panel_id} ({panel_title}): Missing {field}")
            
            # Check grid position
            if 'gridPos' in panel:
                grid_pos = panel['gridPos']
                if not isinstance(grid_pos, dict):
                    self.errors.append(f"Panel {panel_id} ({panel_title}): Invalid gridPos format")
                else:
                    required_grid_fields = ['h', 'w', 'x', 'y']
                    for field in required_grid_fields:
                        if field not in grid_pos:
                            self.errors.append(f"Panel {panel_id} ({panel_title}): Missing gridPos.{field}")
            
            # Check panel type
            if 'type' in panel:
                valid_types = ['graph', 'stat', 'table', 'heatmap', 'timeseries', 'gauge', 'bar']
                if panel['type'] not in valid_types:
                    self.warnings.append(f"Panel {panel_id} ({panel_title}): Unusual panel type: {panel['type']}")
    
    def _validate_dashboard_properties(self, dashboard: Dict[str, Any]) -> None:
        """Validate dashboard-level properties"""
        # Check refresh rate
        refresh = dashboard.get('refresh', '')
        if refresh and refresh != 'false':
            try:
                if refresh.endswith('s'):
                    seconds = int(refresh[:-1])
                    if seconds < 30:
                        self.warnings.append(f"Refresh rate {refresh} is very frequent (recommend >=30s)")
                elif refresh.endswith('m'):
                    minutes = int(refresh[:-1])
                    if minutes < 1:
                        self.warnings.append(f"Refresh rate {refresh} is very frequent (recommend >=1m)")
            except ValueError:
                pass
        
        # Check time range
        time_config = dashboard.get('time', {})
        if time_config:
            from_time = time_config.get('from', '')
            to_time = time_config.get('to', '')
            if from_time and to_time:
                print(f"  ⏰ Time range: {from_time} to {to_time} ✓")
    
    def _validate_variables(self, dashboard: Dict[str, Any]) -> None:
        """Validate template variables"""
        variables = dashboard.get('templating', {}).get('list', [])
        if variables:
            print(f"  🔧 Template variables: {len(variables)} ✓")
            
            for var in variables:
                var_name = var.get('name', 'unnamed')
                if not var.get('query'):
                    self.warnings.append(f"Variable '{var_name}' missing query definition")
                if not var.get('type'):
                    self.warnings.append(f"Variable '{var_name}' missing type")
        else:
            print("  🔧 Template variables: None (consider adding for dynamic filtering)")
    
    def _validate_queries(self, dashboard: Dict[str, Any]) -> None:
        """Validate panel queries"""
        for i, panel in enumerate(dashboard.get('panels', [])):
            panel_title = panel.get('title', f'Panel {i}')
            targets = panel.get('targets', [])
            
            if not targets:
                self.warnings.append(f"Panel '{panel_title}' has no query targets")
                continue
            
            for j, target in enumerate(targets):
                query = target.get('query', '')
                if not query:
                    self.warnings.append(f"Panel '{panel_title}' target {j+1}: Empty query")
                    continue
                
                # Check for InfluxDB specific patterns
                if 'from(bucket:' in query:
                    print(f"    📊 Panel '{panel_title}' target {j+1}: InfluxDB query ✓")
                elif 'from(' in query:
                    print(f"    📊 Panel '{panel_title}' target {j+1}: Flux query ✓")
                else:
                    self.warnings.append(f"Panel '{panel_title}' target {j+1}: Query format unclear")

def main():
    """Main validation function"""
    print("🚀 Grafana Dashboard Validator")
    print("=" * 50)
    
    # Find dashboard files
    current_dir = Path('.')
    dashboard_files = list(current_dir.glob('**/*.json'))
    
    # Filter for dashboard files
    dashboard_files = [f for f in dashboard_files if 'dashboard' in f.name.lower()]
    
    if not dashboard_files:
        print("❌ No dashboard JSON files found")
        sys.exit(1)
    
    print(f"Found {len(dashboard_files)} dashboard file(s)")
    
    # Validate each dashboard
    validator = DashboardValidator()
    all_valid = True
    
    for file_path in dashboard_files:
        if not validator.validate_dashboard(file_path):
            all_valid = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_valid:
        print("🎉 All dashboards passed validation!")
        sys.exit(0)
    else:
        print("❌ Some dashboards failed validation")
        sys.exit(1)

if __name__ == "__main__":
    main()
