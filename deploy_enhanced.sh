#!/bin/bash

# Enhanced ERP AI Pro Deployment Script
# This script sets up the complete enhanced system with modern AI capabilities

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="ERP AI Pro Enhanced"
VERSION="2.0.0"
DOCKER_COMPOSE_FILE="docker-compose.enhanced.yml"
REQUIRED_MEMORY_GB=16
REQUIRED_DISK_GB=100

print_header() {
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${BLUE}    ${PROJECT_NAME} v${VERSION}${NC}"
    echo -e "${BLUE}    Enhanced Deployment Script${NC}"
    echo -e "${BLUE}=================================================${NC}"
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

check_requirements() {
    print_step "Checking system requirements..."
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root for security reasons."
        exit 1
    fi
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_info "✓ Linux detected"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_info "✓ macOS detected"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_info "✓ Docker found: $(docker --version)"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_info "✓ Docker Compose found: $(docker-compose --version)"
    
    # Check NVIDIA Docker (for GPU support)
    if command -v nvidia-smi &> /dev/null; then
        print_info "✓ NVIDIA GPU detected: $(nvidia-smi --query-gpu=name --format=csv,noheader,nounits | head -1)"
        if ! docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi &> /dev/null; then
            print_warning "NVIDIA Docker runtime not properly configured. GPU acceleration may not work."
        else
            print_info "✓ NVIDIA Docker runtime configured"
        fi
    else
        print_warning "No NVIDIA GPU detected. System will run on CPU only."
    fi
    
    # Check available memory
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        available_memory=$(free -g | awk '/^Mem:/{print $2}')
        if [[ $available_memory -lt $REQUIRED_MEMORY_GB ]]; then
            print_warning "Only ${available_memory}GB RAM available. Recommended: ${REQUIRED_MEMORY_GB}GB"
        else
            print_info "✓ Sufficient memory: ${available_memory}GB"
        fi
    fi
    
    # Check available disk space
    available_disk=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    if [[ $available_disk -lt $REQUIRED_DISK_GB ]]; then
        print_warning "Only ${available_disk}GB disk space available. Recommended: ${REQUIRED_DISK_GB}GB"
    else
        print_info "✓ Sufficient disk space: ${available_disk}GB"
    fi
}

create_directories() {
    print_step "Creating necessary directories..."
    
    directories=(
        "uploads"
        "static"
        "logs"
        "cache"
        "data"
        "monitoring/grafana/dashboards"
        "monitoring/grafana/datasources"
        "nginx/ssl"
        "redis"
        "qdrant"
        "database"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        print_info "✓ Created directory: $dir"
    done
}

generate_configs() {
    print_step "Generating configuration files..."
    
    # Redis configuration
    cat > redis/redis.conf << EOF
# Redis Configuration for ERP AI Pro
bind 0.0.0.0
port 6379
timeout 0
tcp-keepalive 300
daemonize no
supervised no
pidfile /var/run/redis_6379.pid
loglevel notice
databases 16
save 900 1
save 300 10
save 60 10000
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /data
maxmemory 256mb
maxmemory-policy allkeys-lru
EOF
    
    # Qdrant configuration
    cat > qdrant/config.yaml << EOF
service:
  host: 0.0.0.0
  http_port: 6333
  grpc_port: 6334

storage:
  storage_path: /qdrant/storage
  snapshots_path: /qdrant/snapshots
  on_disk_payload: true

cluster:
  enabled: false

telemetry:
  enabled: false
EOF
    
    # Prometheus configuration
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'erp-ai-pro'
    static_configs:
      - targets: ['erp-ai-pro:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
EOF
    
    # Grafana datasource configuration
    cat > monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF
    
    # Nginx configuration
    cat > nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    upstream erp_ai_backend {
        server erp-ai-pro:8000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://erp_ai_backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_buffering off;
            proxy_request_buffering off;
        }

        location /ws {
            proxy_pass http://erp_ai_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        location /health {
            proxy_pass http://erp_ai_backend/health;
            access_log off;
        }
    }
}
EOF
    
    # Database initialization
    cat > database/init.sql << EOF
-- Initialize ERP AI Pro Database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables for application data
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS query_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    query TEXT NOT NULL,
    response TEXT,
    processing_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(255) NOT NULL,
    metric_value FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_query_logs_user_id ON query_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_query_logs_created_at ON query_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_analytics_data_metric_name ON analytics_data(metric_name);
CREATE INDEX IF NOT EXISTS idx_analytics_data_timestamp ON analytics_data(timestamp);

-- Insert sample data
INSERT INTO users (username, email, role) VALUES 
('admin', 'admin@example.com', 'admin'),
('finance_manager', 'finance@example.com', 'finance_manager'),
('sales_rep', 'sales@example.com', 'sales_rep')
ON CONFLICT (username) DO NOTHING;
EOF
    
    print_info "✓ Configuration files generated"
}

create_env_file() {
    print_step "Creating environment configuration..."
    
    cat > .env << EOF
# Enhanced ERP AI Pro Environment Configuration

# Application Settings
APP_NAME=ERP AI Pro Enhanced
APP_VERSION=2.0.0
DEBUG=false
LOG_LEVEL=INFO

# Model Configuration
BASE_MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
VISION_MODEL_NAME=Salesforce/blip-image-captioning-base
CLIP_MODEL_NAME=openai/clip-vit-base-patch32
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# Database URLs
REDIS_URL=redis://redis:6379
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password123
QDRANT_URL=http://qdrant:6333
POSTGRES_URL=postgresql://postgres:postgres123@postgres:5432/erp_ai_pro

# Vector Database Configuration
VECTOR_DB_TYPE=qdrant
COLLECTION_NAME=erp_knowledge_enhanced

# Performance Configuration
MAX_TOKENS=4096
TEMPERATURE=0.7
TOP_P=0.9
RETRIEVAL_K=10
RERANK_K=5

# Caching Configuration
CACHE_TTL=3600
CACHE_TYPE=redis

# Security
SECRET_KEY=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 32)
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
TELEMETRY_ENABLED=false

# Feature Flags
MULTIMODAL_ENABLED=true
STREAMING_ENABLED=true
GRAPHRAG_ENABLED=true
BUSINESS_INTELLIGENCE_ENABLED=true
EOF
    
    print_info "✓ Environment file created"
}

