# Deployment and Environment Configuration

## Overview

This document provides comprehensive guidance for deploying and configuring the AI Agent MCP Service Learning Project in various environments.

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Anthropic API Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=task_management
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/task_management

# Service Configuration
MCP_SERVICE_URL=http://mcp-service:8000
CREWAI_AGENT_URL=http://crewai-agent:8001

# pgAdmin Configuration
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=admin123

# Application Ports
MCP_SERVICE_PORT=8000
CREWAI_AGENT_PORT=8001
PGADMIN_PORT=8080
POSTGRES_PORT=5432
```

### Environment Setup Steps

1. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Configure Anthropic API Key**:
   - Sign up at [Anthropic Console](https://console.anthropic.com/)
   - Generate an API key
   - Add to `.env` file: `ANTHROPIC_API_KEY=sk-ant-...`

3. **Customize other variables** as needed for your environment

## Docker Deployment

### Prerequisites

- **Docker**: Version 20.0+ 
- **Docker Compose**: Version 2.0+
- **Available Ports**: 8000, 8001, 8080, 5432
- **System Resources**: 2GB RAM minimum, 4GB recommended

### Production Deployment

#### 1. Clone and Setup
```bash
# Clone repository
git clone <repository-url>
cd mcp_proj1

# Configure environment
cp .env.example .env
# Edit .env with your configuration
```

#### 2. Build and Deploy
```bash
# Build all services
docker-compose build

# Start services in detached mode
docker-compose up -d

# Verify all services are running
docker-compose ps
```

#### 3. Health Checks
```bash
# Check AI Agent service
curl http://localhost:8001/health

# Check MCP service
curl http://localhost:8000/health

# Check database connection via pgAdmin
# http://localhost:8080 (admin@example.com / admin123)
```

#### 4. Test End-to-End
```bash
# Test natural language processing
curl -X POST http://localhost:8001/agent/execute \
  -H "Content-Type: application/json" \
  -d '{"request": "Create a test project with sample tasks"}'
```

### Development Deployment

#### 1. Development with Hot Reload
```bash
# Start with build
docker-compose up --build

# View logs in real-time
docker-compose logs -f crewai-agent
docker-compose logs -f mcp-service
```

#### 2. Debugging Individual Services
```bash
# Run single service
docker-compose up postgres pgadmin
docker-compose up mcp-service

# Shell into service for debugging
docker-compose exec mcp-service bash
docker-compose exec crewai-agent bash
```

### Scaling and Load Balancing

#### Scale Services
```bash
# Scale AI agent service
docker-compose up --scale crewai-agent=3 -d

# Scale MCP service
docker-compose up --scale mcp-service=2 -d
```

#### Load Balancer Configuration
For production, use nginx or similar:

```nginx
upstream ai_agent_backend {
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}

upstream mcp_backend {
    server localhost:8000;
    server localhost:8010;
}

