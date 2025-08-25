#!/bin/bash
# Bhashini QoS Monitoring Stack Setup Script

set -e

echo "🚀 Bhashini QoS Monitoring Stack Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if Docker is installed
echo "🔍 Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_status "Docker is installed"

# Check if Docker Compose is installed
echo "🔍 Checking Docker Compose installation..."
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
print_status "Docker Compose is installed"

# Check if Docker daemon is running
echo "🔍 Checking Docker daemon..."
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running. Please start Docker first."
    exit 1
fi
print_status "Docker daemon is running"

# Create .env file if it doesn't exist
echo "📝 Setting up environment configuration..."
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        print_status "Created .env file from .env.example"
        print_warning "Please update .env file with your secure passwords and tokens"
    else
        print_error ".env.example file not found. Please create .env file manually."
        exit 1
    fi
else
    print_status ".env file already exists"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data-simulator
mkdir -p influxdb/init-scripts
mkdir -p grafana/provisioning/datasources
mkdir -p scripts
mkdir -p secrets
print_status "Directories created"

# Create placeholder token file
echo "🔐 Creating placeholder token file..."
: > secrets/influxdb_tokens.env
print_status "Placeholder token file created"

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x scripts/*.py 2>/dev/null || true
chmod +x influxdb/init-scripts/*.sh 2>/dev/null || true
chmod +x scripts/setup.sh 2>/dev/null || true
print_status "Scripts made executable"

# Validate environment file
echo "🔍 Validating environment configuration..."
if [ -f .env ]; then
    # Check for required variables
    required_vars=(
        "INFLUXDB_ADMIN_USER"
        "INFLUXDB_ADMIN_PASSWORD"
        "INFLUXDB_ORG"
        "INFLUXDB_BUCKET"
        "GRAFANA_ADMIN_USER"
        "GRAFANA_ADMIN_PASSWORD"
    )
    
    missing_vars=()
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env || grep -q "^${var}=$" .env; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -eq 0 ]; then
        print_status "Environment configuration is valid"
    else
        print_warning "Missing or empty environment variables: ${missing_vars[*]}"
        print_warning "Please update your .env file with proper values"
    fi
fi

# Check if ports are available
echo "🔍 Checking port availability..."
ports_to_check=(3000 8086)
for port in "${ports_to_check[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $port is already in use. Please ensure it's available for the stack."
    else
        print_status "Port $port is available"
    fi
done

# Provide next steps
echo ""
echo "🎯 Setup Complete! Next Steps:"
echo "==============================="
echo "1. Update your .env file with secure passwords and tokens"
echo "2. Run the stack: docker-compose up -d"
echo "3. Wait for services to start (check with: docker-compose ps)"
echo "4. Access services:"
echo "   - Grafana: http://localhost:3000"
echo "   - InfluxDB: http://localhost:8086"
echo "5. Run verification: python scripts/verify-data-flow.py"
echo ""
echo "📚 For more information, see README.md"
echo ""

# Check if user wants to start the stack
read -p "Would you like to start the stack now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting Bhashini QoS Monitoring Stack with staged startup..."
    
    # Create secrets directory and placeholder
    echo "🔐 Setting up secrets directory..."
    mkdir -p secrets
    : > secrets/influxdb_tokens.env
    print_status "Secrets directory created with placeholder token file"
    
    # Start only InfluxDB first
    echo "🚀 Starting InfluxDB service..."
    docker-compose up -d influxdb
    print_status "InfluxDB service started"
    
    # Wait for tokens file to be populated
    echo "⏳ Waiting for InfluxDB to generate tokens..."
    until [ -s secrets/influxdb_tokens.env ]; do 
        echo 'Waiting for tokens...'; 
        sleep 2; 
    done
    print_status "Tokens generated successfully"
    
    # Start remaining services
    echo "🚀 Starting remaining services..."
    docker-compose up -d grafana data-simulator
    print_status "All Docker services started successfully"
    
    echo ""
    echo "⏳ Services are starting up. This may take a few minutes..."
    echo "Check status with: docker-compose ps"
    echo "View logs with: docker-compose logs -f"
else
    echo "📋 Stack not started. Run 'docker-compose up -d' when ready."
fi

print_status "Setup completed successfully!"