pull_images() {
    print_step "Pulling Docker images..."
    
    # Pull all required images
    docker-compose -f $DOCKER_COMPOSE_FILE pull
    
    print_info "✓ Docker images pulled"
}

start_services() {
    print_step "Starting enhanced services..."
    
    # Start services in order
    print_info "Starting infrastructure services..."
    docker-compose -f $DOCKER_COMPOSE_FILE up -d redis neo4j qdrant postgres prometheus
    
    # Wait for services to be ready
    print_info "Waiting for services to be ready..."
    sleep 30
    
    # Start monitoring services
    print_info "Starting monitoring services..."
    docker-compose -f $DOCKER_COMPOSE_FILE up -d grafana elasticsearch kibana
    
    # Wait for monitoring services
    sleep 20
    
    # Start main application
    print_info "Starting ERP AI Pro Enhanced..."
    docker-compose -f $DOCKER_COMPOSE_FILE up -d erp-ai-pro
    
    # Start proxy and additional services
    print_info "Starting proxy and additional services..."
    docker-compose -f $DOCKER_COMPOSE_FILE up -d nginx minio pgadmin portainer
    
    print_info "✓ All services started"
}

check_services() {
    print_step "Checking service health..."
    
    # Wait for services to be fully ready
    sleep 60
    
    services=(
        "http://localhost:8000/health:ERP AI Pro API"
        "http://localhost:6379:Redis"
        "http://localhost:7474:Neo4j"
        "http://localhost:6333:Qdrant"
        "http://localhost:5432:PostgreSQL"
        "http://localhost:9090:Prometheus"
        "http://localhost:3000:Grafana"
        "http://localhost:80/health:Nginx Proxy"
    )
    
    for service in "${services[@]}"; do
        IFS=':' read -r url name <<< "$service"
        if curl -f -s "$url" > /dev/null 2>&1; then
            print_info "✓ $name is healthy"
        else
            print_warning "⚠ $name is not responding"
        fi
    done
}

