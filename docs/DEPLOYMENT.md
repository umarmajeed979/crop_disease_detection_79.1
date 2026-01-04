# 🚀 Deployment Guide

Complete guide for deploying the Crop Disease Detection API to production.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Local Production Testing](#local-production-testing)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Frontend Integration](#frontend-integration)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Pre-Deployment Checklist

### ✅ Essential Steps

- [ ] Train model with full dataset
- [ ] Test all API endpoints locally
- [ ] Configure production environment variables
- [ ] Set up proper CORS origins
- [ ] Enable HTTPS/SSL
- [ ] Set up logging and monitoring
- [ ] Create backup strategy for models
- [ ] Document API for frontend team

### ⚙️ Production Configuration

Create `.env.production`:

```bash
# Environment
FLASK_ENV=production
DEBUG=False

# Server
HOST=0.0.0.0
PORT=5000

# CORS - IMPORTANT: Set to your frontend domain
CORS_ORIGINS=https://your-frontend-domain.com,https://app.your-domain.com

# Security
API_KEY=your_secure_api_key_here

# Performance
MAX_BATCH_SIZE=5
REQUEST_TIMEOUT=60

# Logging
LOG_LEVEL=WARNING
```

---

## Local Production Testing

### 1. Test with Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run production server
gunicorn --bind 0.0.0.0:5000 \
         --workers 4 \
         --timeout 120 \
         --log-level info \
         wsgi:app
```

### 2. Test API Endpoints

```bash
# Health check
curl http://localhost:5000/api/health

# Prediction test
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "image": "base64_encoded_image",
    "use_tflite": true
  }'
```

### 3. Load Testing (Optional)

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test 100 requests with 10 concurrent
ab -n 100 -c 10 http://localhost:5000/api/health
```

---

## Docker Deployment

### Method 1: Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p logs data/models

# Expose port
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "wsgi:app"]
```

### Build and Run

```bash
# Build image
docker build -t crop-disease-api:latest .

# Run container
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env.production \
  --name crop-disease-api \
  crop-disease-api:latest

# Check logs
docker logs -f crop-disease-api

# Stop container
docker stop crop-disease-api
```

### Method 2: Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    env_file:
      - .env.production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped
```

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:5000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    server {
        listen 443 ssl;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location /api {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_connect_timeout 300s;
            proxy_send_timeout 300s;
            proxy_read_timeout 300s;
        }
    }
}
```

Run with Docker Compose:

```bash
docker-compose up -d
```

---

## Cloud Deployment

### AWS Deployment (EC2)

#### 1. Launch EC2 Instance

```bash
# Instance specs:
# - t3.medium (2 vCPU, 4GB RAM) minimum
# - Ubuntu 20.04 LTS
# - 20GB+ storage
# - Security group: Allow ports 80, 443, 22
```

#### 2. Setup EC2

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 3. Deploy Application

```bash
# Clone repository
git clone <your-repo> crop-disease-api
cd crop-disease-api

# Copy models and data
# (Upload trained models to EC2)

# Configure environment
cp .env.example .env.production
nano .env.production  # Edit settings

# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

#### 4. Setup Domain & SSL

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### Google Cloud Platform (GCP)

#### Deploy to Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/YOUR_PROJECT/crop-disease-api

# Deploy to Cloud Run
gcloud run deploy crop-disease-api \
  --image gcr.io/YOUR_PROJECT/crop-disease-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --timeout 300s
```

### Azure Deployment

#### Deploy to Azure Container Instances

```bash
# Create resource group
az group create --name crop-disease-rg --location eastus

# Create container
az container create \
  --resource-group crop-disease-rg \
  --name crop-disease-api \
  --image your-registry/crop-disease-api \
  --cpu 2 --memory 4 \
  --ports 5000 \
  --environment-variables FLASK_ENV=production
```

---

## Frontend Integration

### CORS Configuration

In `.env.production`:

```bash
# Allow specific frontend domains
CORS_ORIGINS=https://your-app.com,https://www.your-app.com

# For development also
CORS_ORIGINS=http://localhost:3000,https://your-app.com
```

### API Integration Example (JavaScript)

```javascript
// Frontend integration example

const API_BASE_URL = 'https://api.your-domain.com';

async function predictDisease(imageFile) {
  // Convert image to base64
  const base64Image = await fileToBase64(imageFile);
  
  // Make prediction request
  const response = await fetch(`${API_BASE_URL}/api/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      image: base64Image,
      use_tflite: true,  // Use mobile model for faster response
      top_k: 3
    })
  });
  
  const result = await response.json();
  return result;
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}
```

### Lovable Integration

For Lovable.dev frontend:

1. **Set CORS**: Update backend CORS to include Lovable preview URL
2. **API Endpoint**: Configure API base URL in frontend
3. **Error Handling**: Implement proper error displays
4. **Loading States**: Show loading spinners during predictions

---

## Monitoring & Maintenance

### 1. Logging

```bash
# View application logs
docker-compose logs -f api

# View specific log file
tail -f logs/app.log

# Monitor error logs
tail -f logs/error.log
```

### 2. Health Monitoring

Set up automated health checks:

```bash
# Cron job for health check
*/5 * * * * curl -f http://localhost:5000/api/health || echo "API Down" | mail -s "Alert" admin@example.com
```

### 3. Performance Monitoring

Tools to consider:
- **New Relic**: Application performance monitoring
- **DataDog**: Infrastructure and application monitoring
- **Prometheus + Grafana**: Custom metrics and dashboards

### 4. Backup Strategy

```bash
# Backup models and configuration
tar -czf backup-$(date +%Y%m%d).tar.gz \
  data/models/ \
  .env.production \
  logs/

# Upload to S3 (example)
aws s3 cp backup-$(date +%Y%m%d).tar.gz s3://your-bucket/backups/
```

### 5. Updates and Maintenance

```bash
# Update application
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# Check status
docker-compose ps
```

---

## Troubleshooting Production Issues

### Issue: Container keeps restarting

```bash
# Check logs
docker-compose logs api

# Check resource usage
docker stats

# Increase memory if needed in docker-compose.yml
```

### Issue: Slow response times

**Solutions:**
1. Use TFLite model for predictions
2. Increase number of workers
3. Enable caching
4. Use CDN for static assets
5. Optimize image preprocessing

### Issue: CORS errors

**Check:**
1. CORS_ORIGINS in .env matches frontend domain
2. Frontend sends correct headers
3. Preflight requests are handled

---

## Security Best Practices

1. **Use HTTPS**: Always use SSL/TLS in production
2. **API Keys**: Implement API key authentication
3. **Rate Limiting**: Prevent abuse with rate limits
4. **Input Validation**: Validate all inputs
5. **Security Headers**: Add security headers in Nginx
6. **Regular Updates**: Keep dependencies updated
7. **Monitoring**: Monitor for unusual activity

---

## Support

For production issues:
1. Check logs: `docker-compose logs -f`
2. Review health endpoint: `/api/health`
3. Contact DevOps team
4. Check cloud provider status

---

**Last Updated**: 2024  
**Maintainer**: [Your Team]