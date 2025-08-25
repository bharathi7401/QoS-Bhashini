#!/bin/bash

echo "🚀 Starting Bhashini Cloud9 Development Environment..."
echo ""

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Instance details
INSTANCE_ID="i-0616810ba3843819e"
INSTANCE_NAME="bhashini-cloud9-dev"

echo "📊 Checking AWS instance status..."
STATUS=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[*].Instances[*].State.Name' --output text)

if [ "$STATUS" = "stopped" ]; then
    echo "🔄 Instance is stopped. Starting it now..."
    aws ec2 start-instances --instance-ids $INSTANCE_ID
    echo "⏳ Waiting for instance to start..."
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID
    echo "✅ Instance is now running!"
    
    # Wait a bit more for services to fully start
    echo "⏳ Waiting for Cloud9 services to start..."
    sleep 30
elif [ "$STATUS" = "running" ]; then
    echo "✅ Instance is already running!"
else
    echo "⚠️  Instance status: $STATUS"
    exit 1
fi

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[*].Instances[*].PublicIpAddress' --output text)
echo "🌐 Instance IP: $PUBLIC_IP"

echo ""
echo "🎉 Your Cloud9 Environment is Ready!"
echo "======================================"
echo ""
echo "🌐 **Access Your Cloud9:**"
echo "   Primary URL: http://$PUBLIC_IP"
echo "   Direct Access: http://$PUBLIC_IP:8081"
echo ""
echo "🔑 **Login Details:**"
echo "   Username: ubuntu"
echo "   Password: (none required)"
echo ""
echo "📁 **Project Location:**"
echo "   /home/ubuntu/bhashini-project"
echo ""
echo "💻 **Features Available:**"
echo "   ✅ Full VS Code experience in browser"
echo "   ✅ Python development tools"
echo "   ✅ Git integration"
echo "   ✅ Terminal access"
echo "   ✅ Extension support (including Traycer!)"
echo "   ✅ All processing on AWS (4 vCPUs + 16GB RAM)"
echo ""

# Test the connection
echo "🔍 Testing Cloud9 connection..."
if curl -s -o /dev/null -w "%{http_code}" "http://$PUBLIC_IP" | grep -q "302\|200"; then
    echo "✅ Cloud9 is accessible!"
else
    echo "⚠️  Cloud9 might still be starting up. Please wait a few minutes."
fi

echo ""
echo "🚀 **Getting Started:**"
echo "1. Open your browser and go to: http://$PUBLIC_IP"
echo "2. You'll see the full VS Code interface"
echo "3. Go to File → Open Folder → /home/ubuntu/bhashini-project"
echo "4. Install Traycer extension (Ctrl+Shift+X)"
echo "5. Start coding with AI assistance on AWS!"
echo ""

# Offer to open the browser
read -p "Would you like to open Cloud9 in your browser now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v open >/dev/null 2>&1; then
        open "http://$PUBLIC_IP"
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "http://$PUBLIC_IP"
    else
        echo "Please manually open: http://$PUBLIC_IP"
    fi
fi

echo ""
echo "💡 **Tips:**"
echo "   - Use Ctrl+Shift+X to install extensions"
echo "   - Use Ctrl+Shift+P for command palette"
echo "   - Use Ctrl+` for integrated terminal"
echo "   - All AI processing happens on AWS!"
echo ""
echo "🛑 **When Done:**"
echo "   Stop the instance: aws ec2 stop-instances --instance-ids $INSTANCE_ID"
echo "   Or use: ./stop-cloud9.sh"
echo ""
echo "🎉 Happy coding in the cloud! 🌟"
