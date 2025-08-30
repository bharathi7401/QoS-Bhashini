#!/bin/bash

# Bhashini Dashboard Status Check Script
# This script checks the status of your deployed dashboards

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="bhashini-dashboards"
REGION="ap-south-1"
INSTANCE_ID="i-02459867a699b6c14"

echo -e "${BLUE}🔍 Bhashini Dashboard Status Check${NC}"
echo "=========================================="

# Check CloudFormation stack status
echo -e "${YELLOW}Checking CloudFormation stack...${NC}"
STACK_STATUS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].StackStatus' --output text)
echo -e "${BLUE}Stack Status: ${STACK_STATUS}${NC}"

# Get instance information
echo -e "${YELLOW}Checking EC2 instance...${NC}"
INSTANCE_INFO=$(aws ec2 describe-instances --region $REGION --instance-ids $INSTANCE_ID --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress,LaunchTime]' --output table)
echo -e "${BLUE}Instance Info:${NC}"
echo "$INSTANCE_INFO"

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances --region $REGION --instance-ids $INSTANCE_ID --query 'Reservations[*].Instances[*].PublicIpAddress' --output text)
echo -e "${BLUE}Public IP: ${PUBLIC_IP}${NC}"

# Test dashboard connectivity
echo -e "${YELLOW}Testing dashboard connectivity...${NC}"

# Test main dashboard
echo -n "Main Dashboard (Port 80): "
if curl -s --max-time 10 "http://${PUBLIC_IP}" > /dev/null; then
    echo -e "${GREEN}✅ Accessible${NC}"
else
    echo -e "${RED}❌ Not accessible${NC}"
fi

# Test Grafana
echo -n "Grafana (Port 3000): "
if curl -s --max-time 10 "http://${PUBLIC_IP}:3000" > /dev/null; then
    echo -e "${GREEN}✅ Accessible${NC}"
else
    echo -e "${RED}❌ Not accessible${NC}"
fi

# Test InfluxDB
echo -n "InfluxDB (Port 8086): "
if curl -s --max-time 10 "http://${PUBLIC_IP}:8086" > /dev/null; then
    echo -e "${GREEN}✅ Accessible${NC}"
else
    echo -e "${RED}❌ Not accessible${NC}"
fi

echo ""
echo -e "${BLUE}📊 Dashboard URLs:${NC}"
echo -e "Main Portal: ${GREEN}http://${PUBLIC_IP}${NC}"
echo -e "Grafana: ${GREEN}http://${PUBLIC_IP}:3000${NC}"
echo -e "InfluxDB: ${GREEN}http://${PUBLIC_IP}:8086${NC}"
echo ""
echo -e "${BLUE}🔐 Admin Access:${NC}"
echo -e "Grafana Login: ${GREEN}admin/admin123${NC}"
echo ""
echo -e "${YELLOW}💡 If services are not accessible, the instance may still be setting up.${NC}"
echo -e "${YELLOW}   Wait 5-10 minutes and run this script again.${NC}"
