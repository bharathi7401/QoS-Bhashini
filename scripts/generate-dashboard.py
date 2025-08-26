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
        
        # Dashboard configuration - removed wrapper structure
        self.dashboard_config = {
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
        
        # Panel counter
        self.panel_id = 1
        
        # Load Flux queries from template file
        self.flux_queries = self.load_flux_queries()
        
    def load_flux_queries(self) -> Dict[str, str]:
        """Load Flux queries from the provider-queries.flux file."""
        queries = {}
        queries_file = Path("scripts/dashboard-queries/provider-queries.flux")
        
        if not queries_file.exists():
            print(f"Warning: Flux queries file not found: {queries_file}")
            return queries
        
        try:
            with open(queries_file, 'r') as f:
                content = f.read()
            
            # Split content into sections and extract function definitions
            sections = content.split('// =============================================================================')
            
            for section in sections:
                if not section.strip():
                    continue
                    
                lines = section.split('\n')
                current_function = None
                current_query = []
                
                for line in lines:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if line.startswith('//') or not line:
                        continue
                    
                    # Check for function definition
                    if '=' in line and '=>' in line:
                        # Save previous function if exists
                        if current_function and current_query:
                            queries[current_function] = '\n  '.join(current_query)
                        
                        # Start new function
                        func_name = line.split('=')[0].strip()
                        current_function = func_name
                        current_query = []
                    elif current_function and line:
                        # Add line to current query
                        current_query.append(line)
                
                # Save last function in section
                if current_function and current_query:
                    queries[current_function] = '\n  '.join(current_query)
                
            print(f"Loaded {len(queries)} Flux query templates: {list(queries.keys())}")
            
        except Exception as e:
            print(f"Error loading Flux queries: {e}")
            
        return queries
    
    def get_flux_query(self, query_name: str, fallback: str = "") -> str:
        """Get a Flux query by name from the loaded templates."""
        if query_name in self.flux_queries:
            return self.flux_queries[query_name]
        elif fallback:
            print(f"Warning: Query template '{query_name}' not found, using fallback")
            return fallback
        else:
            print(f"Error: Query template '{query_name}' not found and no fallback provided")
            return ""
        
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
        
        # System Status - using template query
        system_availability_query = self.get_flux_query(
            "system_availability",
            "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"availability\")\n  |> filter(fn: (r) => r[\"_field\"] == \"value\")\n  |> group(columns: [\"tenant_id\", \"service_name\"])\n  |> mean()\n  |> group()\n  |> min()\n  |> yield(name: \"min_availability\")"
        )
        
        panels.append(self.create_stat_panel(
            title="System Status",
            query=system_availability_query,
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
        
        # Total API Calls - using template query
        total_api_calls_query = self.get_flux_query(
            "total_api_calls",
            "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"throughput\")\n  |> filter(fn: (r) => r[\"_field\"] == \"value\")\n  |> group()\n  |> sum()\n  |> yield(name: \"total_calls\")"
        )
        
        panels.append(self.create_stat_panel(
            title="Total API Calls",
            query=total_api_calls_query,
            unit="short",
            position={"h": 8, "w": 6, "x": 6, "y": 0}
        ))
        
        # Active Tenants - fixed query
        panels.append(self.create_stat_panel(
            title="Active Tenants",
            query="from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"_field\"] == \"value\")\n  |> distinct(column: \"tenant_id\")\n  |> count()\n  |> yield(name: \"active_tenants\")",
            unit="none",
            position={"h": 8, "w": 6, "x": 12, "y": 0}
        ))
        
        # System Health Score - using template query
        system_health_query = self.get_flux_query(
            "system_availability",
            "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"availability\")\n  |> filter(fn: (r) => r[\"_field\"] == \"value\")\n  |> group()\n  |> mean()\n  |> yield(name: \"health_score\")"
        )
        
        panels.append(self.create_stat_panel(
            title="System Health Score",
            query=system_health_query,
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
        
        # Average Response Time - using template query
        avg_response_query = self.get_flux_query(
            "weighted_avg_latency",
            "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"_field\"] == \"value\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"latency\")\n  |> filter(fn: (r) => array.contains(value: \"All\", set: ${service_name:json}) or array.contains(value: r[\"service_name\"], set: ${service_name:json}))\n  |> filter(fn: (r) => array.contains(value: \"All\", set: ${sla_tier:json}) or array.contains(value: r[\"sla_tier\"], set: ${sla_tier:json}))\n  |> group()\n  |> mean()\n  |> yield(name: \"avg_response_time\")"
        )
        
        panels.append(self.create_stat_panel(
            title="Average Response Time",
            query=avg_response_query,
            unit="ms",
            thresholds={
                "steps": [
                    {"color": "green", "value": None},
                    {"color": "yellow", "value": 100},
                    {"color": "red", "value": 200}
                ]
            },
            position={"h": 8, "w": 6, "x": 0, "y": 8}
        ))
        
        # Overall Error Rate - using template query
        overall_error_query = self.get_flux_query(
            "overall_error_rate",
            "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"_field\"] == \"value\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"error_rate\")\n  |> filter(fn: (r) => array.contains(value: \"All\", set: ${service_name:json}) or array.contains(value: r[\"service_name\"], set: ${service_name:json}))\n  |> filter(fn: (r) => array.contains(value: \"All\", set: ${sla_tier:json}) or array.contains(value: r[\"sla_tier\"], set: ${sla_tier:json}))\n  |> group()\n  |> mean()\n  |> yield(name: \"overall_error_rate\")"
        )
        
        panels.append(self.create_stat_panel(
            title="Overall Error Rate",
            query=overall_error_query,
            unit="percent",
            thresholds={
                "steps": [
                    {"color": "green", "value": None},
                    {"color": "yellow", "value": 1},
                    {"color": "red", "value": 5}
                ]
            },
            position={"h": 8, "w": 6, "x": 6, "y": 8}
        ))
        
        # Service Latency Trends with P50, P95, P99
        latency_targets = [
            {
                "refId": "A",
                "query": "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"_field\"] == \"value\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"latency\")\n  |> filter(fn: (r) => array.contains(value: \"All\", set: ${service_name:json}) or array.contains(value: r[\"service_name\"], set: ${service_name:json}))\n  |> filter(fn: (r) => array.contains(value: \"All\", set: ${sla_tier:json}) or array.contains(value: r[\"sla_tier\"], set: ${sla_tier:json}))\n  |> group(columns: [\"service_name\"])\n  |> aggregateWindow(every: v.windowPeriod, fn: quantile, createEmpty: false, q: 0.50)\n  |> yield(name: \"p50\")",
                "datasource": {"type": "influxdb", "uid": "InfluxDB-Provider-CrossTenant"}
            },
            {
                "refId": "B",
                "query": "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"_field\"] == \"value\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"latency\")\n  |> filter(fn: (r) => array.contains(value: \"All\", set: ${service_name:json}) or array.contains(value: r[\"service_name\"], set: ${service_name:json}))\n  |> filter(fn: (r) => array.contains(value: \"All\", set: ${sla_tier:json}) or array.contains(value: r[\"sla_tier\"], set: ${sla_tier:json}))\n  |> group(columns: [\"service_name\"])\n  |> aggregateWindow(every: v.windowPeriod, fn: quantile, createEmpty: false, q: 0.95)\n  |> yield(name: \"p95\")",
                "datasource": {"type": "influxdb", "uid": "InfluxDB-Provider-CrossTenant"}
            },
            {
                "refId": "C",
                "query": "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"_field\"] == \"value\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"latency\")\n  |> filter(fn: (r) => array.contains(value: \"All\", set: ${service_name:json}) or array.contains(value: r[\"service_name\"], set: ${service_name:json}))\n  |> filter(fn: (r) => array.contains(value: \"All\", set: ${sla_tier:json}) or array.contains(value: r[\"sla_tier\"], set: ${sla_tier:json}))\n  |> group(columns: [\"service_name\"])\n  |> aggregateWindow(every: v.windowPeriod, fn: quantile, createEmpty: false, q: 0.99)\n  |> yield(name: \"p99\")",
                "datasource": {"type": "influxdb", "uid": "InfluxDB-Provider-CrossTenant"}
            }
        ]
        
        panels.append(self.create_timeseries_panel(
            title="Service Latency Trends",
            targets=latency_targets,
            position={"h": 8, "w": 12, "x": 0, "y": 16}
        ))
        
        return panels
    
    def generate_capacity_panels(self) -> List[Dict[str, Any]]:
        """Generate capacity planning panels."""
        panels = []
        
        # Capacity Utilization - using template query
        capacity_query = self.get_flux_query(
            "capacity_utilization",
            "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"_field\"] == \"value\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"throughput\")\n  |> group()\n  |> sum()\n  |> map(fn: (r) => ({r with _value: r._value / 1000.0}))\n  |> yield(name: \"capacity_utilization\")"
        )
        
        panels.append(self.create_gauge_panel(
            title="Capacity Utilization",
            query=capacity_query,
            position={"h": 8, "w": 6, "x": 0, "y": 40}
        ))
        
        # SLA Compliance - using template query
        sla_compliance_query = self.get_flux_query(
            "sla_compliance_tracking",
            "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"_field\"] == \"value\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"availability\")\n  |> group(columns: [\"tenant_id\", \"service_name\", \"sla_tier\"])\n  |> mean()\n  |> filter(fn: (r) => r._value >= 99.0)\n  |> count()\n  |> yield(name: \"sla_compliant\")"
        )
        
        panels.append(self.create_stat_panel(
            title="SLA Compliance",
            query=sla_compliance_query,
            unit="none",
            thresholds={
                "steps": [
                    {"color": "red", "value": None},
                    {"color": "green", "value": 1}
                ]
            },
            position={"h": 8, "w": 6, "x": 6, "y": 40}
        ))
        
        return panels
    
    def generate_dashboard(self) -> Dict[str, Any]:
        """Generate the complete dashboard configuration."""
        # Add all panels
        self.dashboard_config["panels"].extend(self.generate_header_panels())
        self.dashboard_config["panels"].extend(self.generate_performance_panels())
        
        # Add throughput and availability panels
        throughput_query = self.get_flux_query(
            "service_throughput_patterns",
            "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"_field\"] == \"value\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"throughput\")\n  |> filter(fn: (r) => array.contains(value: \"All\", set: ${service_name:json}) or array.contains(value: r[\"service_name\"], set: ${service_name:json}))\n  |> group(columns: [\"service_name\"])\n  |> aggregateWindow(every: v.windowPeriod, fn: sum, createEmpty: false)\n  |> yield(name: \"throughput\")"
        )
        
        self.dashboard_config["panels"].append(self.create_timeseries_panel(
            title="Throughput Patterns",
            targets=[{
                "refId": "A",
                "query": throughput_query,
                "datasource": {"type": "influxdb", "uid": "InfluxDB-Provider-CrossTenant"}
            }],
            position={"h": 8, "w": 12, "x": 0, "y": 24}
        ))
        
        availability_query = self.get_flux_query(
            "service_availability_tracking",
            "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"_field\"] == \"value\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"availability\")\n  |> filter(fn: (r) => array.contains(value: \"All\", set: ${service_name:json}) or array.contains(value: r[\"service_name\"], set: ${service_name:json}))\n  |> filter(fn: (r) => array.contains(value: \"All\", set: ${sla_tier:json}) or array.contains(value: r[\"sla_tier\"], set: ${sla_tier:json}))\n  |> group(columns: [\"service_name\", \"sla_tier\"])\n  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)\n  |> yield(name: \"availability\")"
        )
        
        self.dashboard_config["panels"].append(self.create_heatmap_panel(
            title="Availability Heatmap",
            query=availability_query,
            position={"h": 8, "w": 12, "x": 12, "y": 24}
        ))
        
        self.dashboard_config["panels"].extend(self.generate_capacity_panels())
        
        # Add traffic growth trends
        traffic_growth_query = self.get_flux_query(
            "traffic_growth_rate",
            "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"_field\"] == \"value\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"throughput\")\n  |> group(columns: [\"service_name\"])\n  |> aggregateWindow(every: 1h, fn: sum, createEmpty: false)\n  |> yield(name: \"hourly_traffic\")"
        )
        
        self.dashboard_config["panels"].append(self.create_timeseries_panel(
            title="Traffic Growth Trends",
            targets=[{
                "refId": "A",
                "query": traffic_growth_query,
                "datasource": {"type": "influxdb", "uid": "InfluxDB-Provider-CrossTenant"}
            }],
            position={"h": 8, "w": 12, "x": 12, "y": 40}
        ))
        
        # Add capacity planning panels
        peak_traffic_query = self.get_flux_query(
            "peak_traffic_analysis",
            "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"_field\"] == \"value\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"throughput\")\n  |> filter(fn: (r) => array.contains(value: \"All\", set: ${service_name:json}) or array.contains(value: r[\"service_name\"], set: ${service_name:json}))\n  |> filter(fn: (r) => array.contains(value: \"All\", set: ${sla_tier:json}) or array.contains(value: r[\"sla_tier\"], set: ${sla_tier:json}))\n  |> group(columns: [\"service_name\"])\n  |> aggregateWindow(every: 15m, fn: sum, createEmpty: false)\n  |> group()\n  |> max()\n  |> yield(name: \"peak_traffic\")"
        )
        
        self.dashboard_config["panels"].append(self.create_timeseries_panel(
            title="Peak Traffic Analysis",
            targets=[{
                "refId": "A",
                "query": peak_traffic_query,
                "datasource": {"type": "influxdb", "uid": "InfluxDB-Provider-CrossTenant"}
            }],
            position={"h": 8, "w": 12, "x": 0, "y": 48}
        ))
        
        resource_allocation_query = self.get_flux_query(
            "resource_allocation_by_service",
            "from(bucket: \"qos_metrics\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\")\n  |> filter(fn: (r) => r[\"_field\"] == \"value\")\n  |> filter(fn: (r) => r[\"metric_type\"] == \"throughput\")\n  |> filter(fn: (r) => array.contains(value: \"All\", set: ${service_name:json}) or array.contains(value: r[\"service_name\"], set: ${service_name:json}))\n  |> filter(fn: (r) => array.contains(value: \"All\", set: ${sla_tier:json}) or array.contains(value: r[\"sla_tier\"], set: ${sla_tier:json}))\n  |> group(columns: [\"service_name\"])\n  |> sum()\n  |> yield(name: \"service_allocation\")"
        )
        
        self.dashboard_config["panels"].append(self.create_timeseries_panel(
            title="Resource Allocation by Service",
            targets=[{
                "refId": "A",
                "query": resource_allocation_query,
                "datasource": {"type": "influxdb", "uid": "InfluxDB-Provider-CrossTenant"}
            }],
            position={"h": 8, "w": 12, "x": 12, "y": 48}
        ))
        
        # Add template variables
        self.dashboard_config["templating"]["list"] = self.create_template_variables()
        
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
            
            # Basic validation - removed dashboard wrapper check
            required_keys = ["title", "panels", "templating", "uid"]
            for key in required_keys:
                if key not in dashboard:
                    print(f"Missing required key: {key}")
                    return False
            
            # Panel validation
            if not dashboard["panels"]:
                print("No panels generated")
                return False
            
            print(f"Dashboard validation successful. Generated {len(dashboard['panels'])} panels.")
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
