# Grafana Dashboard Widget Best Practices

## Overview
This document defines the standards and best practices for creating Grafana dashboard widgets in the Bhashini QoS monitoring system. All dashboards must adhere to these guidelines to ensure consistency, maintainability, and optimal performance.

## Table of Contents
1. [General Dashboard Structure](#general-dashboard-structure)
2. [Panel Configuration Standards](#panel-configuration-standards)
3. [Query and Data Source Standards](#query-and-data-source-standards)
4. [Visualization Best Practices](#visualization-best-practices)
5. [Naming Conventions](#naming-conventions)
6. [Performance Guidelines](#performance-guidelines)
7. [CI/CD Validation Rules](#cicd-validation-rules)
8. [Common Anti-Patterns](#common-anti-patterns)

## General Dashboard Structure

### Required Dashboard Properties
```json
{
  "title": "Dashboard Title - [Environment]",
  "uid": "unique-dashboard-identifier",
  "version": 1,
  "refresh": "30s",
  "time": {
    "from": "now-1h",
    "to": "now"
  },
  "timepicker": {
    "refresh_intervals": ["5s", "10s", "30s", "1m", "5m", "15m", "30m", "1h", "2h", "1d"]
  },
  "templating": {
    "list": []
  },
  "annotations": {
    "list": []
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "links": [],
  "panels": []
}
```

### Dashboard Organization Rules
- **Maximum panels per dashboard**: 20 panels
- **Grid layout**: Use 12-column grid system consistently
- **Panel spacing**: Maintain consistent spacing between panels
- **Responsive design**: Ensure dashboards work on different screen sizes

## Panel Configuration Standards

### Required Panel Properties
```json
{
  "id": 1,
  "title": "Panel Title",
  "type": "graph",
  "gridPos": {
    "h": 8,
    "w": 12,
    "x": 0,
    "y": 0
  },
  "targets": [],
  "fieldConfig": {
    "defaults": {
      "color": {
        "mode": "palette-classic"
      },
      "custom": {
        "axisLabel": "",
        "axisPlacement": "auto",
        "barAlignment": 0,
        "drawStyle": "line",
        "fillOpacity": 10,
        "gradientMode": "none",
        "hideFrom": {
          "legend": false,
          "tooltip": false,
          "vis": false
        },
        "lineInterpolation": "linear",
        "lineWidth": 1,
        "pointSize": 5,
        "scaleDistribution": {
          "type": "linear"
        },
        "showPoints": "never",
        "spanNulls": false,
        "stacking": {
          "group": "A",
          "mode": "none"
        },
        "thresholdsStyle": {
          "mode": "off"
        }
      },
      "mappings": [],
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {
            "color": "green",
            "value": null
          },
          {
            "color": "red",
            "value": 80
          }
        ]
      },
      "unit": "short"
    },
    "overrides": []
  },
  "options": {
    "legend": {
      "calcs": [],
      "displayMode": "list",
      "placement": "bottom"
    },
    "tooltip": {
      "mode": "single",
      "sort": "none"
    }
  }
}
```

### Panel Type Guidelines

#### Time Series Panels
- **Use for**: Metrics over time, performance trends
- **Default settings**:
  - Line interpolation: linear
  - Point size: 5
  - Show points: never (unless sparse data)
  - Fill opacity: 10-20%

#### Stat Panels
- **Use for**: Current values, KPIs, status indicators
- **Default settings**:
  - Text mode: auto
  - Color mode: value
  - Graph mode: area (for context)

#### Table Panels
- **Use for**: Detailed data, logs, configuration
- **Default settings**:
  - Show header: true
  - Sort by: time (descending)
  - Column alignment: auto

#### Heatmap Panels
- **Use for**: Time-based patterns, correlation analysis
- **Default settings**:
  - Color scheme: RdYlBu
  - Bucket size: auto
  - Legend: show

## Query and Data Source Standards

### InfluxDB Query Standards
```flux
// Standard query structure
from(bucket: "qos_metrics")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
  |> filter(fn: (r) => r["metric_type"] == "latency")
  |> filter(fn: (r) => r["tenant_id"] == "$tenant")
  |> filter(fn: (r) => r["service_name"] == "$service")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "mean")
```

### Query Best Practices
- **Always use variables** for dynamic filtering
- **Implement proper aggregation** (mean, sum, count)
- **Use time windows** appropriate for the metric
- **Include error handling** for missing data
- **Optimize for performance** with proper filters

### Variable Definitions
```json
{
  "current": {
    "selected": false,
    "text": "All",
    "value": "$__all"
  },
  "datasource": null,
  "definition": "show tag values from qos_metrics where metric_type = 'latency'",
  "hide": 0,
  "includeAll": true,
  "label": "Metric Type",
  "multi": false,
  "name": "metric_type",
  "options": [],
  "query": "show tag values from qos_metrics where metric_type = 'latency'",
  "refresh": 1,
  "regex": "",
  "skipUrlSync": false,
  "sort": 0,
  "type": "query"
}
```

## Visualization Best Practices

### Color Schemes
- **Success metrics**: Green (#7EB26D)
- **Warning metrics**: Yellow (#EAB839)
- **Error metrics**: Red (#E24D42)
- **Info metrics**: Blue (#6ED0E0)
- **Neutral metrics**: Gray (#8F8BB4)

### Threshold Configuration
```json
{
  "thresholds": {
    "mode": "absolute",
    "steps": [
      {
        "color": "green",
        "value": null
      },
      {
        "color": "yellow",
        "value": 80
      },
      {
        "color": "red",
        "value": 95
      }
    ]
  }
}
```

### Legend Configuration
- **Position**: Bottom (for time series), Right (for stat panels)
- **Calculations**: Include relevant aggregations
- **Display mode**: List for multiple series, Single for KPIs

## Naming Conventions

### Dashboard Naming
- **Format**: `[Service] - [Environment] - [Purpose]`
- **Examples**:
  - `Bhashini QoS - Production - Service Overview`
  - `Translation API - Staging - Performance Metrics`
  - `Customer Dashboard - Enterprise - SLA Monitoring`

### Panel Naming
- **Format**: `[Metric] - [Service] - [Tenant]`
- **Examples**:
  - `Response Time - Translation - All Tenants`
  - `Error Rate - TTS - Enterprise Customers`
  - `Throughput - ASR - Startup Tier`

### Variable Naming
- **Format**: `[category]_[metric]`
- **Examples**:
  - `tenant_id`
  - `service_name`
  - `metric_type`
  - `sla_tier`

## Performance Guidelines

### Query Optimization
- **Limit time ranges** to reasonable periods
- **Use appropriate aggregations** to reduce data points
- **Implement caching** where possible
- **Avoid complex regex** in filters

### Dashboard Performance
- **Maximum refresh rate**: 30 seconds
- **Panel count**: Keep under 20 panels
- **Data source queries**: Limit concurrent queries
- **Template variables**: Use with caution

### Memory Management
- **Limit series**: Maximum 1000 series per panel
- **Data retention**: Use appropriate time ranges
- **Caching**: Enable query caching for static data

## CI/CD Validation Rules

### Automated Validation
All dashboards must pass the following validation checks:

#### 1. JSON Schema Validation
```bash
# Validate dashboard JSON structure
python -m jsonschema -i dashboard.json dashboard-schema.json
```

#### 2. Panel Count Validation
```bash
# Check panel count
python -c "
import json
with open('dashboard.json') as f:
    data = json.load(f)
    panel_count = len(data.get('panels', []))
    assert panel_count <= 20, f'Too many panels: {panel_count}'
    print(f'Panel count: {panel_count} ✓')
"
```

#### 3. Query Validation
```bash
# Validate InfluxDB queries
python -c "
import json
import re
with open('dashboard.json') as f:
    data = json.load(f)
    for panel in data.get('panels', []):
        for target in panel.get('targets', []):
            query = target.get('query', '')
            if 'from(bucket:' not in query:
                print(f'Warning: Panel {panel.get(\"title\")} may not have proper InfluxDB query')
"
```

#### 4. Variable Validation
```bash
# Check template variables
python -c "
import json
with open('dashboard.json') as f:
    data = json.load(f)
    variables = data.get('templating', {}).get('list', [])
    for var in variables:
        if not var.get('name') or not var.get('query'):
            print(f'Warning: Variable {var.get(\"name\", \"unnamed\")} missing required fields')
"
```

### Pre-commit Hooks
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Validating Grafana dashboard..."

# Check JSON syntax
if ! python -m json.tool dashboard.json > /dev/null 2>&1; then
    echo "❌ Invalid JSON syntax in dashboard.json"
    exit 1
fi

# Check panel count
PANEL_COUNT=$(python -c "
import json
with open('dashboard.json') as f:
    data = json.load(f)
    print(len(data.get('panels', [])))
")

if [ "$PANEL_COUNT" -gt 20 ]; then
    echo "❌ Too many panels: $PANEL_COUNT (max: 20)"
    exit 1
fi

echo "✅ Dashboard validation passed"
```

### GitHub Actions Workflow
```yaml
# .github/workflows/dashboard-validation.yml
name: Dashboard Validation

on:
  push:
    paths:
      - '**/*.json'
      - 'docs/GRAFANA_DASHBOARD_BEST_PRACTICES.md'
  pull_request:
    paths:
      - '**/*.json'
      - 'docs/GRAFANA_DASHBOARD_BEST_PRACTICES.md'

jobs:
  validate-dashboard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          pip install jsonschema
          
      - name: Validate dashboard structure
        run: |
          python scripts/validate_dashboard.py
          
      - name: Check panel count
        run: |
          python scripts/check_panel_count.py
          
      - name: Validate queries
        run: |
          python scripts/validate_queries.py
```

## Common Anti-Patterns

### ❌ Avoid These Practices
1. **Hard-coded values** instead of variables
2. **Excessive panel count** (>20 panels)
3. **Complex nested queries** without aggregation
4. **Missing error handling** for data gaps
5. **Inconsistent naming** conventions
6. **Overly frequent refresh** rates (<30s)
7. **Missing thresholds** for critical metrics
8. **Poor color choices** that don't follow standards

### ✅ Best Practices Summary
1. **Use template variables** for dynamic filtering
2. **Keep dashboards focused** and organized
3. **Implement proper aggregation** and time windows
4. **Follow naming conventions** consistently
5. **Use appropriate visualization** types
6. **Set meaningful thresholds** for alerts
7. **Optimize for performance** and readability
8. **Document dashboard purpose** and configuration

## Validation Scripts

### Dashboard Validator
```python
#!/usr/bin/env python3
# scripts/validate_dashboard.py

import json
import sys
from pathlib import Path

def validate_dashboard(file_path):
    """Validate dashboard JSON structure and content"""
    try:
        with open(file_path) as f:
            dashboard = json.load(f)
        
        errors = []
        
        # Check required fields
        required_fields = ['title', 'uid', 'version', 'panels']
        for field in required_fields:
            if field not in dashboard:
                errors.append(f"Missing required field: {field}")
        
        # Check panel count
        panel_count = len(dashboard.get('panels', []))
        if panel_count > 20:
            errors.append(f"Too many panels: {panel_count} (max: 20)")
        
        # Check panel structure
        for i, panel in enumerate(dashboard.get('panels', [])):
            if 'title' not in panel:
                errors.append(f"Panel {i}: Missing title")
            if 'type' not in panel:
                errors.append(f"Panel {i}: Missing type")
            if 'gridPos' not in panel:
                errors.append(f"Panel {i}: Missing gridPos")
        
        if errors:
            print("❌ Dashboard validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False
        else:
            print("✅ Dashboard validation passed")
            return True
            
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

if __name__ == "__main__":
    dashboard_files = list(Path('.').glob('**/*.json'))
    
    all_valid = True
    for file_path in dashboard_files:
        if 'dashboard' in file_path.name.lower():
            print(f"\nValidating {file_path}...")
            if not validate_dashboard(file_path):
                all_valid = False
    
    sys.exit(0 if all_valid else 1)
```

## Conclusion

Following these best practices ensures:
- **Consistent dashboard design** across the organization
- **Optimal performance** and user experience
- **Easier maintenance** and updates
- **Automated quality control** through CI/CD
- **Professional appearance** and usability

All dashboard changes must pass the automated validation checks before being merged into the main branch. Regular reviews and updates to these standards help maintain high-quality monitoring solutions.
