# 🚀 Deployment Guide

## Tổng quan triển khai

ERP AI Pro Version được thiết kế để triển khai linh hoạt từ môi trường development đến production scale với Docker, Kubernetes và cloud platforms.

## 📋 Prerequisites

### System Requirements

#### Minimum Requirements
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 20GB SSD
- **GPU**: Optional (NVIDIA RTX 4060 or better for optimal performance)

#### Recommended Requirements
- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Storage**: 50GB+ SSD
- **GPU**: NVIDIA RTX 4080/RTX A4000 or better

### Software Dependencies

```bash
# Required
- Python 3.10+
- Docker 20.10+
- Docker Compose 2.0+

# Optional (for production)
- Kubernetes 1.25+
- Terraform 1.0+
- Helm 3.0+
```

## 🐳 Docker Deployment

### 1. Build Docker Image

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.pro.txt .
RUN pip install --no-cache-dir -r requirements.pro.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Build và Run

```bash
# Build image
docker build -t erp-ai-pro:latest .

# Run container
docker run -d \
  --name erp-ai-pro \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.env:/app/.env \
  --restart unless-stopped \
  erp-ai-pro:latest
```

### 3. Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  erp-ai-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./data:/app/data
      - ./.env:/app/.env
    depends_on:
      - neo4j
      - redis
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

  neo4j:
    image: neo4j:5.15-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/your_password
      - NEO4J_PLUGINS=["apoc"]
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - erp-ai-api
    restart: unless-stopped

volumes:
  neo4j_data:
  neo4j_logs:
  redis_data:
```

### 4. Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f erp-ai-api

# Check status
docker-compose ps
```

## ☸️ Kubernetes Deployment

### 1. Kubernetes Manifests

#### Namespace
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: erp-ai-pro
```

#### ConfigMap
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: erp-ai-config
  namespace: erp-ai-pro
data:
  PYTHONPATH: "/app"
  NEO4J_URI: "bolt://neo4j:7687"
  REDIS_URL: "redis://redis:6379"
```

#### Secret
```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: erp-ai-secret
  namespace: erp-ai-pro
type: Opaque
data:
  neo4j-password: <base64-encoded-password>
  api-token: <base64-encoded-token>
```

#### Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: erp-ai-api
  namespace: erp-ai-pro
spec:
  replicas: 3
  selector:
    matchLabels:
      app: erp-ai-api
  template:
    metadata:
      labels:
        app: erp-ai-api
    spec:
      containers:
      - name: erp-ai-api
        image: erp-ai-pro:latest
        ports:
        - containerPort: 8000
        env:
        - name: NEO4J_PASSWORD
          valueFrom:
            secretKeyRef:
              name: erp-ai-secret
              key: neo4j-password
        envFrom:
        - configMapRef:
            name: erp-ai-config
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### Service
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: erp-ai-service
  namespace: erp-ai-pro
spec:
  selector:
    app: erp-ai-api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

#### Ingress
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: erp-ai-ingress
  namespace: erp-ai-pro
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.erp-ai-pro.com
    secretName: erp-ai-tls
  rules:
  - host: api.erp-ai-pro.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: erp-ai-service
            port:
              number: 80
```

### 2. Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n erp-ai-pro
kubectl get svc -n erp-ai-pro
kubectl get ingress -n erp-ai-pro

# View logs
kubectl logs -f deployment/erp-ai-api -n erp-ai-pro
```

## ☁️ Cloud Deployment

### AWS EKS Deployment

#### 1. Terraform Infrastructure

```hcl
# infrastructure/main.tf
provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "erp-ai-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["${var.aws_region}a", "${var.aws_region}b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]
  
  enable_nat_gateway = true
  enable_vpn_gateway = true
}

module "eks" {
  source = "terraform-aws-modules/eks/aws"
  
  cluster_name    = "erp-ai-cluster"
  cluster_version = "1.25"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  
  node_groups = {
    main = {
      desired_capacity = 3
      max_capacity     = 10
      min_capacity     = 1
      
      instance_types = ["m5.large"]
      
      k8s_labels = {
        Environment = var.environment
        Application = "erp-ai-pro"
      }
    }
  }
}
```

#### 2. Deploy Infrastructure

```bash
# Initialize Terraform
cd infrastructure
terraform init

# Plan deployment
terraform plan -var="aws_region=us-west-2" -var="environment=production"

# Apply infrastructure
terraform apply

# Configure kubectl
aws eks update-kubeconfig --region us-west-2 --name erp-ai-cluster
```

### Google Cloud GKE Deployment

```bash
# Create GKE cluster
gcloud container clusters create erp-ai-cluster \
    --zone=us-central1-a \
    --machine-type=n1-standard-4 \
    --num-nodes=3 \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=10

# Get credentials
gcloud container clusters get-credentials erp-ai-cluster --zone=us-central1-a

# Deploy application
kubectl apply -f k8s/
```

## 🔧 Environment Configuration

### Development Environment

```bash
# .env.development
DEBUG=true
LOG_LEVEL=DEBUG
BASE_MODEL_NAME=google/flan-t5-small
VECTOR_STORE_PATH=./data/dev_vector_store
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=dev_password
```

