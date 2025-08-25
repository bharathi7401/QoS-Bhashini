# Bhashini QoS Monitoring Stack - AWS Deployment

This directory contains the AWS infrastructure setup for the Bhashini QoS monitoring stack, designed to run on AWS ECS with Fargate for serverless container management.

## 🏗️ Architecture

The AWS deployment uses:
- **ECS Fargate**: Serverless container management (no EC2 instances to manage)
- **Application Load Balancer**: Public access to Grafana
- **EFS**: Persistent storage for InfluxDB and Grafana data
- **CloudWatch**: Centralized logging and monitoring
- **VPC**: Isolated network with public/private subnets
- **NAT Gateway**: Private subnet internet access

## 📋 Prerequisites

Before deploying, ensure you have:

1. **AWS CLI** installed and configured
   ```bash
   aws configure
   ```

2. **Terraform** installed (version >= 1.0)
   ```bash
   # macOS
   brew install terraform
   
   # Linux
   curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
   sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
   sudo apt-get update && sudo apt-get install terraform
   ```

3. **Docker** installed and running
   ```bash
   # macOS
   brew install --cask docker
   
   # Linux
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```

4. **AWS Permissions**: Your AWS user/role needs permissions for:
   - ECS
   - ECR
   - VPC
   - EFS
   - CloudWatch
   - IAM
   - Application Load Balancer

## 🚀 Quick Start

### 1. Clone and Navigate
```bash
cd aws
```

### 2. Deploy Everything
```bash
chmod +x deploy.sh
./deploy.sh
```

This script will:
- Check prerequisites
- Build and push Docker images to ECR
- Deploy infrastructure with Terraform
- Wait for services to be ready
- Display access information

### 3. Access Your Stack
- **Grafana**: http://[ALB-DNS-NAME] (admin/admin123)
- **CloudWatch Logs**: AWS Console → CloudWatch → Log Groups
- **ECS Console**: AWS Console → ECS → Clusters

## 🔧 Manual Deployment Steps

If you prefer to deploy step by step:

### 1. Build and Push Docker Image
```bash
# Build image
docker build -t bhashini-qos-data-simulator:latest ../data-simulator/

# Get AWS account and region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region)

# Tag for ECR
docker tag bhashini-qos-data-simulator:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/bhashini-qos-data-simulator:latest

# Create ECR repository
aws ecr create-repository --repository-name bhashini-qos-data-simulator

# Login to ECR
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Push image
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/bhashini-qos-data-simulator:latest
```

### 2. Deploy Infrastructure
```bash
cd terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
cd ..
```

### 3. Wait for Services
```bash
# Get cluster ARN
ECS_CLUSTER_ARN=$(cd terraform && terraform output -raw ecs_cluster_arn && cd ..)

# Wait for services to be stable
aws ecs wait services-stable --cluster ${ECS_CLUSTER_ARN} --services bhashini-qos-influxdb
aws ecs wait services-stable --cluster ${ECS_CLUSTER_ARN} --services bhashini-qos-grafana
aws ecs wait services-stable --cluster ${ECS_CLUSTER_ARN} --services bhashini-qos-data-simulator
```

## 📊 Monitoring and Management

### View Service Status
```bash
aws ecs describe-services \
  --cluster bhashini-qos-cluster \
  --services bhashini-qos-influxdb bhashini-qos-grafana bhashini-qos-data-simulator
```

### View Logs
```bash
# InfluxDB logs
aws logs tail /ecs/bhashini-qos/influxdb --follow

# Grafana logs
aws logs tail /ecs/bhashini-qos/grafana --follow

# Data Simulator logs
aws logs tail /ecs/bhashini-qos/data-simulator --follow
```

### Scale Services
```bash
# Scale up Grafana
aws ecs update-service \
  --cluster bhashini-qos-cluster \
  --service bhashini-qos-grafana \
  --desired-count 2

# Scale down
aws ecs update-service \
  --cluster bhashini-qos-cluster \
  --service bhashini-qos-grafana \
  --desired-count 1
```

### Update Services
```bash
# Force new deployment
aws ecs update-service \
  --cluster bhashini-qos-cluster \
  --service bhashini-qos-grafana \
  --force-new-deployment
```

## 💰 Cost Optimization

### Development Environment
- Use `t3.medium` for ECS tasks (cheaper than larger instances)
- Set `desired_count = 1` for all services
- Use CloudWatch logs with 7-day retention

### Production Considerations
- Use `t3.large` or `c5.large` for better performance
- Enable auto-scaling based on CPU/memory metrics
- Use CloudWatch logs with longer retention
- Consider using Spot instances for cost savings

## 🧹 Cleanup

### Remove Everything
```bash
chmod +x cleanup.sh
./cleanup.sh
```

### Manual Cleanup
```bash
cd terraform
terraform destroy
cd ..

# Remove ECR repository
aws ecr delete-repository --repository-name bhashini-qos-data-simulator --force
```

## 🔍 Troubleshooting

### Common Issues

1. **ECS Service Won't Start**
   - Check CloudWatch logs for container startup errors
   - Verify ECS task execution role has proper permissions
   - Check if EFS mount targets are accessible

2. **Container Health Check Failures**
   - Verify security group rules allow traffic between services
   - Check if InfluxDB is fully initialized before other services start
   - Review container health check configuration

3. **EFS Mount Issues**
   - Ensure EFS mount targets are in the same subnets as ECS tasks
   - Verify security groups allow NFS traffic (port 2049)
   - Check if EFS file system is accessible from VPC

### Debug Commands
```bash
# Check ECS task status
aws ecs describe-tasks \
  --cluster bhashini-qos-cluster \
  --tasks $(aws ecs list-tasks --cluster bhashini-qos-cluster --service-name bhashini-qos-influxdb --query 'taskArns' --output text)

# Check EFS mount targets
aws efs describe-mount-targets --file-system-id $(cd terraform && terraform output -raw efs_file_system_id && cd ..)

# Check ALB target health
aws elbv2 describe-target-health --target-group-arn $(cd terraform && terraform output -raw grafana_target_group_arn && cd ..)
```

## 📁 File Structure

```
aws/
├── README.md              # This file
├── deploy.sh              # Complete deployment script
├── cleanup.sh             # Complete cleanup script
└── terraform/             # Terraform configuration
    ├── main.tf            # Main infrastructure
    ├── variables.tf       # Variable definitions
    ├── ecs.tf             # ECS services and tasks
    └── outputs.tf         # Output values
```

## 🔐 Security Notes

- All services run in private subnets
- Only Grafana is exposed via ALB
- EFS is encrypted at rest
- CloudWatch logs are encrypted
- IAM roles follow least privilege principle

## 📞 Support

For issues or questions:
1. Check CloudWatch logs first
2. Review ECS service events
3. Verify Terraform state and outputs
4. Check AWS service quotas and limits
