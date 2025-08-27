#!/usr/bin/env python3
"""
Grafana Heatmap Generator
Generates Heatmap panel JSON configurations for various metric types
"""

import json
from typing import Dict, List, Optional

class HeatmapPanelGenerator:
    def __init__(self):
        self.base_config = {
            "type": "heatmap",
            "fieldConfig": {
                "defaults": {
                    "color": {
                        "mode": "scheme"
                    },
                    "custom": {
                        "hideFrom": {
                            "legend": False,
                            "tooltip": False,
                            "vis": False
                        }
                    },
                    "mappings": [],
                    "unit": "short"
                }
            },
            "options": {
                "calculate": True,
                "calculation": {
                    "xBuckets": {
                        "mode": "size",
                        "value": "1"
                    },
                    "yBuckets": {
                        "mode": "size",
                        "value": "1"
                    }
                },
                "color": {
                    "exponent": 0.5,
                    "fill": "dark-orange",
                    "mode": "scheme",
                    "reverse": False,
                    "scale": "exponential",
                    "scheme": "Spectral",
                    "steps": 64
                },
                "exemplars": {
                    "color": "rgba(255,0,255,0.9)"
                },
                "legend": {
                    "show": True
                },
                "rowsFrame": {
                    "layout": "auto"
                },
                "tooltip": {
                    "show": True,
                    "yHistogram": False
                },
                "xAxis": {
                    "show": True,
                    "unit": "time"
                },
                "yAxis": {
                    "axisPlacement": "left",
                    "show": True,
                    "unit": "short"
                }
            }
        }
    
    def generate_latency_heatmap(self, 
                                title: str, 
                                datasource_uid: str,
                                tenant_id: Optional[str] = None,
                                service_filter: Optional[str] = None,
                                panel_id: int = 1,
                                grid_pos: Optional[Dict] = None) -> Dict:
        """Generate a latency heatmap panel configuration"""
        query = "from(bucket: \"qos_metrics\")\n"
        query += "  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n"
        query += "  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\" and r.metric_type == \"latency\")\n"
        
        if tenant_id:
            query += f"  |> filter(fn: (r) => r.tenant_id == \"{tenant_id}\")\n"
        
        if service_filter:
            query += f"  |> filter(fn: (r) => r.service_name =~ /{service_filter}/)\n"
        
        query += "  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)\n"
        query += "  |> pivot(rowKey:[\"_time\"], columnKey: [\"service_name\"], valueColumn: \"_value\")\n"
        query += "  |> yield(name: \"latency_heatmap\")"
        
        panel = self.base_config.copy()
        panel.update({
            "id": panel_id,
            "title": title,
            "targets": [
                {
                    "refId": "A",
                    "query": query,
                    "datasource": {
                        "type": "influxdb",
                        "uid": datasource_uid
                    }
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "color": {
                        "mode": "scheme"
                    },
                    "custom": {
                        "hideFrom": {
                            "legend": False,
                            "tooltip": False,
                            "vis": False
                        }
                    },
                    "mappings": [],
                    "unit": "ms"
                }
            }
        })
        
        if grid_pos:
            panel["gridPos"] = grid_pos
        
        return panel
    
    def generate_error_rate_heatmap(self, 
                                   title: str, 
                                   datasource_uid: str,
                                   tenant_id: Optional[str] = None,
                                   service_filter: Optional[str] = None,
                                   panel_id: int = 1,
                                   grid_pos: Optional[Dict] = None) -> Dict:
        """Generate an error rate heatmap panel configuration"""
        query = "from(bucket: \"qos_metrics\")\n"
        query += "  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n"
        query += "  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\" and r.metric_type == \"error_rate\")\n"
        
        if tenant_id:
            query += f"  |> filter(fn: (r) => r.tenant_id == \"{tenant_id}\")\n"
        
        if service_filter:
            query += f"  |> filter(fn: (r) => r.service_name =~ /{service_filter}/)\n"
        
        query += "  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)\n"
        query += "  |> pivot(rowKey:[\"_time\"], columnKey: [\"service_name\"], valueColumn: \"_value\")\n"
        query += "  |> yield(name: \"error_rate_heatmap\")"
        
        panel = self.base_config.copy()
        panel.update({
            "id": panel_id,
            "title": title,
            "targets": [
                {
                    "refId": "A",
                    "query": query,
                    "datasource": {
                        "type": "influxdb",
                        "uid": datasource_uid
                    }
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "color": {
                        "mode": "scheme"
                    },
                    "custom": {
                        "hideFrom": {
                            "legend": False,
                            "tooltip": False,
                            "vis": false
                        }
                    },
                    "mappings": [],
                    "unit": "percent"
                }
            }
        })
        
        if grid_pos:
            panel["gridPos"] = grid_pos
        
        return panel
    
    def generate_availability_heatmap(self, 
                                     title: str, 
                                     datasource_uid: str,
                                     tenant_id: Optional[str] = None,
                                     service_filter: Optional[str] = None,
                                     panel_id: int = 1,
                                     grid_pos: Optional[Dict] = None) -> Dict:
        """Generate an availability heatmap panel configuration"""
        query = "from(bucket: \"qos_metrics\")\n"
        query += "  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n"
        query += "  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\" and r.metric_type == \"availability\")\n"
        
        if tenant_id:
            query += f"  |> filter(fn: (r) => r.tenant_id == \"{tenant_id}\")\n"
        
        if service_filter:
            query += f"  |> filter(fn: (r) => r.service_name =~ /{service_filter}/)\n"
        
        query += "  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)\n"
        query += "  |> map(fn: (r) => ({ r with _value: r._value * 100.0 }))\n"
        query += "  |> pivot(rowKey:[\"_time\"], columnKey: [\"service_name\"], valueColumn: \"_value\")\n"
        query += "  |> yield(name: \"availability_heatmap\")"
        
        panel = self.base_config.copy()
        panel.update({
            "id": panel_id,
            "title": title,
            "targets": [
                {
                    "refId": "A",
                    "query": query,
                    "datasource": {
                        "type": "influxdb",
                        "uid": datasource_uid
                    }
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "color": {
                        "mode": "scheme"
                    },
                    "custom": {
                        "hideFrom": {
                            "legend": False,
                            "tooltip": False,
                            "vis": False
                        }
                    },
                    "mappings": [],
                    "unit": "percent"
                }
            }
        })
        
        if grid_pos:
            panel["gridPos"] = grid_pos
        
        return panel
    
    def generate_custom_heatmap(self, 
                               title: str, 
                               query: str, 
                               datasource_uid: str,
                               unit: str = "short",
                               panel_id: int = 1,
                               grid_pos: Optional[Dict] = None) -> Dict:
        """Generate a custom heatmap panel configuration"""
        panel = self.base_config.copy()
        panel.update({
            "id": panel_id,
            "title": title,
            "targets": [
                {
                    "refId": "A",
                    "query": query,
                    "datasource": {
                        "type": "influxdb",
                        "uid": datasource_uid
                    }
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "color": {
                        "mode": "scheme"
                    },
                    "custom": {
                        "hideFrom": {
                            "legend": False,
                            "tooltip": False,
                            "vis": False
                        }
                    },
                    "mappings": [],
                    "unit": unit
                }
            }
        })
        
        if grid_pos:
            panel["gridPos"] = grid_pos
        
        return panel

