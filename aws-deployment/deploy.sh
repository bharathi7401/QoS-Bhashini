#!/bin/bash

# Bhashini QoS Dashboards - AWS Deployment Script
# This script deploys the dashboard infrastructure to AWS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="bhashini-dashboards"
REGION="ap-south-1"  # Mumbai region for better India performance
INSTANCE_TYPE="t3.medium"

echo -e "${BLUE}🚀 Bhashini QoS Dashboards - AWS Deployment (Mumbai Region)${NC}"
echo "=================================================="

# Check if AWS CLI is configured
echo -e "${YELLOW}Checking AWS configuration...${NC}"
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo -e "${RED}❌ AWS CLI not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ AWS CLI configured${NC}"

# Get AWS account info
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${BLUE}AWS Account: ${ACCOUNT_ID}${NC}"
echo -e "${BLUE}Region: ${REGION} (Mumbai - Best for India)${NC}"

# Check if key pair exists in the target region
echo -e "${YELLOW}Checking for existing key pairs in ${REGION}...${NC}"
KEY_PAIRS=$(aws ec2 describe-key-pairs --region $REGION --query 'KeyPairs[*].KeyName' --output text)

if [ -z "$KEY_PAIRS" ]; then
    echo -e "${YELLOW}No key pairs found in ${REGION}. Creating a new one...${NC}"
    KEY_NAME="bhashini-dashboard-key"
    aws ec2 create-key-pair --key-name $KEY_NAME --region $REGION --query 'KeyMaterial' --output text > "${KEY_NAME}.pem"
    chmod 400 "${KEY_NAME}.pem"
    echo -e "${GREEN}✅ Created key pair: ${KEY_NAME}${NC}"
    echo -e "${YELLOW}⚠️  Save the private key file: ${KEY_NAME}.pem${NC}"
else
    echo -e "${GREEN}Available key pairs in ${REGION}:${NC}"
    echo "$KEY_PAIRS"
    read -p "Enter key pair name to use: " KEY_NAME
fi

# Get VPC and Subnet information for Mumbai region
echo -e "${YELLOW}Getting VPC and Subnet information for ${REGION}...${NC}"
VPC_ID=$(aws ec2 describe-vpcs --region $REGION --query 'Vpcs[0].VpcId' --output text)
SUBNET_ID=$(aws ec2 describe-subnets --region $REGION --query 'Subnets[0].SubnetId' --output text)

echo -e "${GREEN}VPC ID: ${VPC_ID}${NC}"
echo -e "${GREEN}Subnet ID: ${SUBNET_ID}${NC}"

# Deploy CloudFormation stack
echo -e "${YELLOW}Deploying CloudFormation stack to ${REGION}...${NC}"
aws cloudformation deploy \
    --template-file cloudformation.yml \
    --stack-name $STACK_NAME \
    --parameter-overrides \
        InstanceType=$INSTANCE_TYPE \
        KeyPairName=$KEY_NAME \
        VpcId=$VPC_ID \
        SubnetId=$SUBNET_ID \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $REGION

echo -e "${GREEN}✅ CloudFormation stack deployed successfully!${NC}"

# Get stack outputs
echo -e "${YELLOW}Getting deployment information...${NC}"
DASHBOARD_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`DashboardURL`].OutputValue' \
    --output text)

GRAFANA_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`GrafanaURL`].OutputValue' \
    --output text)

INSTANCE_ID=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`InstanceId`].OutputValue' \
    --output text)

# Wait for instance to be running
echo -e "${YELLOW}Waiting for EC2 instance to be running...${NC}"
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION
echo -e "${GREEN}✅ EC2 instance is running${NC}"

# Wait a bit more for user data to complete
echo -e "${YELLOW}Waiting for instance setup to complete...${NC}"
sleep 60

# Test the deployment
echo -e "${YELLOW}Testing deployment...${NC}"
if curl -s --max-time 10 "$DASHBOARD_URL" > /dev/null; then
    echo -e "${GREEN}✅ Dashboard is accessible!${NC}"
else
    echo -e "${YELLOW}⚠️  Dashboard not yet accessible, may still be setting up...${NC}"
fi

# Display results
echo ""
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "=================================================="
echo -e "${BLUE}Stack Name: ${STACK_NAME}${NC}"
echo -e "${BLUE}Region: ${REGION} (Mumbai - Best for India)${NC}"
echo -e "${BLUE}Instance ID: ${INSTANCE_ID}${NC}"
echo -e "${BLUE}Dashboard URL: ${DASHBOARD_URL}${NC}"
echo -e "${BLUE}Grafana URL: ${GRAFANA_URL}${NC}"
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo "1. Wait 5-10 minutes for full setup to complete"
echo "2. Access your dashboards at: ${DASHBOARD_URL}"
echo "3. Grafana admin access: ${GRAFANA_URL} (admin/admin123)"
echo "4. Monitor instance in AWS Console"
echo ""
echo -e "${YELLOW}🔐 SSH Access (if needed):${NC}"
echo "ssh -i ${KEY_NAME}.pem ec2-user@$(echo $DASHBOARD_URL | sed 's|http://||')"
echo ""
echo -e "${YELLOW}💰 Estimated Monthly Cost: $20-30${NC}"
echo -e "${YELLOW}⚠️  Remember to stop/terminate when not needed${NC}"
echo -e "${YELLOW}🇮🇳 Mumbai region provides best performance for India-based users${NC}"

# Create a simple status check script
cat > check-status.sh << EOF
#!/bin/bash
echo "Checking Bhashini Dashboard status..."
echo "Region: ${REGION}"
echo "Dashboard URL: $DASHBOARD_URL"
echo "Grafana URL: $GRAFANA_URL"
echo ""
echo "Testing connectivity..."
curl -s --max-time 10 "$DASHBOARD_URL" > /dev/null && echo "✅ Dashboard accessible" || echo "❌ Dashboard not accessible"
curl -s --max-time 10 "$GRAFANA_URL" > /dev/null && echo "✅ Grafana accessible" || echo "❌ Grafana not accessible"
EOF

chmod +x check-status.sh
echo -e "${GREEN}✅ Created check-status.sh script${NC}"
echo -e "${BLUE}Run './check-status.sh' to check deployment status${NC}"
