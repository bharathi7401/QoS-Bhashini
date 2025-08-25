# AWS Development Environment Setup for Bhashini QoS

## 🚀 Your AWS Development Environment is Ready!

You now have a fully configured development environment running on AWS that uses **ZERO** of your local machine's resources. Everything runs on AWS EC2!

### 📍 Connection Details
- **Instance IP**: `15.207.100.108`
- **SSH Key**: `~/.ssh/bhashini-dev-key.pem`
- **Username**: `ubuntu`
- **Instance Type**: `t3.xlarge` (4 vCPUs, 16GB RAM)

### 🔌 How to Connect

#### Option 1: SSH Terminal (Recommended for Development)
```bash
ssh -i ~/.ssh/bhashini-dev-key.pem ubuntu@15.207.100.108
```

#### Option 2: VS Code Remote Development
1. Install the "Remote - SSH" extension in VS Code
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Type "Remote-SSH: Connect to Host"
4. Enter: `ubuntu@15.207.100.108`
5. Select the SSH key: `~/.ssh/bhashini-dev-key.pem`

### 🛠️ What's Already Installed
- ✅ **Python 3.10+** with pip
- ✅ **Git** for version control
- ✅ **Docker & Docker Compose** for containers
- ✅ **Node.js & npm** for development tools
- ✅ **Build tools** (gcc, make, etc.)
- ✅ **VS Code Server** for remote development

### 🐳 Running Services
Your Bhashini QoS stack is already running:
- **InfluxDB**: http://15.207.100.108:8086
- **Grafana**: http://15.207.100.108:3000 (admin/admin123)

### 💻 Using Traycer on AWS

#### Method 1: VS Code Remote + Traycer Extension
1. Connect to AWS via VS Code Remote-SSH
2. Install Traycer extension in the remote VS Code
3. Open your Bhashini project folder
4. Use Traycer as usual - it will run on AWS resources!

#### Method 2: Terminal + Traycer CLI
1. SSH to your AWS instance
2. Install Traycer CLI: `npm install -g @traycer/cli`
3. Navigate to your project: `cd ~/bhashini-project`
4. Use Traycer commands - all processing happens on AWS

#### Method 3: Web-based Traycer
1. Access Traycer web interface from your AWS instance
2. All AI processing happens on AWS servers
3. Your local machine just displays the web interface

### 🔧 Development Workflow

#### 1. Start Development Session
```bash
ssh -i ~/.ssh/bhashini-dev-key.pem ubuntu@15.207.100.108
cd ~/bhashini-project
./setup-dev-env.sh
```

#### 2. Code with Traycer
- Open VS Code with Remote-SSH
- Install Traycer extension
- Code, debug, and use AI assistance - all on AWS!

#### 3. Test Your Changes
```bash
# Run tests
python3 -m pytest

# Start services
sudo docker-compose -f docker-compose-simple.yml up -d

# View logs
sudo docker-compose -f docker-compose-simple.yml logs -f
```

### 💰 Cost Optimization
- **Stop instance when not using**: `aws ec2 stop-instances --instance-ids i-0616810ba3843819e`
- **Start when needed**: `aws ec2 start-instances --instance-ids i-0616810ba3843819e`
- **Estimated cost**: ~$0.166/hour when running

### 🚨 Important Notes
1. **Always stop the instance** when not developing to save costs
2. **Your code is safe** - it's stored in the project folder
3. **Use SSH key** for secure access
4. **Port 22 (SSH)** and **ports 3000, 8086** are open

### 🔍 Troubleshooting

#### Can't connect via SSH?
```bash
# Check instance status
aws ec2 describe-instances --instance-ids i-0616810ba3843819e

# Check security group
aws ec2 describe-security-groups --group-names triton-server-sg
```

#### Services not starting?
```bash
# Check Docker status
sudo docker ps
sudo docker-compose -f docker-compose-simple.yml logs

# Restart services
sudo docker-compose -f docker-compose-simple.yml restart
```

### 🎯 Next Steps
1. **Connect via SSH** to verify everything works
2. **Set up VS Code Remote-SSH** for full IDE experience
3. **Install Traycer** in your remote environment
4. **Start coding** with full AWS resources at your disposal!

---

## 🎉 You're All Set!

You now have a powerful AWS development environment that:
- ✅ Uses **ZERO** local resources
- ✅ Provides **4 vCPUs + 16GB RAM** for development
- ✅ Runs your entire Bhashini stack
- ✅ Supports VS Code Remote development
- ✅ Can run Traycer and other AI tools on AWS

**Happy coding on the cloud! 🚀**