server {
    listen 80;
    
    location /agent/ {
        proxy_pass http://ai_agent_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /mcp/ {
        proxy_pass http://mcp_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Database Configuration

### PostgreSQL Setup

#### Connection Parameters
- **Host**: postgres (container) / localhost (external)
- **Port**: 5432
- **Database**: task_management
- **Username**: postgres
- **Password**: postgres (configured in .env)

#### Schema Management
```sql
-- Database initialization happens automatically via:
-- database/init.sql - Complete schema with constraints
-- database/sample_data.sql - Sample projects and tasks
```

#### Backup and Restore
```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres task_management > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres task_management < backup.sql
```

#### Database Migrations
For schema changes:
1. Update `database/init.sql`
2. Create migration script
3. Run migration on existing databases

### pgAdmin Configuration

#### Access
- **URL**: http://localhost:8080
- **Email**: admin@example.com  
- **Password**: admin123

#### Server Setup
1. Login to pgAdmin
2. Add New Server:
   - **Name**: MCP Database
   - **Host**: postgres
   - **Port**: 5432
   - **Username**: postgres
   - **Password**: postgres

## Service Configuration

### AI Agent Service

#### Configuration Files
- `crewai_agent/main.py` - FastAPI application
- `crewai_agent/simple_agent.py` - Agent implementation
- `crewai_agent/requirements.txt` - Dependencies

#### Environment Variables
```bash
# AI Agent specific
ANTHROPIC_API_KEY=sk-ant-...
MCP_SERVICE_URL=http://mcp-service:8000
PORT=8001
HOST=0.0.0.0
```

#### Logging Configuration
```python
# Configured in main.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### MCP Service

#### Configuration Files
- `mcp_service/main.py` - FastAPI application
- `mcp_service/tools.py` - MCP tools implementation
- `mcp_service/database.py` - Database operations
- `mcp_service/models.py` - Pydantic models

#### Environment Variables
```bash
# MCP Service specific
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/task_management
PORT=8000
HOST=0.0.0.0
```

## Security Configuration

### Current Security Measures

1. **Non-root Users**: All containers run as non-root users
2. **Network Isolation**: Services communicate via Docker network
3. **Environment Variables**: Sensitive data in environment variables
4. **Input Validation**: Pydantic models validate all inputs

### Production Security Enhancements

#### 1. Authentication
```python
# Add to requirements.txt
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Implement JWT authentication
from jose import JWTError, jwt
from passlib.context import CryptContext

# Add authentication middleware
@app.middleware("http")
async def authenticate_request(request: Request, call_next):
    # JWT validation logic
    pass
```

#### 2. HTTPS Configuration
```yaml
# docker-compose.yml additions
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
```

#### 3. Secrets Management
```bash
# Use Docker secrets for production
echo "your_api_key" | docker secret create anthropic_api_key -

# Reference in docker-compose.yml
secrets:
  anthropic_api_key:
    external: true
```

#### 4. Database Security
```sql
-- Create application-specific user
CREATE USER mcp_app WITH PASSWORD 'secure_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO mcp_app;

-- Enable SSL connections
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```

## Monitoring and Logging

### Health Monitoring

#### Service Health Checks
```bash
# Built-in health checks
curl http://localhost:8001/health
curl http://localhost:8000/health

# Docker health status
docker-compose ps
```

#### Prometheus Metrics (Future Enhancement)
```python
# Add to requirements.txt
prometheus-client==0.17.1

# Add metrics endpoint
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('app_requests_total', 'Total requests')
REQUEST_DURATION = Histogram('app_request_duration_seconds', 'Request duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Centralized Logging

#### Current Logging
- **AI Agent**: Logs to stdout/stderr
- **MCP Service**: Logs to stdout/stderr  
- **PostgreSQL**: Logs to container logs

#### ELK Stack Integration (Future Enhancement)
```yaml
# docker-compose.yml additions
services:
  elasticsearch:
    image: elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
    
  logstash:
    image: logstash:8.5.0
    volumes:
      - ./logstash:/usr/share/logstash/pipeline
      
  kibana:
    image: kibana:8.5.0
    ports:
      - "5601:5601"
```

## Performance Optimization

### Database Optimization

#### Indexing Strategy
```sql
-- Already implemented in init.sql
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_projects_name ON projects(name);
```

#### Connection Pooling
```python
# Add to requirements.txt
psycopg2-pool==1.1

# Implement connection pooling
from psycopg2 import pool

connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=20,
    host="postgres",
    database="task_management",
    user="postgres",
    password="postgres"
)
```

### Application Optimization

#### Caching
```python
# Add Redis for caching
# requirements.txt
redis==4.5.1

# Cache frequent queries
import redis
cache = redis.Redis(host='redis', port=6379, db=0)

@lru_cache(maxsize=100)
def get_project_cache(project_id: int):
    # Cached project lookup
    pass
```

#### Async Database Operations
```python
# Replace psycopg2 with asyncpg for better performance
# requirements.txt
asyncpg==0.28.0

# Async database operations
import asyncpg

async def create_project_async(name: str, description: str):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        result = await conn.fetchrow(
            "INSERT INTO projects (name, description) VALUES ($1, $2) RETURNING *",
            name, description
        )
        return result
    finally:
        await conn.close()
```

## Backup and Disaster Recovery

### Database Backup Strategy

#### Automated Backups
```bash
# Create backup script
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U postgres task_management > "backup_${DATE}.sql"
aws s3 cp "backup_${DATE}.sql" s3://your-backup-bucket/

# Cron job for daily backups
0 2 * * * /path/to/backup.sh
```

#### Point-in-Time Recovery
```bash
# Enable WAL archiving in PostgreSQL
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/wal_archive/%f'
```

### Application Recovery

#### Container Registry
```bash
# Push images to registry
docker tag mcp_proj1_mcp-service:latest your-registry/mcp-service:v1.0
docker push your-registry/mcp-service:v1.0

docker tag mcp_proj1_crewai-agent:latest your-registry/crewai-agent:v1.0  
docker push your-registry/crewai-agent:v1.0
```

#### Configuration Backup
```bash
# Backup critical configuration
tar -czf config_backup.tar.gz .env docker-compose.yml database/
```

## Troubleshooting

### Common Issues

#### 1. Services Won't Start
```bash
# Check port conflicts
netstat -tulpn | grep :8000
netstat -tulpn | grep :8001

# Check Docker resources
docker system df
docker system prune
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U postgres -d task_management -c "SELECT version();"
```

#### 3. API Key Issues
```bash
# Verify environment variables
docker-compose exec crewai-agent env | grep ANTHROPIC

# Test API key
curl -X POST https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-sonnet-20240229","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
```

#### 4. Memory Issues
```bash
# Check container resource usage
docker stats

# Increase memory limits in docker-compose.yml
services:
  crewai-agent:
    deploy:
      resources:
        limits:
          memory: 1G
```

### Log Analysis

#### View Service Logs
```bash
# All services
docker-compose logs

# Specific service with timestamps
docker-compose logs -t -f crewai-agent

# Filter by log level
docker-compose logs | grep ERROR
```

#### Debug Mode
```bash
# Start with debug logging
LOGGING_LEVEL=DEBUG docker-compose up
```

## Cloud Deployment

### AWS Deployment

#### ECS Configuration
```json
{
  "family": "mcp-service",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "mcp-service",
      "image": "your-registry/mcp-service:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL", 
          "value": "postgresql://user:pass@rds-endpoint:5432/db"
        }
      ]
    }
  ]
}
```

#### RDS Database
```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-name task_management \
  --db-instance-identifier mcp-database \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password your-password
```

### Google Cloud Deployment

#### Cloud Run Configuration
```yaml
# cloud-run.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: mcp-service
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "100"
    spec:
      containers:
      - image: gcr.io/your-project/mcp-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "postgresql://user:pass@cloud-sql-proxy:5432/db"
```

### Kubernetes Deployment

#### Deployment Manifests
```yaml
# k8s/mcp-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-service
  template:
    metadata:
      labels:
        app: mcp-service
    spec:
      containers:
      - name: mcp-service
        image: your-registry/mcp-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-service
spec:
  selector:
    app: mcp-service
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer
```

## Maintenance

### Regular Maintenance Tasks

#### Weekly
```bash
# Update container images
docker-compose pull
docker-compose up -d

# Check disk usage
docker system df
```

#### Monthly  
```bash
# Backup database
./backup.sh

# Clean unused images
docker image prune -a

# Update dependencies
# Check requirements.txt for security updates
```

#### Quarterly
```bash
# Review and update API keys
# Security audit
# Performance review
# Capacity planning
```

### Version Updates

#### Update Process
1. **Test in development environment**
2. **Create backup of current deployment**
3. **Update container images**
4. **Run migration scripts if needed**
5. **Verify all services are working**
6. **Monitor for issues**

#### Rollback Plan
```bash
# Rollback to previous version
docker-compose down
docker tag your-registry/mcp-service:previous your-registry/mcp-service:latest
docker-compose up -d
```

This deployment guide provides comprehensive coverage for setting up, securing, monitoring, and maintaining the AI Agent MCP Service in various environments.