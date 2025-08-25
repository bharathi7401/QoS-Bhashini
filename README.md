# Bhashini QoS Monitoring Stack

A comprehensive monitoring infrastructure for Bhashini AI services (Translation, TTS, ASR) with realistic QoS metrics simulation and multi-tenant data isolation.

## 🏗️ Architecture

The system consists of three main components orchestrated via Docker Compose:

- **InfluxDB 2.7**: Time-series database for storing QoS metrics with multi-tenant schema
- **Grafana 10.2**: Visualization and dashboard platform for metrics analysis
- **Python Data Simulator**: Generates realistic QoS metrics using statistical distributions

### Data Flow

```
Data Simulator → InfluxDB → Grafana
     ↓              ↓         ↓
  Generates    Stores      Visualizes
  Metrics      Time-      Multi-tenant
  Every 10s    Series     Dashboards
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for verification scripts)

### 1. Clone Repository
```bash
git clone <repository-url>
cd QoS-Bhashini
```

### 2. Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Update with your secure passwords and tokens
# Edit .env file
```

### 3. Start Stack
```bash
# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 4. Access Services
- **Grafana**: http://localhost:3000 (admin/admin123)
- **InfluxDB**: http://localhost:8086
- **Data Simulator Health**: http://localhost:8000/health

### 5. Run verification
```bash
python scripts/verify-data-flow.py
```

## ☁️ AWS Deployment

For production use or to free up local resources, deploy to AWS:

### Quick AWS Setup
```bash
cd aws
chmod +x deploy.sh
./deploy.sh
```

### AWS Features
- **ECS Fargate**: Serverless container management
- **EFS**: Persistent storage for data
- **CloudWatch**: Centralized logging and monitoring
- **ALB**: Public access to Grafana
- **VPC**: Isolated network architecture

### AWS Access
After deployment, access your stack via:
- **Grafana**: http://[ALB-DNS-NAME] (admin/admin123)
- **CloudWatch Logs**: AWS Console
- **ECS Console**: AWS Console

See [aws/README.md](aws/README.md) for detailed AWS deployment instructions.

## 📊 Metrics Schema

### Multi-Tenant Design

The system uses InfluxDB tags for tenant isolation and metadata:

```flux
measurement: qos_metrics
tags:
  - tenant_id: enterprise_1, startup_1, freemium_1
  - service_name: translation, tts, asr
  - metric_type: latency, error_rate, throughput, availability
  - sla_tier: premium, standard, basic
fields:
  - value: numeric metric value
  - unit: measurement unit (ms, percentage, requests_per_minute)
