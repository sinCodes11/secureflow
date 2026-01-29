#!/bin/bash

# SecureFlow Setup Script
# Automated setup for n8n Security Incident Response Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="SecureFlow"
MIN_DOCKER_VERSION="20.10.0"
MIN_DOCKER_COMPOSE_VERSION="2.0.0"

# Helper functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check Docker version
    DOCKER_VERSION=$(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    if [ "$(printf '%s\n' "$MIN_DOCKER_VERSION" "$DOCKER_VERSION" | sort -V | head -n1)" != "$MIN_DOCKER_VERSION" ]; then
        print_warning "Docker version $DOCKER_VERSION is below recommended $MIN_DOCKER_VERSION"
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Check available ports
    local ports=(5678 8000 5432 6379 9090 3000 80)
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_warning "Port $port is already in use. This may cause conflicts."
        fi
    done
    
    print_success "Prerequisites check completed"
}

# Create environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_success "Created .env file from template"
        print_warning "Please review and update the .env file with your actual API keys"
    else
        print_warning ".env file already exists, skipping creation"
    fi
}

# Create directory structure
create_directories() {
    print_status "Creating directory structure..."
    
    mkdir -p logs
    mkdir -p data/postgres
    mkdir -p data/redis
    mkdir -p data/grafana
    mkdir -p data/prometheus
    mkdir -p backups
    mkdir -p exports
    
    print_success "Directory structure created"
}

# Build and start services
start_services() {
    print_status "Building and starting SecureFlow services..."
    
    # Build the mock APIs image
    docker-compose build mock-apis
    
    # Start all services
    docker-compose up -d
    
    print_success "All services started successfully"
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    local services=("postgres" "redis" "mock-apis" "n8n")
    local max_attempts=30
    local attempt=1
    
    for service in "${services[@]}"; do
        print_status "Waiting for $service..."
        
        while [ $attempt -le $max_attempts ]; do
            if docker-compose ps $service | grep -q "Up (healthy)"; then
                print_success "$service is ready"
                break
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                print_error "$service failed to start within expected time"
                echo "Check logs with: docker-compose logs $service"
                exit 1
            fi
            
            echo -n "."
            sleep 2
            ((attempt++))
        done
    done
    
    print_success "All services are ready"
}

# Import n8n workflows
import_workflows() {
    print_status "Importing n8n workflows..."
    
    # Wait a bit for n8n to fully start
    sleep 10
    
    # Import each workflow
    local workflows=(
        "malware-response.json"
        "brute-force-mitigation.json"
        "data-exfiltration.json"
        "cloud-misconfiguration.json"
        "phishing-analysis.json"
        "suspicious-login.json"
    )
    
    for workflow in "${workflows[@]}"; do
        if [ -f "workflows/$workflow" ]; then
            print_status "Importing $workflow..."
            # Note: In production, you'd use n8n API to import workflows
            # For demo, we're just copying to the workflows volume
            cp "workflows/$workflow" "data/n8n-workflows/"
        else
            print_warning "Workflow file not found: $workflow"
        fi
    done
    
    print_success "Workflow files copied to data directory"
}

# Setup monitoring dashboards
setup_monitoring() {
    print_status "Setting up monitoring dashboards..."
    
    # Create Grafana dashboard configuration
    cat > monitoring/grafana/dashboards/secureflow-dashboard.yml << EOF
apiVersion: 1

providers:
  - name: 'secureflow'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards/secureflow-dashboard.json
EOF
    
    print_success "Monitoring dashboards configured"
}

# Verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Check if all services are running
    local services=("postgres" "redis" "mock-apis" "n8n" "prometheus" "grafana")
    
    for service in "${services[@]}"; do
        if docker-compose ps $service | grep -q "Up"; then
            print_success "$service is running"
        else
            print_error "$service is not running"
            exit 1
        fi
    done
    
    # Test API endpoints
    print_status "Testing API endpoints..."
    
    # Test mock APIs health check
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "Mock APIs are responding"
    else
        print_warning "Mock APIs are not responding yet"
    fi
    
    # Test PostgreSQL connection
    if docker-compose exec -T postgres psql -U secureflow -d secureflow -c "SELECT 1;" > /dev/null 2>&1; then
        print_success "PostgreSQL is accessible"
    else
        print_warning "PostgreSQL connection test failed"
    fi
}

# Display next steps
show_next_steps() {
    print_success "SecureFlow setup completed successfully!"
    
    echo
    echo -e "${BLUE}=== Access Information ===${NC}"
    echo -e "n8n Workflow Editor: ${GREEN}http://localhost:5678${NC}"
    echo -e "Username: ${YELLOW}admin${NC}"
    echo -e "Password: ${YELLOW}secureflow2026${NC}"
    echo
    echo -e "Mock APIs Documentation: ${GREEN}http://localhost:8000/api/docs${NC}"
    echo -e "Prometheus Metrics: ${GREEN}http://localhost:9090${NC}"
    echo -e "Grafana Dashboards: ${GREEN}http://localhost:3000${NC}"
    echo -e "Username: ${YELLOW}admin${NC}"
    echo -e "Password: ${YELLOW}secureflow2026${NC}"
    echo
    echo -e "${BLUE}=== Next Steps ===${NC}"
    echo "1. Visit n8n interface and import the workflow JSON files"
    echo "2. Update the .env file with your actual API keys"
    echo "3. Test the workflows using the provided test scripts"
    echo "4. Configure webhook endpoints in your security tools"
    echo
    echo -e "${BLUE}=== Useful Commands ===${NC}"
    echo "View logs: docker-compose logs -f [service_name]"
    echo "Stop services: docker-compose down"
    echo "Restart services: docker-compose restart"
    echo "Check status: docker-compose ps"
    echo
    echo -e "${BLUE}=== Test Workflows ===${NC}"
    echo "Run test script: ./scripts/test-workflows.sh"
    echo "Generate test data: ./scripts/generate-test-data.py"
    echo
}

# Main execution
main() {
    echo -e "${BLUE}=== SecureFlow Setup Script ===${NC}"
    echo
    
    check_prerequisites
    setup_environment
    create_directories
    start_services
    wait_for_services
    import_workflows
    setup_monitoring
    verify_installation
    show_next_steps
}

# Handle script interruption
trap 'print_error "Setup interrupted. Check logs and clean up manually."' INT

# Run main function
main "$@"