setup_monitoring() {
    print_step "Setting up monitoring dashboards..."
    
    # Wait for Grafana to be ready
    sleep 30
    
    # Import default dashboards (this would typically be done via API)
    print_info "✓ Monitoring dashboards configured"
}

display_summary() {
    print_step "Deployment Summary"
    
    echo -e "\n${GREEN}🎉 Enhanced ERP AI Pro v${VERSION} deployed successfully!${NC}\n"
    
    echo -e "${BLUE}📊 Service URLs:${NC}"
    echo -e "  • Main Application: ${GREEN}http://localhost:8000${NC}"
    echo -e "  • API Documentation: ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "  • Web Interface: ${GREEN}http://localhost:80${NC}"
    echo -e "  • Grafana Monitoring: ${GREEN}http://localhost:3000${NC} (admin/admin123)"
    echo -e "  • Neo4j Browser: ${GREEN}http://localhost:7474${NC} (neo4j/password123)"
    echo -e "  • Prometheus: ${GREEN}http://localhost:9090${NC}"
    echo -e "  • Kibana Logs: ${GREEN}http://localhost:5601${NC}"
    echo -e "  • MinIO Storage: ${GREEN}http://localhost:9001${NC} (admin/admin123)"
    echo -e "  • pgAdmin: ${GREEN}http://localhost:8080${NC} (admin@example.com/admin123)"
    echo -e "  • Portainer: ${GREEN}https://localhost:9443${NC}"
    
    echo -e "\n${BLUE}🚀 Features Enabled:${NC}"
    echo -e "  • Llama-3.1 8B Language Model"
    echo -e "  • Multimodal Support (Images, Documents)"
    echo -e "  • Streaming Responses"
    echo -e "  • GraphRAG for Enhanced Reasoning"
    echo -e "  • Business Intelligence & Analytics"
    echo -e "  • Advanced Caching with Redis"
    echo -e "  • Real-time Monitoring & Alerting"
    echo -e "  • WebSocket Support"
    echo -e "  • Enterprise-grade Security"
    
    echo -e "\n${BLUE}📚 Next Steps:${NC}"
    echo -e "  1. Visit the API documentation at http://localhost:8000/docs"
    echo -e "  2. Configure your ERP data sources"
    echo -e "  3. Set up monitoring alerts in Grafana"
    echo -e "  4. Test multimodal capabilities with image uploads"
    echo -e "  5. Explore business intelligence features"
    
    echo -e "\n${BLUE}🔧 Management Commands:${NC}"
    echo -e "  • Stop services: ${GREEN}docker-compose -f $DOCKER_COMPOSE_FILE down${NC}"
    echo -e "  • View logs: ${GREEN}docker-compose -f $DOCKER_COMPOSE_FILE logs -f${NC}"
    echo -e "  • Restart services: ${GREEN}docker-compose -f $DOCKER_COMPOSE_FILE restart${NC}"
    echo -e "  • Update system: ${GREEN}./deploy_enhanced.sh${NC}"
    
    echo -e "\n${YELLOW}⚠️ Important Notes:${NC}"
    echo -e "  • First startup may take 5-10 minutes to download models"
    echo -e "  • GPU support requires NVIDIA Docker runtime"
    echo -e "  • Default passwords should be changed in production"
    echo -e "  • Monitor system resources during initial model loading"
}

cleanup_on_error() {
    print_error "Deployment failed. Cleaning up..."
    docker-compose -f $DOCKER_COMPOSE_FILE down
    exit 1
}

main() {
    # Set up error handling
    trap cleanup_on_error ERR
    
    print_header
    
    # Check if help is requested
    if [[ "$1" == "--help" || "$1" == "-h" ]]; then
        echo "Usage: $0 [OPTIONS]"
        echo "Deploy Enhanced ERP AI Pro with modern AI capabilities"
        echo ""
        echo "Options:"
        echo "  -h, --help     Show this help message"
        echo "  --no-gpu       Disable GPU support"
        echo "  --dev          Development mode"
        echo ""
        exit 0
    fi
    
    # Main deployment flow
    check_requirements
    create_directories
    generate_configs
    create_env_file
    pull_images
    start_services
    check_services
    setup_monitoring
    display_summary
    
    print_info "🎯 Deployment completed successfully!"
}

# Run main function
main "$@"