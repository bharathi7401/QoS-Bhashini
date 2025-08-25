#!/bin/bash

echo "🛑 Stopping Bhashini Cloud9 Development Environment..."
echo ""

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Instance details
INSTANCE_ID="i-0616810ba3843819e"

echo "📊 Checking instance status..."
STATUS=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[*].Instances[*].State.Name' --output text)

if [ "$STATUS" = "running" ]; then
    echo "🔄 Instance is running. Stopping it now..."
    aws ec2 stop-instances --instance-ids $INSTANCE_ID
    echo "⏳ Waiting for instance to stop..."
    aws ec2 wait instance-stopped --instance-ids $INSTANCE_ID
    echo "✅ Instance has been stopped!"
    echo ""
    echo "💰 **Cost Savings:**"
    echo "   - Running: ~$0.166/hour"
    echo "   - Stopped: ~$0.01/hour (just storage)"
    echo "   - You're saving money! 💰"
elif [ "$STATUS" = "stopped" ]; then
    echo "✅ Instance is already stopped!"
else
    echo "⚠️  Instance status: $STATUS"
fi

echo ""
echo "💡 **Next Time:**"
echo "   To start Cloud9 again, run: ./start-cloud9.sh"
echo ""
echo "🎉 Cloud9 environment stopped successfully!"
