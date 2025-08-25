#!/bin/bash

# Bhashini QoS Monitoring Stack - AWS Deployment Script
# This script sets up the complete infrastructure on AWS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found. Please install it first."
        exit 1
    fi
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform not found. Please install it first."
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_status "All prerequisites met"
}

# Build and push Docker images
build_and_push_images() {
    print_info "Building and pushing Docker images..."
    
    # Get AWS account ID and region
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=$(aws configure get region)
    
    # Build data simulator image
    print_info "Building data simulator image..."
    docker build -t bhashini-qos-data-simulator:latest ../data-simulator/
    
    # Tag for ECR
    docker tag bhashini-qos-data-simulator:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/bhashini-qos-data-simulator:latest
    
    # Create ECR repository if it doesn't exist
    aws ecr describe-repositories --repository-names bhashini-qos-data-simulator &> /dev/null || \
    aws ecr create-repository --repository-name bhashini-qos-data-simulator
    
    # Login to ECR
    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
    
    # Push image
    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/bhashini-qos-data-simulator:latest
    
    print_status "Docker images built and pushed successfully"
}

# Deploy infrastructure with Terraform
deploy_infrastructure() {
    print_info "Deploying infrastructure with Terraform..."
    
    cd terraform
    
    # Initialize Terraform
    print_info "Initializing Terraform..."
    terraform init
    
    # Plan deployment
    print_info "Planning deployment..."
    terraform plan -out=tfplan
    
    # Apply deployment
    print_info "Applying infrastructure changes..."
    terraform apply tfplan
    
    # Get outputs
    print_info "Getting infrastructure outputs..."
    ALB_DNS_NAME=$(terraform output -raw alb_dns_name)
    ECS_CLUSTER_ARN=$(terraform output -raw ecs_cluster_arn)
    
    print_status "Infrastructure deployed successfully"
    print_info "ALB DNS Name: ${ALB_DNS_NAME}"
    print_info "ECS Cluster ARN: ${ECS_CLUSTER_ARN}"
    
    cd ..
}

# Wait for services to be ready
wait_for_services() {
    print_info "Waiting for services to be ready..."
    
    cd terraform
    ECS_CLUSTER_ARN=$(terraform output -raw ecs_cluster_arn)
    cd ..
    
    # Wait for InfluxDB
    print_info "Waiting for InfluxDB service..."
    aws ecs wait services-stable \
        --cluster ${ECS_CLUSTER_ARN} \
        --services bhashini-qos-influxdb
    
    print_status "InfluxDB service is stable"
    
    # Wait for Grafana
    print_info "Waiting for Grafana service..."
    aws ecs wait services-stable \
        --cluster ${ECS_CLUSTER_ARN} \
        --services bhashini-qos-grafana
    
    print_status "Grafana service is stable"
    
    # Wait for Data Simulator
    print_info "Waiting for Data Simulator service..."
    aws ecs wait services-stable \
        --cluster ${ECS_CLUSTER_ARN} \
        --services bhashini-qos-data-simulator
    
    print_status "Data Simulator service is stable"
}

# Setup EFS mount points
setup_efs_mounts() {
    print_info "Setting up EFS mount points..."
    
    cd terraform
    EFS_FILE_SYSTEM_ID=$(terraform output -raw efs_file_system_id)
    cd ..
    
    # Create directories in EFS
    print_info "Creating EFS directories..."
    
    # Get EFS mount target IP
    EFS_MOUNT_TARGET_IP=$(aws efs describe-mount-targets \
        --file-system-id ${EFS_FILE_SYSTEM_ID} \
        --query 'MountTargets[0].IpAddress' \
        --output text)
    
    # Create directories (this would typically be done by the containers)
    print_warning "EFS directories will be created automatically by the containers on first run"
}

# Display final information
display_final_info() {
    print_status "Deployment completed successfully!"
    
    cd terraform
    ALB_DNS_NAME=$(terraform output -raw alb_dns_name)
    cd ..
    
    echo ""
    echo "🎯 Access Information:"
    echo "======================"
    echo "Grafana Dashboard: http://${ALB_DNS_NAME}"
    echo "Username: admin"
    echo "Password: admin123"
    echo ""
    echo "📊 Monitoring:"
    echo "=============="
    echo "CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home"
    echo "ECS Console: https://console.aws.amazon.com/ecs/home"
    echo ""
    echo "🔧 Management Commands:"
    echo "======================="
    echo "View service status: aws ecs describe-services --cluster bhashini-qos-cluster --services bhashini-qos-influxdb bhashini-qos-grafana bhashini-qos-data-simulator"
    echo "View logs: aws logs tail /ecs/bhashini-qos/[service-name] --follow"
    echo "Scale services: aws ecs update-service --cluster bhashini-qos-cluster --service bhashini-qos-[service-name] --desired-count [number]"
    echo ""
    echo "🧹 Cleanup:"
    echo "============"
    echo "To remove all resources: cd aws/terraform && terraform destroy"
}

# Main deployment flow
main() {
    echo "🚀 Bhashini QoS Monitoring Stack - AWS Deployment"
    echo "=================================================="
    echo ""
    
    check_prerequisites
    build_and_push_images
    deploy_infrastructure
    wait_for_services
    setup_efs_mounts
    display_final_info
}

# Run main function
main "$@"
