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
