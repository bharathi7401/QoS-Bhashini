#!/bin/bash

echo "🚀 Starting Bhashini AWS Development Environment..."
echo ""

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Check instance status
echo "📊 Checking AWS instance status..."
INSTANCE_ID="i-0616810ba3843819e"
STATUS=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[*].Instances[*].State.Name' --output text)

if [ "$STATUS" = "stopped" ]; then
    echo "🔄 Instance is stopped. Starting it now..."
    aws ec2 start-instances --instance-ids $INSTANCE_ID
    echo "⏳ Waiting for instance to start..."
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID
    echo "✅ Instance is now running!"
elif [ "$STATUS" = "running" ]; then
    echo "✅ Instance is already running!"
else
    echo "⚠️  Instance status: $STATUS"
fi

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[*].Instances[*].PublicIpAddress' --output text)
echo "🌐 Instance IP: $PUBLIC_IP"

echo ""
echo "🔌 Connecting to AWS development environment..."
echo "   SSH: ssh -i ~/.ssh/bhashini-dev-key.pem ubuntu@$PUBLIC_IP"
echo "   Grafana: http://$PUBLIC_IP:3000 (admin/admin123)"
echo "   InfluxDB: http://$PUBLIC_IP:8086"
echo ""

# Offer to connect via SSH
read -p "Would you like to connect via SSH now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔗 Connecting to AWS instance..."
    ssh -i ~/.ssh/bhashini-dev-key.pem ubuntu@$PUBLIC_IP
fi

echo ""
echo "💡 Tips:"
echo "   - Use VS Code Remote-SSH for full IDE experience"
echo "   - Install Traycer extension in remote VS Code"
echo "   - Stop instance when done: aws ec2 stop-instances --instance-ids $INSTANCE_ID"
echo ""
echo "🎉 Happy coding on AWS! 🚀"
