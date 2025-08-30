# 🚀 Bhashini QoS Dashboards - AWS Deployment

This directory contains everything needed to deploy your Bhashini QoS Dashboards to AWS for worldwide access.

## 🌍 **What This Gives You:**

- **Global Access**: Anyone in the world can access your dashboards
- **Professional Hosting**: 24/7 availability on AWS infrastructure
- **Scalability**: Easy to scale up/down based on usage
- **Monitoring**: Built-in CloudWatch monitoring
- **Security**: AWS security groups and IAM roles
- **🇮🇳 India Optimized**: Deployed in Mumbai (ap-south-1) for best performance

## 💰 **Cost Estimate:**

- **EC2 t3.medium**: ~$15-20/month
- **Data Transfer**: ~$5-10/month
- **Total**: ~$20-30/month

## 🚀 **Quick Deployment:**

### **1. Prerequisites:**
- AWS CLI installed and configured
- AWS account with EC2 permissions
- Basic knowledge of AWS services

### **2. Deploy Everything:**
```bash
cd aws-deployment
chmod +x deploy.sh
./deploy.sh
```

### **3. Access Your Dashboards:**
- **Public URL**: Will be provided after deployment
- **Grafana Admin**: admin/admin123
- **No localhost needed!**

## 📋 **What Gets Deployed:**

### **AWS Resources:**
- **EC2 Instance**: t3.medium (2 vCPU, 4GB RAM)
- **Security Groups**: Open ports 80, 443, 3000, 8086
- **Elastic IP**: Static public IP address
- **IAM Role**: EC2 instance permissions
- **CloudWatch**: Monitoring dashboard
- **Region**: Mumbai (ap-south-1) - Best for India

### **Application Stack:**
- **Nginx**: Reverse proxy and load balancer
- **Grafana**: Dashboard engine
- **InfluxDB**: Time-series database
- **Docker Compose**: Container orchestration
- **Public Portal**: Beautiful landing page

## 🔧 **Manual Deployment Steps:**

### **Step 1: Deploy CloudFormation Stack**
```bash
aws cloudformation deploy \
    --template-file cloudformation.yml \
    --stack-name bhashini-dashboards \
    --capabilities CAPABILITY_NAMED_IAM \
    --region ap-south-1
```

### **Step 2: Get Stack Outputs**
```bash
aws cloudformation describe-stacks \
    --stack-name bhashini-dashboards \
    --region ap-south-1
```

### **Step 3: Access Dashboards**
- Use the DashboardURL from stack outputs
- Wait 5-10 minutes for full setup

## 🌐 **Access URLs After Deployment:**

### **Public Access:**
- **Main Portal**: http://YOUR_EC2_PUBLIC_IP
- **Grafana**: http://YOUR_EC2_PUBLIC_IP:3000
- **Admin Login**: admin/admin123

### **Direct Dashboard Access:**
- **Ultimate Dashboard**: http://YOUR_EC2_PUBLIC_IP:3000/d/be149f0f-0844-4616-83c5-3e896d6aa98b
- **Customer Overview**: http://YOUR_EC2_PUBLIC_IP:3000/d/bhashini-customer-overview
- **All Other Dashboards**: Accessible via Grafana interface

## 🔐 **Security Features:**

### **Network Security:**
- **Port 22**: SSH access (restricted to your IP)
- **Port 80**: HTTP access (public)
- **Port 443**: HTTPS access (when SSL configured)
- **Port 3000**: Grafana direct access
- **Port 8086**: InfluxDB access

### **Application Security:**
- **Rate Limiting**: API calls limited to prevent abuse
- **Security Headers**: XSS protection, frame options
- **IAM Roles**: Least privilege access
- **Security Groups**: Network-level protection

## 📊 **Monitoring & Management:**

### **CloudWatch Dashboard:**
- CPU utilization
- Network in/out
- Instance status
- Custom metrics

### **AWS Console:**
- EC2 instance management
- Security group configuration
- Cost monitoring
- Backup and recovery

## 🛠️ **Customization Options:**

### **Instance Size:**
- **t3.micro**: $5-8/month (1 vCPU, 1GB RAM)
- **t3.small**: $10-15/month (2 vCPU, 2GB RAM)
- **t3.medium**: $15-20/month (2 vCPU, 4GB RAM) ← **Recommended**
- **t3.large**: $25-35/month (2 vCPU, 8GB RAM)

### **Region Selection:**
- **ap-south-1**: Mumbai (default - Best for India) 🇮🇳
- **us-east-1**: Virginia
- **us-west-2**: Oregon
- **eu-west-1**: Ireland
- **ap-southeast-1**: Singapore

### **SSL/HTTPS:**
- **Let's Encrypt**: Free SSL certificates
- **AWS Certificate Manager**: Managed SSL
- **Custom Domain**: Point your domain to the EC2 instance

## 🚨 **Important Notes:**

### **Cost Management:**
- **Stop Instance**: ~$0.50/month when not in use
- **Terminate Stack**: $0 when completely removed
- **Monitor Usage**: Use AWS Cost Explorer

### **Data Persistence:**
- **InfluxDB Data**: Stored in EBS volumes
- **Grafana Config**: Stored in EBS volumes
- **Backup Strategy**: Consider automated backups

### **Scaling:**
- **Vertical**: Change instance type
- **Horizontal**: Add load balancer + multiple instances
- **Auto-scaling**: Based on CPU/memory usage

## 🔍 **Troubleshooting:**

### **Common Issues:**
1. **Instance not accessible**: Check security groups
2. **Services not starting**: Check Docker logs
3. **High costs**: Stop instance when not needed
4. **Performance issues**: Upgrade instance type

### **Useful Commands:**
```bash
# Check deployment status
./check-status.sh

# View CloudFormation events
aws cloudformation describe-stack-events --stack-name bhashini-dashboards --region ap-south-1

# SSH to instance (if needed)
ssh -i bhashini-dashboard-key.pem ec2-user@YOUR_EC2_PUBLIC_IP

# View instance logs
aws logs describe-log-groups --log-group-name-prefix /aws/ec2 --region ap-south-1
```

## 🌟 **Next Steps After Deployment:**

1. **Test Access**: Verify all dashboards work
2. **Configure Alerts**: Set up CloudWatch alarms
3. **Add SSL**: Configure HTTPS for security
4. **Custom Domain**: Point your domain to the instance
5. **Backup Strategy**: Plan for data persistence
6. **Team Access**: Share the public URL with your team

## 📞 **Support:**

- **AWS Support**: For infrastructure issues
- **Grafana Community**: For dashboard issues
- **InfluxDB Docs**: For database issues
- **This Repository**: For deployment issues

## 🇮🇳 **Why Mumbai Region?**

- **Lower Latency**: Better performance for India-based users
- **Cost Effective**: Competitive pricing in ap-south-1
- **Compliance**: Data residency in India
- **Network**: Optimized routing for Indian ISPs
- **Support**: Local AWS support team

---

**🎉 Congratulations!** Your dashboards will be accessible worldwide once deployed to AWS Mumbai region!
