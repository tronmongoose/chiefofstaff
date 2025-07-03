# 🚀 x402 Travel Booking System - Production Deployment Guide

## Overview

This guide covers deploying the world's first x402 crypto-payment travel booking system to production. The system includes:

- **Backend API** (FastAPI + LangGraph)
- **Frontend** (Next.js + TypeScript)
- **Database** (PostgreSQL)
- **Caching** (Redis)
- **Payment System** (x402 + Coinbase CDP)
- **Reverse Proxy** (Nginx)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx (443)   │───▶│  Frontend (3000) │    │  Backend (8000) │
│   SSL/TLS       │    │   Next.js       │    │   FastAPI       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │     Redis       │
                       │   Database      │    │    Cache        │
                       └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

### Required Software
- Docker & Docker Compose
- OpenSSL (for SSL certificates)
- Git
- Domain name (for production)

### Required Accounts
- [Amadeus API](https://developers.amadeus.com/) - Flight data
- [OpenWeather API](https://openweathermap.org/api) - Weather data
- [Coinbase Developer](https://developers.coinbase.com/) - x402 payments
- [Sentry](https://sentry.io/) - Error tracking (optional)
- [Datadog](https://www.datadoghq.com/) - Monitoring (optional)

## 🚀 Quick Start (Local Production)

1. **Clone and setup:**
```bash
git clone <your-repo>
cd my-langgraph-project
```

2. **Configure environment:**
```bash
cp env.production.template .env.production
# Edit .env.production with your actual values
```

3. **Deploy:**
```bash
./deploy.sh
```

4. **Access the application:**
- Frontend: http://localhost
- API: http://localhost/api
- Health: http://localhost/health

## ☁️ Cloud Deployment

### Option 1: DigitalOcean App Platform (Recommended)

1. **Install DigitalOcean CLI:**
```bash
# macOS
brew install doctl

# Linux
snap install doctl
```

2. **Authenticate:**
```bash
doctl auth init
```

3. **Deploy:**
```bash
./deploy.sh digitalocean
```

### Option 2: AWS ECS

1. **Install AWS CLI:**
```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

2. **Configure AWS:**
```bash
aws configure
```

3. **Deploy:**
```bash
./deploy.sh aws
```

### Option 3: Railway

1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
```

2. **Login:**
```bash
railway login
```

3. **Deploy:**
```bash
./deploy.sh railway
```

## 🔧 Configuration

### Environment Variables

Copy `env.production.template` to `.env.production` and configure:

```bash
# Database
DB_PASSWORD=your_secure_password
DATABASE_URL=postgresql://travel_user:${DB_PASSWORD}@postgres:5432/travel_planner

# APIs
OPENWEATHER_API_KEY=your_openweather_key
AMADEUS_CLIENT_ID=your_amadeus_client_id
AMADEUS_CLIENT_SECRET=your_amadeus_secret

# x402 Payments
TRAVEL_PAYMENT_WALLET_ADDRESS=your_wallet_address
COINBASE_API_KEY=your_coinbase_key
COINBASE_API_SECRET=your_coinbase_secret

# Frontend
NEXT_PUBLIC_API_URL=https://your-domain.com/api
NEXT_PUBLIC_APP_NAME=x402 Travel Planner

# Security
SECRET_KEY=your_32_char_secret_key
JWT_SECRET=your_32_char_jwt_secret
```

### SSL Certificates

For production, replace self-signed certificates:

1. **Let's Encrypt (Recommended):**
```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
```

2. **Commercial CA:**
Place your CA certificates in the `ssl/` directory:
- `ssl/cert.pem` - Certificate chain
- `ssl/key.pem` - Private key

## 🗄️ Database Setup

### Initial Setup
```bash
# Start database
docker-compose -f docker-compose.production.yml up -d postgres

# Run migrations
docker-compose -f docker-compose.production.yml run --rm backend alembic upgrade head
```

### Backup Strategy
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose -f docker-compose.production.yml exec -T postgres \
    pg_dump -U travel_user travel_planner > backup_${DATE}.sql
EOF

chmod +x backup.sh

# Schedule daily backups
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

## 📊 Monitoring & Logging

### Health Checks
- Backend: `GET /health`
- Database: PostgreSQL connection
- Redis: Connection ping
- Frontend: HTTP 200 response

### Logging
```bash
# View logs
docker-compose -f docker-compose.production.yml logs -f

# View specific service logs
docker-compose -f docker-compose.production.yml logs -f backend
```

### Monitoring Setup
1. **Sentry (Error Tracking):**
```bash
# Add to .env.production
SENTRY_DSN=your_sentry_dsn
```

2. **Datadog (Performance Monitoring):**
```bash
# Add to .env.production
DATADOG_API_KEY=your_datadog_key
```

## 🔒 Security

### Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Rate Limiting
- API: 10 requests/second
- General: 30 requests/second
- Configured in `nginx.conf`

### Security Headers
- X-Frame-Options: SAMEORIGIN
- X-XSS-Protection: 1; mode=block
- X-Content-Type-Options: nosniff
- Content-Security-Policy: configured

## 🚀 Scaling

### Horizontal Scaling
```bash
# Scale backend services
docker-compose -f docker-compose.production.yml up -d --scale backend=3

# Scale with load balancer
# Update nginx.conf upstream configuration
```

### Database Scaling
- Consider managed PostgreSQL (AWS RDS, DigitalOcean Managed Databases)
- Implement read replicas for read-heavy workloads
- Use connection pooling (PgBouncer)

## 🔄 Maintenance

### Updates
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

### Database Migrations
```bash
# Run migrations
docker-compose -f docker-compose.production.yml run --rm backend alembic upgrade head

# Rollback if needed
docker-compose -f docker-compose.production.yml run --rm backend alembic downgrade -1
```

### SSL Certificate Renewal
```bash
# Let's Encrypt auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet

# Restart nginx after renewal
sudo systemctl reload nginx
```

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Failed:**
```bash
# Check database status
docker-compose -f docker-compose.production.yml ps postgres

# Check logs
docker-compose -f docker-compose.production.yml logs postgres
```

2. **Payment System Not Working:**
```bash
# Verify Coinbase credentials
curl -H "Authorization: Bearer $COINBASE_API_KEY" \
     https://api.coinbase.com/v2/accounts

# Check x402 middleware logs
docker-compose -f docker-compose.production.yml logs backend | grep x402
```

3. **Frontend Not Loading:**
```bash
# Check frontend logs
docker-compose -f docker-compose.production.yml logs frontend

# Verify API connectivity
curl http://localhost/api/health
```

### Performance Issues

1. **Slow Database Queries:**
```bash
# Enable query logging
docker-compose -f docker-compose.production.yml exec postgres \
    psql -U travel_user -d travel_planner -c "SET log_statement = 'all';"
```

2. **High Memory Usage:**
```bash
# Check resource usage
docker stats

# Optimize Redis memory
docker-compose -f docker-compose.production.yml exec redis \
    redis-cli CONFIG SET maxmemory 256mb
```

## 📞 Support

### Getting Help
1. Check the logs: `docker-compose logs`
2. Review this documentation
3. Check GitHub issues
4. Contact the development team

### Emergency Procedures
```bash
# Emergency shutdown
docker-compose -f docker-compose.production.yml down

# Emergency restart
docker-compose -f docker-compose.production.yml up -d

# Database emergency backup
docker-compose -f docker-compose.production.yml exec postgres \
    pg_dump -U travel_user travel_planner > emergency_backup.sql
```

## 🎯 Next Steps

After successful deployment:

1. **Set up monitoring alerts**
2. **Configure automated backups**
3. **Set up CI/CD pipeline**
4. **Implement A/B testing**
5. **Plan for international expansion**
6. **Add more payment methods**

---

**🎉 Congratulations!** You've successfully deployed the world's first x402 crypto-payment travel booking system to production. 