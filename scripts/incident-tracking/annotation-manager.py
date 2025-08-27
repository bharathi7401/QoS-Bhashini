#!/usr/bin/env python3
"""
Grafana Annotation Manager
Manages annotations via Grafana API for incident tracking and maintenance windows
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class GrafanaAnnotationManager:
    def __init__(self, grafana_url: str, api_key: str):
        self.grafana_url = grafana_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_annotation(self, 
                         text: str, 
                         tags: List[str], 
                         time_start: Optional[datetime] = None,
                         time_end: Optional[datetime] = None,
                         dashboard_uid: Optional[str] = None,
                         panel_id: Optional[int] = None) -> Dict:
        """Create a new annotation"""
        payload = {
            'text': text,
            'tags': tags,
            'time': int(time_start.timestamp() * 1000) if time_start else int(datetime.now().timestamp() * 1000)
        }
        
        if time_end:
            payload['timeEnd'] = int(time_end.timestamp() * 1000)
        
        if dashboard_uid:
            payload['dashboardUID'] = dashboard_uid
        
        if panel_id:
            payload['panelId'] = panel_id
        
        response = requests.post(
            f'{self.grafana_url}/api/annotations',
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_annotations(self, 
                       time_from: Optional[datetime] = None,
                       time_to: Optional[datetime] = None,
                       tags: Optional[List[str]] = None,
                       dashboard_uid: Optional[str] = None) -> List[Dict]:
        """Get annotations with optional filtering"""
        params = {}
        
        if time_from:
            params['from'] = int(time_from.timestamp() * 1000)
        if time_to:
            params['to'] = int(time_to.timestamp() * 1000)
        if tags:
            params['tags'] = ','.join(tags)
        if dashboard_uid:
            params['dashboardUID'] = dashboard_uid
        
        response = requests.get(
            f'{self.grafana_url}/api/annotations',
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def delete_annotation(self, annotation_id: int) -> bool:
        """Delete an annotation by ID"""
        response = requests.delete(
            f'{self.grafana_url}/api/annotations/{annotation_id}',
            headers=self.headers
        )
        return response.status_code == 200
    
    def create_incident_annotation(self, 
                                  incident_id: str, 
                                  description: str, 
                                  severity: str = 'medium',
                                  services: List[str] = None) -> Dict:
        """Create an incident annotation with standardized tags"""
        tags = ['incident', f'severity:{severity}', f'incident_id:{incident_id}']
        if services:
            tags.extend([f'service:{service}' for service in services])
        
        return self.create_annotation(
            text=f"INCIDENT {incident_id}: {description}",
            tags=tags
        )
    
    def create_maintenance_annotation(self, 
                                    maintenance_id: str, 
                                    description: str,
                                    time_start: datetime,
                                    time_end: datetime,
                                    services: List[str] = None) -> Dict:
        """Create a maintenance window annotation"""
        tags = ['maintenance', f'maintenance_id:{maintenance_id}']
        if services:
            tags.extend([f'service:{service}' for service in services])
        
        return self.create_annotation(
            text=f"MAINTENANCE {maintenance_id}: {description}",
            tags=tags,
            time_start=time_start,
            time_end=time_end
        )

def main():
    """Example usage"""
    # Load configuration from environment
    grafana_url = os.getenv('GRAFANA_URL', 'http://localhost:3000')
    api_key = os.getenv('GRAFANA_API_KEY', 'admin')
    
    # Initialize manager
    manager = GrafanaAnnotationManager(grafana_url, api_key)
    
    # Example: Create an incident annotation
    try:
        incident = manager.create_incident_annotation(
            incident_id="INC-001",
            description="High latency detected in TTS service",
            severity="high",
            services=["TTS"]
        )
        print(f"Created incident annotation: {incident}")
        
        # Example: Create a maintenance annotation
        now = datetime.now()
        maintenance = manager.create_maintenance_annotation(
            maintenance_id="MAINT-001",
            description="Scheduled database maintenance",
            time_start=now + timedelta(hours=1),
            time_end=now + timedelta(hours=3),
            services=["database"]
        )
        print(f"Created maintenance annotation: {maintenance}")
        
        # Get recent annotations
        recent = manager.get_annotations(
            time_from=datetime.now() - timedelta(hours=24),
            tags=['incident', 'maintenance']
        )
        print(f"Found {len(recent)} recent annotations")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
