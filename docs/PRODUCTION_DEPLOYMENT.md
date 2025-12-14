# Production Deployment Guide

## Pre-Deployment Checklist

- [ ] All tests passing: `pytest app/test_main.py -v`
- [ ] Code style verified: `flake8 app/ --max-line-length=79`
- [ ] Type checking passed: `mypy app/`
- [ ] No hardcoded secrets in code
- [ ] `.env` file in `.gitignore`
- [ ] Debug mode disabled: `DEBUG=false`
- [ ] Database backup created
- [ ] Rollback plan documented

## Deployment Stack

### Recommended Architecture

```text
┌─────────────────────┐
│      Users          │
└──────────┬──────────┘
           │ HTTPS
           ▼
┌─────────────────────┐
│  nginx (Reverse Proxy)
│  - TLS/SSL          │
│  - Load Balancing   │
│  - Static Files     │
└──────────┬──────────┘
           │
    ┌──────┴──────┬──────────┬──────────┐
    │             │          │          │
    ▼             ▼          ▼          ▼
┌────────────────────────────────────────┐
│  Gunicorn (4-8 workers)                │
│  - FastAPI App                         │
│  - Async (uvicorn workers)             │
└────────────┬───────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  PostgreSQL 15+                         │
│  - Connection pooling                   │
│  - SSL connections                      │
│  - Regular backups                      │
└─────────────────────────────────────────┘
```

## Deployment Methods

### Option 1: Traditional Server (VPS/Dedicated)

#### 1.1 Server Setup

```bash
# 1. Create application user
sudo useradd -m -s /bin/bash heroesapp

# 2. Install dependencies
sudo apt-get update
sudo apt-get install -y python3.14 python3.14-venv postgresql-15 nginx

# 3. Clone repository
sudo su - heroesapp
git clone https://github.com/your-username/fastapi-heroes.git
cd fastapi-heroes

# 4. Create virtual environment
python3.14 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# 6. Create .env file
nano .env
```

#### 1.2 Environment Variables

```bash
# .env (production)
DATABASE_URL=postgresql://heroesuser:secretpassword@localhost:5432/heroes_prod
LOG_LEVEL=info
DEBUG=false
WORKERS=4
```

#### 1.3 Gunicorn Configuration

Create `gunicorn_config.py`:

```python
import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2  # or set explicitly
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Process naming
proc_name = 'fastapi-heroes'

# Server mechanics
daemon = False
umask = 0o022
pidfile = "/tmp/gunicorn.pid"
```

#### 1.4 Systemd Service

Create `/etc/systemd/system/fastapi-heroes.service`:

```ini
[Unit]
Description=FastAPI Heroes Application
After=network.target postgresql.service

[Service]
Type=notify
User=heroesapp
WorkingDirectory=/home/heroesapp/fastapi-heroes
Environment="PATH=/home/heroesapp/fastapi-heroes/venv/bin"
ExecStart=/home/heroesapp/fastapi-heroes/venv/bin/gunicorn \
    --config gunicorn_config.py \
    --access-logfile - \
    --error-logfile - \
    app.main:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGQUIT
SyslogIdentifier=fastapi-heroes

[Install]
WantedBy=multi-user.target
```

#### 1.5 Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable fastapi-heroes
sudo systemctl start fastapi-heroes
sudo systemctl status fastapi-heroes

# View logs
sudo journalctl -u fastapi-heroes -f
```

#### 1.6 Nginx Configuration

Create `/etc/nginx/sites-available/fastapi-heroes`:

```nginx
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name example.com www.example.com;

    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/fastapi-heroes.access.log;
    error_log /var/log/nginx/fastapi-heroes.error.log;

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (if any)
    location /static/ {
        alias /home/heroesapp/fastapi-heroes/static/;
        expires 1y;
    }
}
```

#### 1.7 Enable Nginx Site

```bash
sudo ln -s /etc/nginx/sites-available/fastapi-heroes /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 2: Docker Deployment

#### 2.1 Dockerfile

```dockerfile
FROM python:3.14-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/docs')"

EXPOSE 8000

CMD ["gunicorn", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app.main:app"]
```

#### 2.2 Docker Compose (Production)

Create `compose.prod.yml`:

```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: heroesuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: heroes_prod
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U heroesuser"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  api:
    build: .
    environment:
      - DATABASE_URL=postgresql+asyncpg://heroesuser:${DB_PASSWORD}@postgres:5432/heroes_prod
      - LOG_LEVEL=info
      - DEBUG=false
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "8000:8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
```

#### 2.3 Build and Deploy