```

### Metric Types

- **Latency**: API response time in milliseconds (Gaussian distribution)
- **Error Rate**: Percentage of failed requests (Probability-based)
- **Throughput**: Requests per minute (Poisson distribution)
- **Availability**: Service uptime percentage

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `INFLUXDB_ADMIN_USER` | InfluxDB admin username | admin |
| `INFLUXDB_ADMIN_PASSWORD` | InfluxDB admin password | - |
| `INFLUXDB_ORG` | Organization name | bhashini |
| `INFLUXDB_BUCKET` | Metrics bucket name | qos_metrics |
| `GRAFANA_ADMIN_USER` | Grafana admin username | admin |
| `GRAFANA_ADMIN_PASSWORD` | Grafana admin password | - |
| `SIMULATION_INTERVAL` | Metrics generation interval (seconds) | 10 |
| `LOG_LEVEL` | Logging level | INFO |

### Service Configuration

The data simulator includes realistic configurations for Bhashini services:

- **Translation Service**: 150ms mean latency, 2% base error rate
- **TTS Service**: 200ms mean latency, 1.5% base error rate  
- **ASR Service**: 180ms mean latency, 2.5% base error rate

### Tenant Profiles

- **Enterprise**: Premium SLA with 20% better performance
- **Startup**: Standard SLA with baseline performance
- **Freemium**: Basic SLA with reduced performance

## 📈 Usage Examples

### Viewing Metrics in Grafana

1. Login to Grafana (http://localhost:3000)
2. Navigate to Explore
3. Select InfluxDB-QoS-Metrics data source
4. Use Flux queries like:

```flux
from(bucket: "qos_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
  |> filter(fn: (r) => r["tenant_id"] == "enterprise_1")
  |> filter(fn: (r) => r["metric_type"] == "latency")
```

### Custom Queries

**Service Performance Comparison**:
```flux
from(bucket: "qos_metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
  |> filter(fn: (r) => r["metric_type"] == "latency")
  |> group(columns: ["service_name"])
  |> mean()
```

**Tenant SLA Compliance**:
```flux
from(bucket: "qos_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "qos_metrics")
  |> filter(fn: (r) => r["metric_type"] == "availability")
  |> group(columns: ["tenant_id", "sla_tier"])
  |> mean()
```

## 🧪 Testing and Verification

### Automated Verification

Run the verification script to test the complete data flow:

```bash
python scripts/verify-data-flow.py
```

Tests include:
- ✅ InfluxDB connectivity
- ✅ Data ingestion verification
- ✅ Schema validation
- ✅ Multi-tenant isolation
- ✅ Service coverage

### Manual Testing

1. **Check service health**:
   ```bash
   docker-compose ps
   curl http://localhost:8000/health
   ```

2. **View logs**:
   ```bash
   docker-compose logs -f data-simulator
   docker-compose logs -f influxdb
   docker-compose logs -f grafana
   ```

3. **Query InfluxDB directly**:
   ```bash
   docker exec -it bhashini-influxdb influx query \
     --org bhashini \
     --token $INFLUXDB_ADMIN_TOKEN \
     'from(bucket:"qos_metrics") |> range(start: -5m) |> count()'
   ```

## 🏥 Health Checks

The system provides health endpoints for monitoring:

- **Grafana**: http://localhost:3000/api/health
- **InfluxDB**: http://localhost:8086/health  
- **Data Simulator**: http://localhost:8000/health

The data simulator health endpoint provides:
- **Liveness**: Always returns `ok` if the process is running
- **Readiness**: Returns `ready` when connected to InfluxDB, `not_ready` otherwise
- **Status**: Current simulation state and metrics generation count

## 🔒 Security

- **Multi-tenant isolation** via InfluxDB tags
- **Service-specific tokens** with minimal required permissions
- **Non-root containers** for security
- **Environment-based configuration** for sensitive data

## 📁 Project Structure

```
QoS-Bhashini/
├── docker-compose.yml          # Main orchestration
├── data-simulator/            # Python metrics generator
│   ├── Dockerfile            # Container definition
│   ├── requirements.txt      # Python dependencies
│   ├── main.py              # Main application
│   ├── config.py            # Configuration management
│   ├── metrics_generator.py # Metrics generation logic
│   └── influx_client.py     # InfluxDB client wrapper
├── influxdb/                 # InfluxDB configuration
│   └── init-scripts/        # Initialization scripts
├── grafana/                  # Grafana configuration
│   └── provisioning/        # Auto-provisioning
├── scripts/                  # Utility scripts
├── env.example              # Environment template
└── README.md                # This file
```

## 🚨 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000 and 8086 are available
2. **Permission errors**: Check Docker permissions and file ownership
3. **Connection failures**: Verify InfluxDB is fully started before simulator
4. **Token issues**: Regenerate tokens if authentication fails

### Debug Commands

```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs -f [service-name]

# Restart specific service
docker-compose restart [service-name]

# Access container shell
docker exec -it bhashini-influxdb /bin/bash
docker exec -it bhashini-data-simulator /bin/bash

# Check InfluxDB health
curl http://localhost:8086/health

# Verify data flow
python scripts/verify-data-flow.py
```

## 📚 Additional Resources

- [InfluxDB Documentation](https://docs.influxdata.com/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Flux Query Language](https://docs.influxdata.com/flux/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note**: This is a development/testing environment. For production use, ensure proper security measures, monitoring, and backup strategies are in place.