### Staging Environment

```bash
# .env.staging
DEBUG=false
LOG_LEVEL=INFO
BASE_MODEL_NAME=google/flan-t5-base
VECTOR_STORE_PATH=/app/data/staging_vector_store
NEO4J_URI=bolt://neo4j-staging:7687
FINETUNED_MODEL_PATH=/app/models/staging_model
```

### Production Environment

```bash
# .env.production
DEBUG=false
LOG_LEVEL=WARNING
BASE_MODEL_NAME=google/flan-t5-large
VECTOR_STORE_PATH=/app/data/prod_vector_store
NEO4J_URI=bolt://neo4j-prod:7687
FINETUNED_MODEL_PATH=/app/models/prod_model
REDIS_URL=redis://redis-cluster:6379
```

## 📊 Monitoring & Logging

### Prometheus Monitoring

```yaml
# monitoring/prometheus.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'erp-ai-api'
      static_configs:
      - targets: ['erp-ai-service:80']
      metrics_path: /metrics
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "ERP AI Pro Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)"
          }
        ]
      }
    ]
  }
}
```

### ELK Stack Logging

```yaml
# logging/filebeat.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: filebeat-config
data:
  filebeat.yml: |
    filebeat.inputs:
    - type: container
      paths:
        - /var/log/containers/*erp-ai*.log
    output.elasticsearch:
      hosts: ["elasticsearch:9200"]
    setup.kibana:
      host: "kibana:5601"
```

## 🔒 Security Hardening

### Container Security

```dockerfile
# Security-hardened Dockerfile
FROM python:3.10-slim

# Update and install security patches
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set secure permissions
COPY --chown=appuser:appuser . /app
USER appuser
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.pro.txt

# Remove unnecessary files
RUN find /app -name "*.pyc" -delete \
    && find /app -name "__pycache__" -delete

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Network Policies

```yaml
# security/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: erp-ai-network-policy
  namespace: erp-ai-pro
spec:
  podSelector:
    matchLabels:
      app: erp-ai-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: nginx-ingress
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: neo4j
    ports:
    - protocol: TCP
      port: 7687
```

## 🚀 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy ERP AI Pro

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        pip install -r requirements.pro.txt
    - name: Run tests
      run: |
        python -m pytest tests/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Build Docker image
      run: |
        docker build -t erp-ai-pro:${{ github.sha }} .
    - name: Push to registry
      run: |
        docker tag erp-ai-pro:${{ github.sha }} ${{ secrets.DOCKER_REGISTRY }}/erp-ai-pro:${{ github.sha }}
        docker push ${{ secrets.DOCKER_REGISTRY }}/erp-ai-pro:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/erp-ai-api erp-ai-api=${{ secrets.DOCKER_REGISTRY }}/erp-ai-pro:${{ github.sha }}
        kubectl rollout status deployment/erp-ai-api
```

## 📈 Scaling Strategies

### Horizontal Pod Autoscaler

```yaml
# scaling/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: erp-ai-hpa
  namespace: erp-ai-pro
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: erp-ai-api
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Vertical Pod Autoscaler

```yaml
# scaling/vpa.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: erp-ai-vpa
  namespace: erp-ai-pro
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: erp-ai-api
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: erp-ai-api
      maxAllowed:
        cpu: 4
        memory: 8Gi
      minAllowed:
        cpu: 100m
        memory: 512Mi
```

## 🔄 Backup & Recovery

### Database Backup

```bash
#!/bin/bash
# scripts/backup.sh

# Neo4j backup
docker exec neo4j neo4j-admin backup \
  --from=bolt://localhost:7687 \
  --backup-dir=/backups \
  --name=neo4j-backup-$(date +%Y%m%d-%H%M%S)

# Vector store backup
tar -czf /backups/vector-store-$(date +%Y%m%d-%H%M%S).tar.gz ./data/vector_store

# Upload to S3
aws s3 sync /backups s3://erp-ai-backups/
```

### Disaster Recovery

```bash
#!/bin/bash
# scripts/restore.sh

# Restore Neo4j
docker exec neo4j neo4j-admin restore \
  --from=/backups/neo4j-backup-latest \
  --database=neo4j

# Restore vector store
tar -xzf /backups/vector-store-latest.tar.gz -C ./data/
```

## 📋 Troubleshooting

### Common Issues

1. **Out of Memory Errors**
   ```bash
   # Increase memory limits
   docker run -m 8g erp-ai-pro:latest
   ```

2. **Model Loading Timeouts**
   ```python
   # Increase timeout in config
   MODEL_LOAD_TIMEOUT = 300  # 5 minutes
   ```

3. **Database Connection Issues**
   ```bash
   # Check Neo4j connectivity
   docker exec neo4j cypher-shell -u neo4j -p password "MATCH (n) RETURN count(n);"
   ```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database health
docker exec neo4j cypher-shell -u neo4j -p password "CALL dbms.components();"

# Resource usage
docker stats erp-ai-pro
```