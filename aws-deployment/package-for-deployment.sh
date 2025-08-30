#!/bin/bash

# Package Bhashini Dashboards for AWS Deployment
# This script copies all necessary files to the aws-deployment directory

set -e

echo "📦 Packaging Bhashini Dashboards for AWS Deployment..."

# Create necessary directories
mkdir -p aws-deployment/grafana/provisioning/dashboards
mkdir -p aws-deployment/grafana/provisioning/alerting
mkdir -p aws-deployment/public-dashboard
mkdir -p aws-deployment/data-generator

# Copy Grafana provisioning files
echo "📁 Copying Grafana provisioning files..."
cp -r grafana/provisioning/dashboards/* aws-deployment/grafana/provisioning/dashboards/
cp -r grafana/provisioning/alerting/* aws-deployment/grafana/provisioning/alerting/

# Copy public dashboard files
echo "🌐 Copying public dashboard files..."
cp -r public-dashboard/* aws-deployment/public-dashboard/

# Copy data generator
echo "📊 Copying data generator..."
cp -r data-generator/* aws-deployment/data-generator/ 2>/dev/null || echo "No data-generator directory found"

# Create a simple data generator if it doesn't exist
if [ ! -f "aws-deployment/data-generator/generate_qos_data.py" ]; then
    cat > aws-deployment/data-generator/generate_qos_data.py << 'EOF'
#!/usr/bin/env python3
"""
Simple QoS data generator for Bhashini Dashboards
"""

import os
import time
import random
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuration
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'admin-token-123')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'bhashini')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'qos_metrics')

def generate_qos_data():
    """Generate realistic QoS metrics data"""
    
    # Initialize InfluxDB client
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    # Service configurations
    services = ['asr', 'translation', 'tts']
    tenants = ['enterprise_1', 'startup_1', 'freemium_1']
    sla_tiers = ['premium', 'standard', 'basic']
    
    try:
        while True:
            timestamp = datetime.utcnow()
            points = []
            
            for service in services:
                for tenant in tenants:
                    # Determine SLA tier based on tenant
                    sla_tier = 'premium' if tenant == 'enterprise_1' else 'standard' if tenant == 'startup_1' else 'basic'
                    
                    # Generate availability (higher for premium tiers)
                    base_availability = 99.5 if sla_tier == 'premium' else 97.0 if sla_tier == 'standard' else 94.0
                    availability = max(85.0, min(100.0, base_availability + random.uniform(-2.0, 2.0)))
                    
                    # Generate latency (lower for premium tiers)
                    base_latency = 50 if sla_tier == 'premium' else 150 if sla_tier == 'standard' else 300
                    latency = max(10, min(1000, base_latency + random.uniform(-20, 50)))
                    
                    # Generate error rate (lower for premium tiers)
                    base_error_rate = 0.1 if sla_tier == 'premium' else 0.5 if sla_tier == 'standard' else 1.0
                    error_rate = max(0.0, min(5.0, base_error_rate + random.uniform(-0.1, 0.3)))
                    
                    # Generate throughput
                    throughput = random.uniform(100, 2000)
                    
                    # Create data points
                    points.extend([
                        Point("qos_metrics")
                            .tag("service_name", service)
                            .tag("tenant_id", tenant)
                            .tag("sla_tier", sla_tier)
                            .field("metric_type", "availability")
                            .field("value", availability)
                            .time(timestamp),
                        
                        Point("qos_metrics")
                            .tag("service_name", service)
                            .tag("tenant_id", tenant)
                            .tag("sla_tier", sla_tier)
                            .field("metric_type", "latency")
                            .field("value", latency)
                            .time(timestamp),
                        
                        Point("qos_metrics")
                            .tag("service_name", service)
                            .tag("tenant_id", tenant)
                            .tag("sla_tier", sla_tier)
                            .field("metric_type", "error_rate")
                            .field("value", error_rate)
                            .time(timestamp),
                        
                        Point("qos_metrics")
                            .tag("service_name", service)
                            .tag("tenant_id", tenant)
                            .tag("sla_tier", sla_tier)
                            .field("metric_type", "throughput")
                            .field("value", throughput)
                            .time(timestamp)
                    ])
            
            # Write data to InfluxDB
            if points:
                write_api.write(bucket=INFLUXDB_BUCKET, record=points)
                print(f"✅ Generated {len(points)} data points at {timestamp}")
            
            # Wait before next generation
            time.sleep(30)  # Generate data every 30 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Data generation stopped by user")
    except Exception as e:
        print(f"❌ Error generating data: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    print("🚀 Starting QoS data generation...")
    generate_qos_data()
EOF
fi

# Create deployment instructions
cat > aws-deployment/DEPLOYMENT_INSTRUCTIONS.md << 'EOF'
# 🚀 Quick AWS Deployment

## **Option 1: Automated Deployment (Recommended)**
```bash
cd aws-deployment
./deploy.sh
```

## **Option 2: Manual Deployment**
```bash
# 1. Deploy CloudFormation stack
aws cloudformation deploy \
    --template-file cloudformation.yml \
    --stack-name bhashini-dashboards \
    --capabilities CAPABILITY_NAMED_IAM \
    --region us-east-1

# 2. Get deployment info
aws cloudformation describe-stacks \
    --stack-name bhashini-dashboards \
    --query 'Stacks[0].Outputs'
```

## **What You Get:**
- 🌍 **Global Access**: Anyone can access your dashboards
- 💰 **Cost**: ~$20-30/month
- 🔒 **Security**: AWS security groups and IAM
- 📊 **Monitoring**: CloudWatch integration

## **After Deployment:**
- **Public URL**: Will be provided
- **Grafana Admin**: admin/admin123
- **Wait**: 5-10 minutes for full setup

## **Need Help?**
- Check the main README.md
- Run `./check-status.sh` after deployment
- Monitor in AWS Console
EOF

echo "✅ Packaging complete!"
echo ""
echo "📦 Your AWS deployment package is ready in the 'aws-deployment' directory"
echo ""
echo "🚀 To deploy to AWS:"
echo "   cd aws-deployment"
echo "   ./deploy.sh"
echo ""
echo "📚 Read DEPLOYMENT_INSTRUCTIONS.md for quick start"
echo "📖 Read README.md for detailed information"
echo ""
echo "🌍 After deployment, your dashboards will be accessible worldwide!"
