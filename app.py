#!/usr/bin/env python3
"""
Bhashini QoS Dashboards - Full Stack Fly.io Deployment
Flask app serving the public dashboard with links to Grafana
"""

from flask import Flask, render_template_string, send_from_directory
import os

app = Flask(__name__)

# HTML template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bhashini QoS Dashboards - Full Stack Monitoring</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 3rem;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }
        .dashboard-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .dashboard-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .dashboard-card h3 {
            margin: 0 0 15px 0;
            color: #fff;
            font-size: 1.5rem;
        }
        .dashboard-card p {
            margin: 0 0 20px 0;
            opacity: 0.9;
            line-height: 1.6;
        }
        .dashboard-card a {
            display: inline-block;
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            text-decoration: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .dashboard-card a:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .status {
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background: rgba(76, 175, 80, 0.2);
            border-radius: 10px;
            border: 1px solid rgba(76, 175, 80, 0.3);
        }
        .status h3 {
            margin: 0;
            color: #4caf50;
        }
        .service-links {
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
        }
        .service-links h3 {
            margin: 0 0 20px 0;
            color: #fff;
        }
        .service-links a {
            display: inline-block;
            margin: 10px;
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            text-decoration: none;
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        .service-links a:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Bhashini QoS Monitoring</h1>
            <p>Full Stack Monitoring System - Grafana + InfluxDB + BI Engine</p>
        </div>
        
        <div class="status">
            <h3>✅ Full Stack Deployed on Fly.io</h3>
            <p>Complete monitoring system with real-time dashboards, metrics, and business intelligence!</p>
        </div>

        <div class="status" style="background: rgba(255, 193, 7, 0.2); border-color: rgba(255, 193, 7, 0.3);">
            <h3>🆕 NEW: Ultimate QoS Overview Dashboard</h3>
            <p><strong>Important:</strong> Use the NEW dashboard below (not the old localhost:3010 one). This dashboard has 9 panels with real-time data!</p>
        </div>

        <div class="dashboard-grid">
            <div class="dashboard-card" style="border: 2px solid #4caf50; background: rgba(76, 175, 80, 0.1);">
                <h3>🏢 Ultimate QoS Overview (NEW!)</h3>
                <p><strong>9 Panels:</strong> System Status, API Calls, Active Tenants, Response Time, Error Rate, SLA Compliance, Peak Throughput, Service Count, and more!</p>
                <a href="/grafana/d/bhashini-ultimate-overview/bhashini-ultimate-overview" target="_blank" style="background: linear-gradient(45deg, #4caf50, #45a049);">🚀 View NEW Dashboard</a>
            </div>
            
            <div class="dashboard-card">
                <h3>🏥 Healthcare Dashboard</h3>
                <p>Healthcare sector specific metrics for ASR, Translation, and TTS services with performance monitoring.</p>
                <a href="/grafana/dashboards" target="_blank">Browse Healthcare Dashboards</a>
            </div>
            
            <div class="dashboard-card">
                <h3>🎓 Education Dashboard</h3>
                <p>Education sector monitoring with SLA compliance tracking and performance metrics for learning services.</p>
                <a href="/grafana/dashboards" target="_blank">Browse Education Dashboards</a>
            </div>
            
            <div class="dashboard-card">
                <h3>🏛️ Government Dashboard</h3>
                <p>Government sector metrics for public service applications with compliance and performance tracking.</p>
                <a href="/grafana/dashboards" target="_blank">Browse Government Dashboards</a>
            </div>
            
            <div class="dashboard-card">
                <h3>🚨 Customer Alerts</h3>
                <p>SLA monitoring and alerting system for different customer tiers and performance thresholds.</p>
                <a href="/grafana/alerting" target="_blank">View Alerts</a>
            </div>
            
            <div class="dashboard-card">
                <h3>🔧 Admin Access</h3>
                <p>Grafana administration panel for managing dashboards, users, and system configuration.</p>
                <a href="/grafana" target="_blank">Admin Panel</a>
            </div>
        </div>
        
        <div class="service-links">
            <h3>🔗 Service Access Links</h3>
            <a href="/grafana" target="_blank">📊 Grafana Dashboards</a>
            <a href="/influxdb" target="_blank">💾 InfluxDB Database</a>
            <a href="/bi" target="_blank">🧠 BI API</a>
            <a href="/simulator" target="_blank">🎲 Data Simulator</a>
        </div>
        
        <div class="status" style="margin-top: 40px;">
            <h3>🌍 Full Stack Benefits</h3>
            <p>• Real-time Monitoring • Grafana Dashboards • InfluxDB Metrics • Business Intelligence • Alerting System • Global Edge Network</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return DASHBOARD_HTML

@app.route('/health')
def health():
    return "OK - Full Stack Monitoring System Running"

@app.route('/grafana')
def grafana_redirect():
    return """
    <html>
    <head>
        <title>Redirecting to Grafana...</title>
        <meta http-equiv="refresh" content="0; url=/grafana/">
    </head>
    <body>
        <p>Redirecting to Grafana...</p>
        <script>window.location.href = '/grafana/';</script>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port, debug=False)