```bash
# Build image
docker build -t fastapi-heroes:latest .

# Run with docker compose
docker compose -f compose.prod.yml up -d

# View logs
docker compose -f compose.prod.yml logs -f api

# Stop services
docker compose -f compose.prod.yml down
```

### Option 3: Kubernetes (Advanced)

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-heroes
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-heroes
  template:
    metadata:
      labels:
        app: fastapi-heroes
    spec:
      containers:
      - name: api
        image: fastapi-heroes:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: LOG_LEVEL
          value: "info"
        livenessProbe:
          httpGet:
            path: /docs
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /docs
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

## Database Setup

### PostgreSQL Installation

```bash
# Install PostgreSQL
sudo apt-get install postgresql-15

# Connect to PostgreSQL
sudo -u postgres psql

# Create user and database
CREATE USER heroesuser WITH PASSWORD 'strong_password_here';
CREATE DATABASE heroes_prod OWNER heroesuser;
GRANT ALL PRIVILEGES ON DATABASE heroes_prod TO heroesuser;

# Enable SSL connections
ALTER SYSTEM SET ssl = on;
SELECT pg_reload_conf();

# Exit
\q
```

### Database Backups

```bash
# Manual backup
pg_dump -U heroesuser heroes_prod > backup_$(date +%Y%m%d).sql

# Automated daily backup
# Add to crontab
0 2 * * * pg_dump -U heroesuser heroes_prod > /backups/heroes_$(date +\%Y\%m\%d).sql

# Restore from backup
psql -U heroesuser heroes_prod < backup_20240101.sql
```

## Security Checklist

### SSL/TLS

- [ ] Install SSL certificate (Let's Encrypt)
- [ ] Configure HTTPS redirect
- [ ] Enable HSTS headers
- [ ] Update TLS 1.2 minimum

### Access Control

- [ ] Use strong database passwords
- [ ] Restrict database access to app server only
- [ ] Use environment variables for secrets
- [ ] Enable SSH key-based authentication

### Application Security

- [ ] Disable debug mode (`DEBUG=false`)
- [ ] Set `ALLOWED_HOSTS` in production
- [ ] Configure CORS carefully
- [ ] Enable rate limiting

### System Security

- [ ] Enable firewall (UFW/iptables)
- [ ] Keep OS packages updated
- [ ] Monitor system logs
- [ ] Enable automatic security updates

```bash
# UFW firewall rules
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable

# Automatic security updates
sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Monitoring & Logging

### Application Logs

```bash
# View application logs
sudo journalctl -u fastapi-heroes -f

# Nginx access logs
sudo tail -f /var/log/nginx/fastapi-heroes.access.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### Health Checks

```python
# Add health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }
```

### Monitoring Tools

Recommended: Prometheus, Grafana, ELK Stack, or cloud-native alternatives

## Scaling Strategies

### Horizontal Scaling

```bash
# Run multiple Gunicorn instances
gunicorn \
    --workers 8 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    app.main:app
```

### Caching (Redis)

```python
# Add Redis caching
from redis import Redis
redis = Redis(host='localhost', port=6379)

@app.get("/heroes")
async def read_heroes(skip: int = 0, limit: int = 10):
    cache_key = f"heroes:{skip}:{limit}"
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)

    heroes = session.exec(select(Hero).offset(skip).limit(limit)).all()
    redis.setex(cache_key, 3600, json.dumps(heroes))
    return heroes
```

### Load Balancing

```nginx
# nginx load balancing
upstream app_servers {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
    server 127.0.0.1:8004;
}

server {
    location / {
        proxy_pass http://app_servers;
        proxy_set_header Host $host;
    }
}
```

## Troubleshooting

### Common Issues

#### Service won't start

```bash
sudo systemctl status fastapi-heroes
sudo journalctl -u fastapi-heroes -n 50
```

#### Database connection fails

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U heroesuser -d heroes_prod -h localhost
```

#### High memory usage

```bash
# Check for memory leaks
ps aux | grep gunicorn

# Reduce worker count or increase memory
```

## Disaster Recovery

### Rollback Procedure

```bash
# 1. Stop current version
sudo systemctl stop fastapi-heroes

# 2. Checkout previous version
git checkout <previous-commit>

# 3. Install dependencies (if changed)
source venv/bin/activate
pip install -r requirements.txt

# 4. Restart service
sudo systemctl start fastapi-heroes

# 5. Verify
curl https://example.com/docs
```

### Database Recovery

```bash
# 1. Stop application
sudo systemctl stop fastapi-heroes

# 2. Restore from backup
psql -U heroesuser heroes_prod < backup_20240101.sql

# 3. Restart application
sudo systemctl start fastapi-heroes
```

## See Also

- [Configuration Guide](CONFIGURATION.md)
- [Architecture Guide](ARCHITECTURE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
