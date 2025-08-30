# Bhashini QoS Dashboards - Public Access

This directory contains a public web portal for accessing Bhashini's QoS monitoring dashboards.

## 🚀 Quick Start

### 1. Start the Public Server
```bash
cd public-dashboard
python server.py
```

The server will start on port 8080 by default.

### 2. Access the Portal
Open your browser and navigate to:
- **Local access**: http://localhost:8080
- **Network access**: http://YOUR_IP_ADDRESS:8080

### 3. View Dashboards
Click on any dashboard card to open the corresponding Grafana dashboard in a new tab.

## 🌐 Public Access

### Local Network Access
- The server binds to `0.0.0.0:8080` for public network access
- Other devices on your network can access using your computer's IP address
- Example: `http://192.168.1.100:8080`

### Internet Access (Optional)
To make dashboards accessible from the internet:

1. **Port Forwarding**: Configure your router to forward port 8080 to your computer
2. **Dynamic DNS**: Use a service like No-IP for dynamic IP addresses
3. **Cloud Deployment**: Deploy to AWS, Google Cloud, or similar services

## 📊 Available Dashboards

### 1. Ultimate QoS Dashboard
- **URL**: `/d/be149f0f-0844-4616-83c5-3e896d6aa98b/bhashini-ultimate-qos-dashboard-v2`
- **Features**: Comprehensive overview, top 5/worst 5 customers, service performance

### 2. Customer Overview Dashboard
- **URL**: `/d/bhashini-customer-overview/bhashini-customer-overview-dashboard`
- **Features**: Side-by-side customer comparison, all metrics in one view

### 3. Individual Customer Dashboards
- **Enterprise 1**: Premium SLA monitoring (99% availability, <100ms response)
- **Startup 1**: Standard SLA monitoring (95% availability, <200ms response)
- **Freemium 1**: Basic SLA monitoring (90% availability, <500ms response)

### 4. Provider Overview
- **URL**: `/d/bhashini-provider-overview/bhashini-provider-overview`
- **Features**: Cross-tenant analytics, capacity planning, business intelligence

## 🔧 Configuration

### Change Port
```bash
python server.py --port 9000
```

### Environment Variables
- `PORT`: Server port (default: 8080)
- `HOST`: Bind address (default: 0.0.0.0)

### Customization
- Edit `index.html` to modify the portal appearance
- Update dashboard URLs in the HTML file
- Add new dashboard cards as needed

## 🚨 Security Considerations

### Current Setup (Development)
- No authentication required
- Accessible to anyone on the network
- Suitable for internal/trusted networks only

### Production Recommendations
1. **Authentication**: Implement login system
2. **HTTPS**: Use SSL/TLS certificates
3. **Firewall**: Restrict access to specific IP ranges
4. **Rate Limiting**: Prevent abuse
5. **Monitoring**: Log access attempts

## 📱 Mobile Access

The portal is responsive and works on mobile devices:
- Responsive grid layout
- Touch-friendly interface
- Optimized for small screens

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Find what's using the port
lsof -i :8080

# Kill the process
kill -9 <PID>

# Or use a different port
python server.py --port 8081
```

### Can't Access from Other Devices
1. Check firewall settings
2. Verify network connectivity
3. Use correct IP address
4. Ensure server is bound to `0.0.0.0`

### Dashboard Links Not Working
1. Verify Grafana is running on port 3010
2. Check dashboard UIDs are correct
3. Ensure Grafana is accessible from the network

## 📞 Support

For issues or questions:
- Check Grafana logs: `docker-compose logs grafana`
- Verify dashboard provisioning
- Check network connectivity
- Contact: support@bhashini.com

## 🚀 Deployment Options

### 1. Local Development
```bash
python server.py
```

### 2. Docker Deployment
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
EXPOSE 8080
CMD ["python", "server.py"]
```

### 3. Cloud Deployment
- **AWS**: EC2 + Application Load Balancer
- **Google Cloud**: Compute Engine + Cloud Load Balancing
- **Azure**: Virtual Machine + Application Gateway

### 4. Reverse Proxy
Use Nginx or Apache as a reverse proxy:
```nginx
server {
    listen 80;
    server_name dashboards.bhashini.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📈 Monitoring the Portal

### Access Logs
The server logs all requests to stdout. Monitor with:
```bash
python server.py | tee access.log
```

### Health Checks
Add a health check endpoint:
```bash
curl http://localhost:8080/health
```

### Performance
- Monitor response times
- Check concurrent connections
- Monitor resource usage

---

**Note**: This is a development setup. For production use, implement proper security measures and consider using a production-grade web server like Nginx or Apache.