def main():
    """Example usage"""
    generator = HeatmapPanelGenerator()
    
    # Generate latency heatmap for provider dashboard
    latency_panel = generator.generate_latency_heatmap(
        title="Latency Heatmap by Service",
        datasource_uid="InfluxDB-Provider-CrossTenant",
        panel_id=15,
        grid_pos={"h": 8, "w": 12, "x": 0, "y": 56}
    )
    
    # Generate error rate heatmap for provider dashboard
    error_panel = generator.generate_error_rate_heatmap(
        title="Error Rate Heatmap by Service",
        datasource_uid="InfluxDB-Provider-CrossTenant",
        panel_id=16,
        grid_pos={"h": 8, "w": 12, "x": 12, "y": 56}
    )
    
    # Generate availability heatmap for customer dashboard
    availability_panel = generator.generate_availability_heatmap(
        title="Availability Heatmap by Service",
        datasource_uid="InfluxDB-Customer-enterprise_1",
        tenant_id="enterprise_1",
        panel_id=15,
        grid_pos={"h": 8, "w": 12, "x": 0, "y": 48}
    )
    
    # Print generated configurations
    print("Latency Heatmap Panel:")
    print(json.dumps(latency_panel, indent=2))
    print("\nError Rate Heatmap Panel:")
    print(json.dumps(error_panel, indent=2))
    print("\nAvailability Heatmap Panel:")
    print(json.dumps(availability_panel, indent=2))

if __name__ == '__main__':
    main()
