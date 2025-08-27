#!/usr/bin/env python3
"""
Panel Count Validator
Checks that all dashboards have an appropriate number of panels (≤20)
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def check_panel_count(file_path: Path) -> Tuple[bool, int, List[str]]:
    """Check panel count for a single dashboard file"""
    issues = []
    
    try:
        with open(file_path) as f:
            dashboard = json.load(f)
        
        panel_count = len(dashboard.get('panels', []))
        dashboard_title = dashboard.get('title', file_path.name)
        
        # Check panel count limit
        if panel_count > 20:
            issues.append(f"Too many panels: {panel_count} (max: 20)")
            return False, panel_count, issues
        
        # Check for empty dashboards
        if panel_count == 0:
            issues.append("Dashboard has no panels")
            return False, panel_count, issues
        
        # Check for very few panels (might indicate incomplete dashboard)
        if panel_count < 3:
            issues.append(f"Very few panels: {panel_count} (consider adding more)")
        
        return True, panel_count, issues
        
    except json.JSONDecodeError as e:
        issues.append(f"Invalid JSON: {e}")
        return False, 0, issues
    except Exception as e:
        issues.append(f"Error reading file: {e}")
        return False, 0, issues

def main():
    """Main function to check panel counts across all dashboards"""
    print("📊 Panel Count Validator")
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
    print()
    
    # Check each dashboard
    all_valid = True
    total_panels = 0
    dashboard_summary = []
    
    for file_path in dashboard_files:
        is_valid, panel_count, issues = check_panel_count(file_path)
        dashboard_title = file_path.name
        
        # Try to get actual dashboard title
        try:
            with open(file_path) as f:
                data = json.load(f)
                dashboard_title = data.get('title', file_path.name)
        except:
            pass
        
        status = "✅" if is_valid else "❌"
        print(f"{status} {dashboard_title}: {panel_count} panels")
        
        if issues:
            for issue in issues:
                print(f"    ⚠️  {issue}")
        
        if not is_valid:
            all_valid = False
        
        total_panels += panel_count
        dashboard_summary.append((dashboard_title, panel_count, is_valid))
    
    # Summary
    print("\n" + "=" * 40)
    print(f"Total dashboards: {len(dashboard_files)}")
    print(f"Total panels: {total_panels}")
    print(f"Average panels per dashboard: {total_panels / len(dashboard_files):.1f}")
    
    # Panel count distribution
    panel_counts = [count for _, count, _ in dashboard_summary]
    if panel_counts:
        print(f"Min panels: {min(panel_counts)}")
        print(f"Max panels: {max(panel_counts)}")
    
    # Recommendations
    print("\n📋 Recommendations:")
    if any(count > 15 for _, count, _ in dashboard_summary):
        print("  - Some dashboards are approaching the 20-panel limit")
        print("  - Consider splitting large dashboards into focused views")
    
    if any(count < 3 for _, count, _ in dashboard_summary):
        print("  - Some dashboards have very few panels")
        print("  - Consider adding more metrics or combining with other dashboards")
    
    if all_valid:
        print("\n🎉 All dashboards passed panel count validation!")
        sys.exit(0)
    else:
        print("\n❌ Some dashboards failed panel count validation")
        sys.exit(1)

if __name__ == "__main__":
    main()
