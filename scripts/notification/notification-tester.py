#!/usr/bin/env python3
"""
Notification Tester
Tests Slack and SMTP notifications for alerting system
"""

import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
import json

class NotificationTester:
    def __init__(self):
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.smtp_from_address = os.getenv('SMTP_FROM_ADDRESS')
        self.smtp_from_name = os.getenv('SMTP_FROM_NAME')
    
    def test_slack_notification(self, 
                               message: str, 
                               channel: str = "#bhashini-alerts",
                               username: str = "Bhashini Alerts",
                               icon_emoji: str = ":warning:") -> bool:
        """Test Slack notification via webhook"""
        if not self.slack_webhook_url:
            print("❌ SLACK_WEBHOOK_URL not configured")
            return False
        
        payload = {
            "text": message,
            "channel": channel,
            "username": username,
            "icon_emoji": icon_emoji
        }
        
        try:
            response = requests.post(
                self.slack_webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Slack notification sent successfully to {channel}")
                return True
            else:
                print(f"❌ Slack notification failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Slack notification error: {e}")
            return False
    
    def test_smtp_notification(self, 
                              to_address: str, 
                              subject: str, 
                              body: str) -> bool:
        """Test SMTP notification"""
        if not all([self.smtp_host, self.smtp_user, self.smtp_password]):
            print("❌ SMTP configuration incomplete")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.smtp_from_name} <{self.smtp_from_address}>"
            msg['To'] = to_address
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ SMTP notification sent successfully to {to_address}")
            return True
            
        except Exception as e:
            print(f"❌ SMTP notification error: {e}")
            return False
    
    def test_sla_violation_notification(self, 
                                       tenant_id: str, 
                                       sla_tier: str,
                                       metric: str,
                                       current_value: float,
                                       threshold: float) -> Dict:
        """Test SLA violation notification via both channels"""
        results = {}
        
        # Slack notification
        slack_message = f"🚨 SLA VIOLATION ALERT\n\n"
        slack_message += f"*Tenant:* {tenant_id}\n"
        slack_message += f"*SLA Tier:* {sla_tier}\n"
        slack_message += f"*Metric:* {metric}\n"
        slack_message += f"*Current Value:* {current_value}\n"
        slack_message += f"*Threshold:* {threshold}\n"
        slack_message += f"*Time:* {self._get_current_time()}"
        
        results['slack'] = self.test_slack_notification(
            message=slack_message,
            channel="#bhashini-alerts",
            icon_emoji=":rotating_light:"
        )
        
        # SMTP notification
        email_subject = f"SLA Violation Alert - {tenant_id}"
        email_body = f"""
SLA VIOLATION ALERT

Tenant: {tenant_id}
SLA Tier: {sla_tier}
Metric: {metric}
Current Value: {current_value}
Threshold: {threshold}
Time: {self._get_current_time()}

This is an automated alert from the Bhashini QoS monitoring system.
Please investigate the service performance for this tenant.
        """.strip()
        
        results['smtp'] = self.test_smtp_notification(
            to_address=os.getenv('PROVIDER_EMAIL_LIST', 'ops@example.com'),
            subject=email_subject,
            body=email_body
        )
        
        return results
    
    def test_incident_notification(self, 
                                  incident_id: str, 
                                  description: str, 
                                  severity: str = "high",
                                  services: list = None) -> Dict:
        """Test incident notification via both channels"""
        results = {}
        
        # Slack notification
        severity_emoji = {
            "critical": ":rotating_light:",
            "high": ":warning:",
            "medium": ":exclamation:",
            "low": ":information_source:"
        }
        
        slack_message = f"{severity_emoji.get(severity, ':warning:')} INCIDENT ALERT\n\n"
        slack_message += f"*Incident ID:* {incident_id}\n"
        slack_message += f"*Description:* {description}\n"
        slack_message += f"*Severity:* {severity.upper()}\n"
        if services:
            slack_message += f"*Affected Services:* {', '.join(services)}\n"
        slack_message += f"*Time:* {self._get_current_time()}"
        
        results['slack'] = self.test_slack_notification(
            message=slack_message,
            channel="#bhashini-alerts",
            icon_emoji=severity_emoji.get(severity, ':warning:')
        )
        
        # SMTP notification
        email_subject = f"Incident Alert - {incident_id} - {severity.upper()}"
        email_body = f"""
INCIDENT ALERT

Incident ID: {incident_id}
Description: {description}
Severity: {severity.upper()}
Affected Services: {', '.join(services) if services else 'All services'}
Time: {self._get_current_time()}

This is an automated incident alert from the Bhashini QoS monitoring system.
Please investigate and take appropriate action.
        """.strip()
        
        results['smtp'] = self.test_smtp_notification(
            to_address=os.getenv('PROVIDER_EMAIL_LIST', 'ops@example.com'),
            subject=email_subject,
            body=email_body
        )
        
        return results
    
    def test_maintenance_notification(self, 
                                    maintenance_id: str, 
                                    description: str,
                                    start_time: str,
                                    end_time: str,
                                    services: list = None) -> Dict:
        """Test maintenance notification via both channels"""
        results = {}
        
        # Slack notification
        slack_message = f"🔧 MAINTENANCE NOTIFICATION\n\n"
        slack_message += f"*Maintenance ID:* {maintenance_id}\n"
        slack_message += f"*Description:* {description}\n"
        slack_message += f"*Start Time:* {start_time}\n"
        slack_message += f"*End Time:* {end_time}\n"
        if services:
            slack_message += f"*Affected Services:* {', '.join(services)}\n"
        slack_message += f"*Notification Time:* {self._get_current_time()}"
        
        results['slack'] = self.test_slack_notification(
            message=slack_message,
            channel="#bhashini-alerts",
            icon_emoji=":tools:"
        )
        
        # SMTP notification
        email_subject = f"Maintenance Notification - {maintenance_id}"
        email_body = f"""
MAINTENANCE NOTIFICATION

Maintenance ID: {maintenance_id}
Description: {description}
Start Time: {start_time}
End Time: {end_time}
Affected Services: {', '.join(services) if services else 'All services'}
Notification Time: {self._get_current_time()}

This is a maintenance notification from the Bhashini QoS monitoring system.
Please plan accordingly for potential service disruptions.
        """.strip()
        
        results['smtp'] = self.test_smtp_notification(
            to_address=os.getenv('PROVIDER_EMAIL_LIST', 'ops@example.com'),
            subject=email_subject,
            body=email_body
        )
        
        return results
    
    def _get_current_time(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    def run_all_tests(self) -> Dict:
        """Run all notification tests"""
        print("🧪 Running notification tests...\n")
        
        results = {}
        
        # Test SLA violation
        print("1. Testing SLA violation notification...")
        results['sla_violation'] = self.test_sla_violation_notification(
            tenant_id="enterprise_1",
            sla_tier="premium",
            metric="availability",
            current_value=95.2,
            threshold=99.0
        )
        print()
        
        # Test incident notification
        print("2. Testing incident notification...")
        results['incident'] = self.test_incident_notification(
            incident_id="INC-001",
            description="High latency detected in TTS service",
            severity="high",
            services=["TTS", "ASR"]
        )
        print()
        
        # Test maintenance notification
        print("3. Testing maintenance notification...")
        results['maintenance'] = self.test_maintenance_notification(
            maintenance_id="MAINT-001",
            description="Scheduled database maintenance",
            start_time="2024-01-15 02:00:00 UTC",
            end_time="2024-01-15 04:00:00 UTC",
            services=["database"]
        )
        print()
        
        # Summary
        print("📊 Test Results Summary:")
        for test_name, test_results in results.items():
            slack_status = "✅" if test_results.get('slack') else "❌"
            smtp_status = "✅" if test_results.get('smtp') else "❌"
            print(f"  {test_name}: Slack {slack_status}, SMTP {smtp_status}")
        
        return results

def main():
    """Main function"""
    tester = NotificationTester()
    
    # Check configuration
    print("🔧 Notification Configuration:")
    print(f"  Slack Webhook: {'✅ Configured' if tester.slack_webhook_url else '❌ Not configured'}")
    print(f"  SMTP Host: {'✅ Configured' if tester.smtp_host else '❌ Not configured'}")
    print(f"  SMTP User: {'✅ Configured' if tester.smtp_user else '❌ Not configured'}")
    print(f"  SMTP Password: {'✅ Configured' if tester.smtp_password else '❌ Not configured'}")
    print()
    
    # Run tests
    results = tester.run_all_tests()
    
    # Exit with error code if any test failed
    all_passed = all(
        all(test_results.values()) 
        for test_results in results.values()
    )
    
    if all_passed:
        print("\n🎉 All notification tests passed!")
        exit(0)
    else:
        print("\n💥 Some notification tests failed!")
        exit(1)

if __name__ == '__main__':
    main()
