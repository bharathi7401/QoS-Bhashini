#!/bin/bash

# Bhashini QoS Monitoring Stack - AWS Cleanup Script
# This script removes all AWS resources created by the deployment

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
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_status "All prerequisites met"
}

# Stop ECS services
stop_ecs_services() {
    print_info "Stopping ECS services..."
    
    cd terraform
    
    # Get ECS cluster ARN
    ECS_CLUSTER_ARN=$(terraform output -raw ecs_cluster_arn 2>/dev/null || echo "")
    
    if [ -n "$ECS_CLUSTER_ARN" ]; then
        # Update services to 0 desired count
        print_info "Scaling down ECS services..."
        
        aws ecs update-service \
            --cluster ${ECS_CLUSTER_ARN} \
            --service bhashini-qos-influxdb \
            --desired-count 0 2>/dev/null || print_warning "Could not scale down InfluxDB service"
        
        aws ecs update-service \
            --cluster ${ECS_CLUSTER_ARN} \
            --service bhashini-qos-grafana \
            --desired-count 0 2>/dev/null || print_warning "Could not scale down Grafana service"
        
        aws ecs update-service \
            --cluster ${ECS_CLUSTER_ARN} \
            --service bhashini-qos-data-simulator \
            --desired-count 0 2>/dev/null || print_warning "Could not scale down Data Simulator service"
        
        # Wait for services to stop
        print_info "Waiting for services to stop..."
        sleep 30
        
        print_status "ECS services stopped"
    else
        print_warning "ECS cluster not found, skipping service cleanup"
    fi
    
    cd ..
}

# Remove ECR images
remove_ecr_images() {
    print_info "Removing ECR images..."
    
    # Get AWS account ID and region
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=$(aws configure get region)
    
    # Remove ECR repository
    print_info "Removing ECR repository..."
    aws ecr delete-repository \
        --repository-name bhashini-qos-data-simulator \
        --force 2>/dev/null || print_warning "Could not remove ECR repository"
    
    print_status "ECR images removed"
}

# Destroy infrastructure with Terraform
destroy_infrastructure() {
    print_info "Destroying infrastructure with Terraform..."
    
    cd terraform
    
    # Check if Terraform state exists
    if [ -f "terraform.tfstate" ]; then
        # Plan destruction
        print_info "Planning destruction..."
        terraform plan -destroy -out=tfdestroy
        
        # Apply destruction
        print_info "Destroying infrastructure..."
        terraform apply tfdestroy
        
        print_status "Infrastructure destroyed successfully"
    else
        print_warning "No Terraform state found, skipping infrastructure cleanup"
    fi
    
    cd ..
}

# Clean up local files
cleanup_local() {
    print_info "Cleaning up local files..."
    
    # Remove Terraform files
    if [ -d "terraform" ]; then
        cd terraform
        rm -f tfplan tfdestroy terraform.tfstate* .terraform.lock.hcl
        rm -rf .terraform/
        cd ..
        print_status "Terraform files cleaned up"
    fi
    
    # Remove any temporary files
    rm -f *.log *.tmp 2>/dev/null || true
    
    print_status "Local files cleaned up"
}

# Main cleanup flow
main() {
    echo "🧹 Bhashini QoS Monitoring Stack - AWS Cleanup"
    echo "==============================================="
    echo ""
    
    print_warning "This will remove ALL AWS resources created by the deployment!"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleanup cancelled"
        exit 0
    fi
    
    check_prerequisites
    stop_ecs_services
    remove_ecr_images
    destroy_infrastructure
    cleanup_local
    
    print_status "Cleanup completed successfully!"
    echo ""
    echo "All AWS resources have been removed."
    echo "You can now run the deployment script again if needed."
}

# Run main function
main "$@"
