#!/usr/bin/env python3
"""
Bhashini Provider Dashboard Generator
Generates comprehensive provider dashboard JSON configuration programmatically.
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path

class DashboardGenerator:
    """Generates Bhashini provider dashboard configurations."""
    
    def __init__(self, output_dir: str = "grafana/provisioning/dashboards/provider-dashboards"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Dashboard configuration
        self.dashboard_config = {
            "dashboard": {
                "id": None,
                "title": "Bhashini Provider Overview",
                "tags": ["bhashini", "provider", "qos", "monitoring"],
                "style": "dark",
                "timezone": "browser",
                "panels": [],
                "templating": {"list": []},
                "time": {"from": "now-6h", "to": "now"},
                "timepicker": {},
                "timezone": "",
                "uid": "bhashini-provider-overview",
                "version": 1
            }
        }
        
        # Panel counter
        self.panel_id = 1
        
    def create_stat_panel(self, title: str, query: str, unit: str = "none", 
                          thresholds: Optional[Dict] = None, position: Dict[str, int] = None) -> Dict[str, Any]:
        """Create a stat panel for KPIs."""
        panel = {
            "id": self.panel_id,
            "title": title,
            "type": "stat",
            "targets": [{
                "refId": "A",
                "query": query,
                "datasource": {
                    "type": "influxdb",
                    "uid": "InfluxDB-Provider-CrossTenant"
                }
            }],
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "mappings": [],
                    "unit": unit
                }
            },
            "gridPos": position or {"h": 8, "w": 6, "x": 0, "y": 0}
        }
        
        if thresholds:
            panel["fieldConfig"]["defaults"]["color"]["mode"] = "thresholds"
            panel["fieldConfig"]["defaults"]["thresholds"] = thresholds
            
        self.panel_id += 1
        return panel
    
    def create_timeseries_panel(self, title: str, targets: List[Dict], position: Dict[str, int] = None) -> Dict[str, Any]:
        """Create a time series panel for trends."""
        panel = {
            "id": self.panel_id,
            "title": title,
            "type": "timeseries",
            "targets": targets,
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {
                        "axisLabel": "",
                        "axisPlacement": "auto",
                        "barAlignment": 0,
                        "drawStyle": "line",
                        "fillOpacity": 10,
                        "gradientMode": "none",
                        "hideFrom": {"legend": False, "tooltip": False, "vis": False},
                        "lineInterpolation": "linear",
                        "lineWidth": 1,
                        "pointSize": 5,
                        "scaleDistribution": {"type": "linear"},
                        "showPoints": "never",
                        "spanNulls": False,
                        "stacking": {"group": "A", "mode": "none"},
                        "thresholdsStyle": {"mode": "off"}
                    },
                    "mappings": [],
                    "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]},
                    "unit": "ms"
                }
            },
            "gridPos": position or {"h": 8, "w": 12, "x": 0, "y": 0}
        }
        
        self.panel_id += 1
        return panel
    
    def create_heatmap_panel(self, title: str, query: str, position: Dict[str, int] = None) -> Dict[str, Any]:
        """Create a heatmap panel for availability visualization."""
        panel = {
            "id": self.panel_id,
            "title": title,
            "type": "heatmap",
            "targets": [{
                "refId": "A",
                "query": query,
                "datasource": {
                    "type": "influxdb",
                    "uid": "InfluxDB-Provider-CrossTenant"
                }
            }],
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {"hideFrom": {"legend": False, "tooltip": False, "vis": False}},
                    "mappings": [],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "red", "value": None},
                            {"color": "yellow", "value": 95},
                            {"color": "green", "value": 99}
                        ]
                    },
                    "unit": "percent"
                }
            },
            "gridPos": position or {"h": 8, "w": 12, "x": 0, "y": 0}
        }
        
        self.panel_id += 1
        return panel
    
    def create_gauge_panel(self, title: str, query: str, position: Dict[str, int] = None) -> Dict[str, Any]:
        """Create a gauge panel for capacity utilization."""
        panel = {
            "id": self.panel_id,
            "title": title,
            "type": "gauge",
            "targets": [{
                "refId": "A",
                "query": query,
                "datasource": {
                    "type": "influxdb",
                    "uid": "InfluxDB-Provider-CrossTenant"
                }
            }],
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "thresholds"},
                    "mappings": [],
                    "max": 100,
                    "min": 0,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "yellow", "value": 70},
                            {"color": "red", "value": 90}
                        ]
                    },
                    "unit": "percent"
                }
            },
            "gridPos": position or {"h": 8, "w": 6, "x": 0, "y": 0}
        }
        
        self.panel_id += 1
        return panel
    
    def create_template_variables(self) -> List[Dict[str, Any]]:
        """Create template variables for dashboard filtering."""
        return [
            {
                "current": {"selected": True, "text": "All", "value": "$__all"},
                "datasource": {"type": "influxdb", "uid": "InfluxDB-Provider-CrossTenant"},
                "definition": "from(bucket: \"qos_metrics\")\n  |> range(start: -1h)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> group(columns: [\"service_name\"])\n  |> distinct(column: \"service_name\")\n  |> yield(name: \"service_names\")",
                "hide": 0,
                "includeAll": True,
                "label": "Service",
                "multi": True,
                "name": "service_name",
                "options": [],
                "query": "from(bucket: \"qos_metrics\")\n  |> range(start: -1h)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> group(columns: [\"service_name\"])\n  |> distinct(column: \"service_name\")\n  |> yield(name: \"service_names\")",
                "refresh": 1,
                "regex": "",
                "skipUrlSync": False,
                "sort": 0,
                "type": "query"
            },
            {
                "current": {"selected": True, "text": "All", "value": "$__all"},
                "datasource": {"type": "influxdb", "uid": "InfluxDB-Provider-CrossTenant"},
                "definition": "from(bucket: \"qos_metrics\")\n  |> range(start: -1h)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> group(columns: [\"sla_tier\"])\n  |> distinct(column: \"sla_tier\")\n  |> yield(name: \"sla_tiers\")",
                "hide": 0,
                "includeAll": True,
                "multi": True,
                "name": "sla_tier",
                "options": [],
                "query": "from(bucket: \"qos_metrics\")\n  |> range(start: -1h)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> group(columns: [\"sla_tier\"])\n  |> distinct(column: \"sla_tier\")\n  |> yield(name: \"sla_tiers\")",
                "refresh": 1,
                "regex": "",
                "skipUrlSync": False,
                "sort": 0,
                "type": "query"
            }
        ]
    
    def generate_header_panels(self) -> List[Dict[str, Any]]:
        """Generate header section panels."""
        panels = []
        
        # System Status
        panels.append(self.create_stat_panel(
            title="System Status",
            query="from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"availability\")\n  |> group(columns: [\"tenant_id\", \"service_name\"])\n  |> mean()\n  |> group()\n  |> min()\n  |> yield(name: \"min_availability\")",
            unit="percent",
            thresholds={
                "steps": [
                    {"color": "red", "value": None},
                    {"color": "yellow", "value": 95},
                    {"color": "green", "value": 99}
                ]
            },
            position={"h": 8, "w": 6, "x": 0, "y": 0}
        ))
        
        # Total API Calls
        panels.append(self.create_stat_panel(
            title="Total API Calls",
            query="from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"throughput\")\n  |> group()\n  |> sum()\n  |> yield(name: \"total_calls\")",
            unit="short",
            position={"h": 8, "w": 6, "x": 6, "y": 0}
        ))
        
        # Active Tenants
        panels.append(self.create_stat_panel(
            title="Active Tenants",
            query="from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> group(columns: [\"tenant_id\"])\n  |> count()\n  |> yield(name: \"active_tenants\")",
            unit="none",
            position={"h": 8, "w": 6, "x": 12, "y": 0}
        ))
        
        # System Health Score
        panels.append(self.create_stat_panel(
            title="System Health Score",
            query="from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"availability\")\n  |> group()\n  |> mean()\n  |> yield(name: \"health_score\")",
            unit="percent",
            thresholds={
                "steps": [
                    {"color": "red", "value": None},
                    {"color": "yellow", "value": 95},
                    {"color": "green", "value": 99}
                ]
            },
            position={"h": 8, "w": 6, "x": 18, "y": 0}
        ))
        
        return panels
    
    def generate_performance_panels(self) -> List[Dict[str, Any]]:
        """Generate performance overview panels."""
        panels = []
        
        # Service Latency Trends
        latency_targets = [
            {
                "refId": "A",
                "query": "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"latency\")\n  |> filter(fn: (r) => contains(value: r[\"service_name\"], set: ${service_name:json}))\n  |> group(columns: [\"service_name\"])\n  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)\n  |> yield(name: \"mean\")",
                "datasource": {"type": "influxdb", "uid": "InfluxDB-Provider-CrossTenant"}
            },
            {
                "refId": "B",
                "query": "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"latency\")\n  |> filter(fn: (r) => contains(value: r[\"service_name\"], set: ${service_name:json}))\n  |> group(columns: [\"service_name\"])\n  |> aggregateWindow(every: v.windowPeriod, fn: quantile, createEmpty: false, q: 0.95)\n  |> yield(name: \"p95\")",
                "datasource": {"type": "influxdb", "uid": "InfluxDB-Provider-CrossTenant"}
            }
        ]
        
        panels.append(self.create_timeseries_panel(
            title="Service Latency Trends",
            targets=latency_targets,
            position={"h": 8, "w": 12, "x": 0, "y": 8}
        ))
        
        # Error Rate Trends
        error_targets = [{
            "refId": "A",
            "query": "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"error_rate\")\n  |> filter(fn: (r) => contains(value: r[\"service_name\"], set: ${service_name:json}))\n  |> group(columns: [\"service_name\"])\n  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)\n  |> yield(name: \"error_rate\")",
            "datasource": {"type": "influxdb", "uid": "InfluxDB-Provider-CrossTenant"}
        }]
        
        panels.append(self.create_timeseries_panel(
            title="Error Rate Trends",
            targets=error_targets,
            position={"h": 8, "w": 12, "x": 12, "y": 8}
        ))
        
        return panels
    
    def generate_capacity_panels(self) -> List[Dict[str, Any]]:
        """Generate capacity planning panels."""
        panels = []
        
        # Capacity Utilization
        panels.append(self.create_gauge_panel(
            title="Capacity Utilization",
            query="from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"throughput\")\n  |> group()\n  |> sum()\n  |> map(fn: (r) => ({r with _value: r._value / 1000.0}))\n  |> yield(name: \"capacity_utilization\")",
            position={"h": 8, "w": 6, "x": 0, "y": 24}
        ))
        
        # SLA Compliance
        panels.append(self.create_stat_panel(
            title="SLA Compliance",
            query="from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"availability\")\n  |> group(columns: [\"tenant_id\", \"service_name\", \"sla_tier\"])\n  |> mean()\n  |> filter(fn: (r) => r._value >= 99.0)\n  |> count()\n  |> yield(name: \"sla_compliant\")",
            unit="none",
            thresholds={
                "steps": [
                    {"color": "red", "value": None},
                    {"color": "green", "value": 1}
                ]
            },
            position={"h": 8, "w": 6, "x": 6, "y": 24}
        ))
        
        return panels
    
    def generate_dashboard(self) -> Dict[str, Any]:
        """Generate the complete dashboard configuration."""
        # Add all panels
        self.dashboard_config["dashboard"]["panels"].extend(self.generate_header_panels())
        self.dashboard_config["dashboard"]["panels"].extend(self.generate_performance_panels())
        
        # Add throughput and availability panels
        self.dashboard_config["dashboard"]["panels"].append(self.create_timeseries_panel(
            title="Throughput Patterns",
            targets=[{
                "refId": "A",
                "query": "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"throughput\")\n  |> filter(fn: (r) => contains(value: r[\"service_name\"], set: ${service_name:json}))\n  |> group(columns: [\"service_name\"])\n  |> aggregateWindow(every: v.windowPeriod, fn: sum, createEmpty: false)\n  |> yield(name: \"throughput\")",
                "datasource": {"type": "influxdb", "uid": "InfluxDB-Provider-CrossTenant"}
            }],
            position={"h": 8, "w": 12, "x": 0, "y": 16}
        ))
        
        self.dashboard_config["dashboard"]["panels"].append(self.create_heatmap_panel(
            title="Availability Heatmap",
            query="from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"availability\")\n  |> filter(fn: (r) => contains(value: r[\"service_name\"], set: ${service_name:json}))\n  |> group(columns: [\"service_name\", \"sla_tier\"])\n  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)\n  |> yield(name: \"availability\")",
            position={"h": 8, "w": 12, "x": 12, "y": 16}
        ))
        
        self.dashboard_config["dashboard"]["panels"].extend(self.generate_capacity_panels())
        
        # Add traffic growth trends
        self.dashboard_config["dashboard"]["panels"].append(self.create_timeseries_panel(
            title="Traffic Growth Trends",
            targets=[{
                "refId": "A",
                "query": "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"throughput\")\n  |> group(columns: [\"service_name\"])\n  |> aggregateWindow(every: 1h, fn: sum, createEmpty: false)\n  |> yield(name: \"hourly_traffic\")",
                "datasource": {"type": "influxdb", "uid": "InfluxDB-Provider-CrossTenant"}
            }],
            position={"h": 8, "w": 12, "x": 12, "y": 24}
        ))
        
        # Add template variables
        self.dashboard_config["dashboard"]["templating"]["list"] = self.create_template_variables()
        
        return self.dashboard_config
    
    def save_dashboard(self, filename: str = "bhashini-provider-overview.json") -> str:
        """Save the dashboard configuration to a file."""
        dashboard = self.generate_dashboard()
        output_path = self.output_dir / filename
        
        with open(output_path, 'w') as f:
            json.dump(dashboard, f, indent=2)
        
        return str(output_path)
    
    def validate_dashboard(self) -> bool:
        """Validate the generated dashboard configuration."""
        try:
            dashboard = self.generate_dashboard()
            
            # Basic validation
            required_keys = ["dashboard", "panels", "templating"]
            for key in required_keys:
                if key not in dashboard["dashboard"]:
                    print(f"Missing required key: {key}")
                    return False
            
            # Panel validation
            if not dashboard["dashboard"]["panels"]:
                print("No panels generated")
                return False
            
            print(f"Dashboard validation successful. Generated {len(dashboard['dashboard']['panels'])} panels.")
            return True
            
        except Exception as e:
            print(f"Dashboard validation failed: {e}")
            return False

def main():
    """Main function to generate the dashboard."""
    generator = DashboardGenerator()
    
    print("Generating Bhashini Provider Dashboard...")
    
    if generator.validate_dashboard():
        output_path = generator.save_dashboard()
        print(f"Dashboard saved to: {output_path}")
        print("Dashboard generation completed successfully!")
    else:
        print("Dashboard generation failed validation!")
        sys.exit(1)

if __name__ == "__main__":
    main()
