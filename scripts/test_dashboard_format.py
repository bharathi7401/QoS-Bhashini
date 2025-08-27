#!/usr/bin/env python3
"""
Dashboard Formatting Validation Script
Enforces all formatting guidelines for Grafana dashboards
"""

import json
import glob
import sys
from pathlib import Path

class DashboardValidator:
    def __init__(self):
        self.errors = []
        self.dashboards_checked = 0
        
    def add_error(self, dashboard_name, panel_title, message):
        """Add a validation error"""
        error = {
            'dashboard': dashboard_name,
            'panel': panel_title,
            'message': message
        }
        self.errors.append(error)
        print(f"❌ ERROR in {dashboard_name} - Panel '{panel_title}': {message}")
    
    def validate_dashboard(self, file_path):
        """Validate a single dashboard file"""
        dashboard_name = Path(file_path).stem
        print(f"📊 Validating: {dashboard_name}")
        
        try:
            with open(file_path, 'r') as f:
                dashboard = json.load(f)
        except json.JSONDecodeError as e:
            self.add_error(dashboard_name, "N/A", f"Invalid JSON: {e}")
            return
        
        self.dashboards_checked += 1
        
        # Validate each panel
        for panel in dashboard.get('panels', []):
            self.validate_panel(dashboard_name, panel)
        
        print(f"✅ {dashboard_name} validation completed")
        print("---")
    
    def validate_panel(self, dashboard_name, panel):
        """Validate a single panel"""
        panel_title = panel.get('title', 'Unknown Panel')
        
        # Check 1: No units in panel titles
        title = panel.get('title', '')
        if any(unit in title for unit in ['%', 'ms', 'requests', 'per_minute']):
            self.add_error(dashboard_name, panel_title, 
                         f"Unit found in title: '{title}' - Units should be in fieldConfig")
        
        # Check 2: Has displayName in fieldConfig
        field_config = panel.get('fieldConfig', {}).get('defaults', {})
        if 'displayName' not in field_config:
            self.add_error(dashboard_name, panel_title, 
                         "Missing displayName in fieldConfig.defaults")
        
        # Check 3: Flux queries use map() function for clean output
        for target in panel.get('targets', []):
            query = target.get('query', '')
            if 'from(bucket:' in query and 'map(fn:' not in query:
                self.add_error(dashboard_name, panel_title, 
                             "Missing map() function in Flux query for clean data output")
        
        # Check 4: Proper unit configuration
        if 'unit' not in field_config:
            self.add_error(dashboard_name, panel_title, 
                         "Missing unit configuration in fieldConfig.defaults")
        
        # Check 5: No technical field names in display
        if 'displayName' in field_config:
            display_name = field_config['displayName']
            technical_terms = ['_value', '_measurement', '_field', 'raw', 'object']
            if any(term in display_name for term in technical_terms):
                self.add_error(dashboard_name, panel_title, 
                             f"Technical term in displayName: '{display_name}'")
        
        # Check 6: Clean panel titles (no technical terms)
        technical_title_terms = ['raw', 'object', 'data', 'technical', '_value']
        if any(term in title.lower() for term in technical_title_terms):
            self.add_error(dashboard_name, panel_title, 
                         f"Technical term in panel title: '{title}'")
    
    def run_validation(self):
        """Run validation on all dashboard files"""
        print("🔍 Validating Dashboard Formatting Guidelines...")
        print("=" * 60)
        
        # Find all dashboard files
        dashboard_files = glob.glob("grafana/provisioning/dashboards/**/*.json", recursive=True)
        
        if not dashboard_files:
            print("❌ No dashboard files found!")
            return False
        
        print(f"🔍 Found {len(dashboard_files)} dashboard files")
        print()
        
        # Validate each dashboard
        for file_path in dashboard_files:
            self.validate_dashboard(file_path)
        
        # Summary
        print("=" * 60)
        print("📊 Validation Summary:")
        print(f"   Dashboards checked: {self.dashboards_checked}")
        print(f"   Errors found: {len(self.errors)}")
        
        if not self.errors:
            print("🎉 All dashboards pass formatting validation!")
            print("✅ Formatting guidelines are being followed correctly.")
            return True
        else:
            print(f"❌ {len(self.errors)} formatting violations found!")
            print("🔧 Please fix these issues before committing.")
            print()
            print("📋 Common fixes:")
            print("   - Add map() functions to Flux queries")
            print("   - Remove units from panel titles")
            print("   - Add displayName to fieldConfig")
            print("   - Use proper unit settings")
            print("   - Clean up technical field names")
            return False

def main():
    """Main function"""
    validator = DashboardValidator()
    success = validator.run_validation()
    
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
