#!/usr/bin/env python3
"""
Grafana Alert Manager
Manages alert rules via Grafana API for SLA monitoring and alerting
"""

import requests
import json
import os
from typing import Dict, List, Optional

class GrafanaAlertManager:
    def __init__(self, grafana_url: str, api_key: str):
        self.grafana_url = grafana_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_alert_rule(self, 
                          name: str, 
                          condition: str, 
                          data: List[Dict],
                          interval: str = "10s",
                          labels: Optional[Dict] = None,
                          annotations: Optional[Dict] = None) -> Dict:
        """Create a new alert rule"""
        payload = {
            'rule_group': {
                'name': 'SLA Rules',
                'interval_seconds': 10,
                'rules': [
                    {
                        'grafana_alert': {
                            'title': name,
                            'condition': condition,
                            'data': data,
                            'no_data_state': 'NoData',
                            'exec_err_state': 'Error'
                        },
                        'for': '0s',
                        'annotations': annotations or {},
                        'labels': labels or {}
                    }
                ]
            }
        }
        
        response = requests.post(
            f'{self.grafana_url}/api/ruler/grafana/api/v1/rules/SLA%20Rules',
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_alert_rules(self) -> List[Dict]:
        """Get all alert rules"""
        response = requests.get(
            f'{self.grafana_url}/api/ruler/grafana/api/v1/rules',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def delete_alert_rule(self, rule_name: str) -> bool:
        """Delete an alert rule by name"""
        response = requests.delete(
            f'{self.grafana_url}/api/ruler/grafana/api/v1/rules/SLA%20Rules/{rule_name}',
            headers=self.headers
        )
        return response.status_code == 200
    
    def create_sla_availability_rule(self, 
                                   tenant_id: str, 
                                   sla_tier: str,
                                   threshold: float = 99.0) -> Dict:
        """Create an SLA availability alert rule"""
        data = [
            {
                "refId": "A",
                "queryType": "",
                "relativeTimeRange": {
                    "from": 600,
                    "to": 0
                },
                "datasourceUid": f"InfluxDB-Customer-{tenant_id}",
                "model": {
                    "query": f"from(bucket: \"qos_metrics\")\n  |> range(start: -5m)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\" and r.metric_type == \"availability\" and r.tenant_id == \"{tenant_id}\")\n  |> group()\n  |> mean()\n  |> map(fn: (r) => ({{r with _value: r._value * 100.0}}))\n  |> last()",
                    "refId": "A"
                }
            }
        ]
        
        condition = f"B"
        
        labels = {
            'alert_type': 'sla_violation',
            'sla_tier': sla_tier,
            'tenant_id': tenant_id,
            'metric': 'availability'
        }
        
        annotations = {
            'summary': f'SLA violation for {tenant_id} - Availability below {threshold}%',
            'description': f'Service availability for tenant {tenant_id} has dropped below the {threshold}% SLA threshold',
            'severity': 'critical'
        }
        
        return self.create_alert_rule(
            name=f"SLA Availability - {tenant_id}",
            condition=condition,
            data=data,
            labels=labels,
            annotations=annotations
        )
    
    def create_latency_rule(self, 
                           tenant_id: str, 
                           service_name: str,
                           threshold_ms: int = 500) -> Dict:
        """Create a latency alert rule"""
        data = [
            {
                "refId": "A",
                "queryType": "",
                "relativeTimeRange": {
                    "from": 600,
                    "to": 0
                },
                "datasourceUid": f"InfluxDB-Customer-{tenant_id}",
                "model": {
                    "query": f"from(bucket: \"qos_metrics\")\n  |> range(start: -5m)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"qos_metrics\" and r.metric_type == \"latency\" and r.tenant_id == \"{tenant_id}\" and r.service_name == \"{service_name}\")\n  |> group()\n  |> mean()\n  |> last()",
                    "refId": "A"
                }
            }
        ]
        
        condition = f"B"
        
        labels = {
            'alert_type': 'latency_violation',
            'service_name': service_name,
            'tenant_id': tenant_id,
            'metric': 'latency'
        }
        
        annotations = {
            'summary': f'High latency for {service_name} service - {tenant_id}',
            'description': f'Service {service_name} for tenant {tenant_id} has exceeded {threshold_ms}ms latency threshold',
            'severity': 'warning'
        }
        
        return self.create_alert_rule(
            name=f"Latency Alert - {service_name} - {tenant_id}",
            condition=condition,
            data=data,
            labels=labels,
            annotations=annotations
        )

def main():
    """Example usage"""
    # Load configuration from environment
    grafana_url = os.getenv('GRAFANA_URL', 'http://localhost:3000')
    api_key = os.getenv('GRAFANA_API_KEY', 'admin')
    
    # Initialize manager
    manager = GrafanaAlertManager(grafana_url, api_key)
    
    try:
        # Example: Create SLA availability rule for a tenant
        sla_rule = manager.create_sla_availability_rule(
            tenant_id="enterprise_1",
            sla_tier="premium",
            threshold=99.5
        )
        print(f"Created SLA rule: {sla_rule}")
        
        # Example: Create latency rule for TTS service
        latency_rule = manager.create_latency_rule(
            tenant_id="enterprise_1",
            service_name="TTS",
            threshold_ms=300
        )
        print(f"Created latency rule: {latency_rule}")
        
        # Get all alert rules
        rules = manager.get_alert_rules()
        print(f"Found {len(rules)} alert rule groups")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
