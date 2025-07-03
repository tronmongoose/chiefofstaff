#!/bin/bash

# Production Deployment Script for x402 Travel Booking System
# Supports multiple cloud providers: AWS, DigitalOcean, Vercel, Railway

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="x402-travel-planner"
DOMAIN=${DOMAIN:-"your-domain.com"}
ENVIRONMENT=${ENVIRONMENT:-"production"}

echo -e "${BLUE}🚀 x402 Travel Booking System - Production Deployment${NC}"
echo "=================================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}📋 Checking prerequisites...${NC}"
    
    local missing_deps=()
    
    if ! command_exists docker; then
        missing_deps+=("docker")
    fi
    
    if ! command_exists docker-compose; then
        missing_deps+=("docker-compose")
    fi
    
    if ! command_exists openssl; then
        missing_deps+=("openssl")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo -e "${RED}❌ Missing dependencies: ${missing_deps[*]}${NC}"
        echo "Please install the missing dependencies and try again."
        exit 1
    fi
    
    echo -e "${GREEN}✅ All prerequisites met${NC}"
}

# Function to setup SSL certificates
setup_ssl() {
    echo -e "${YELLOW}🔒 Setting up SSL certificates...${NC}"
    
    if [ ! -d "ssl" ]; then
        mkdir -p ssl
    fi
    
    # Check if certificates already exist
    if [ -f "ssl/cert.pem" ] && [ -f "ssl/key.pem" ]; then
        echo -e "${GREEN}✅ SSL certificates already exist${NC}"
        return
    fi
    
    # Generate self-signed certificate for development
    echo -e "${YELLOW}📝 Generating self-signed SSL certificate...${NC}"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem \
        -out ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=${DOMAIN}"
    
    echo -e "${GREEN}✅ SSL certificates generated${NC}"
    echo -e "${YELLOW}⚠️  Note: For production, replace with Let's Encrypt or your CA certificates${NC}"
}

# Function to setup environment
setup_environment() {
    echo -e "${YELLOW}⚙️  Setting up environment...${NC}"
    
    if [ ! -f ".env.production" ]; then
        if [ -f "env.production.template" ]; then
            cp env.production.template .env.production
            echo -e "${YELLOW}📝 Created .env.production from template${NC}"
            echo -e "${RED}⚠️  Please edit .env.production with your actual values before continuing${NC}"
            read -p "Press Enter after editing .env.production..."
        else
            echo -e "${RED}❌ Environment template not found${NC}"
            exit 1
        fi
    fi
    
    # Load environment variables
    source .env.production
    
    echo -e "${GREEN}✅ Environment setup complete${NC}"
}

# Function to run database migrations
run_migrations() {
    echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
    
    # Start database container for migrations
    docker-compose -f docker-compose.production.yml up -d postgres
    
    # Wait for database to be ready
    echo "Waiting for database to be ready..."
    sleep 10
    
    # Run migrations
    docker-compose -f docker-compose.production.yml exec -T postgres \
        psql -U travel_user -d travel_planner -c "SELECT 1;" > /dev/null 2>&1 || {
        echo -e "${RED}❌ Database connection failed${NC}"
        exit 1
    }
    
    # Run Alembic migrations
    docker-compose -f docker-compose.production.yml run --rm backend \
        alembic upgrade head
    
    echo -e "${GREEN}✅ Database migrations complete${NC}"
}

# Function to build and deploy
deploy_application() {
    echo -e "${YELLOW}🏗️  Building and deploying application...${NC}"
    
    # Build images
    echo "Building Docker images..."
    docker-compose -f docker-compose.production.yml build
    
    # Deploy all services
    echo "Starting all services..."
    docker-compose -f docker-compose.production.yml up -d
    
    echo -e "${GREEN}✅ Application deployed successfully${NC}"
}

# Function to check deployment health
check_health() {
    echo -e "${YELLOW}🏥 Checking deployment health...${NC}"
    
    # Wait for services to start
    echo "Waiting for services to start..."
    sleep 30
    
    # Check backend health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
    else
        echo -e "${RED}❌ Backend health check failed${NC}"
        return 1
    fi
    
    # Check frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is accessible${NC}"
    else
        echo -e "${RED}❌ Frontend health check failed${NC}"
        return 1
    fi
    
    # Check nginx
    if curl -f http://localhost > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Nginx is working${NC}"
    else
        echo -e "${RED}❌ Nginx health check failed${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ All services are healthy${NC}"
}

# Function to show deployment info
show_info() {
    echo -e "${BLUE}📊 Deployment Information${NC}"
    echo "=================================="
    echo "🌐 Frontend: http://localhost"
    echo "🔗 API: http://localhost/api"
    echo "🏥 Health: http://localhost/health"
    echo "🗄️  Database: localhost:5432"
    echo "📊 Redis: localhost:6379"
    echo ""
    echo -e "${YELLOW}📝 Next steps:${NC}"
    echo "1. Configure your domain in .env.production"
    echo "2. Replace SSL certificates with real ones"
    echo "3. Set up monitoring and logging"
    echo "4. Configure backup strategies"
}

# Function to deploy to specific cloud provider
deploy_to_cloud() {
    local provider=$1
    
    case $provider in
        "aws")
            echo -e "${BLUE}☁️  Deploying to AWS...${NC}"
            # AWS ECS deployment logic
            echo "AWS deployment not implemented yet"
            ;;
        "digitalocean")
            echo -e "${BLUE}☁️  Deploying to DigitalOcean...${NC}"
            # DigitalOcean App Platform deployment
            echo "DigitalOcean deployment not implemented yet"
            ;;
        "vercel")
            echo -e "${BLUE}☁️  Deploying to Vercel...${NC}"
            # Vercel deployment logic
            echo "Vercel deployment not implemented yet"
            ;;
        "railway")
            echo -e "${BLUE}☁️  Deploying to Railway...${NC}"
            # Railway deployment logic
            echo "Railway deployment not implemented yet"
            ;;
        *)
            echo -e "${RED}❌ Unknown provider: $provider${NC}"
            exit 1
            ;;
    esac
}

# Main deployment function
main() {
    local cloud_provider=${1:-"local"}
    
    check_prerequisites
    setup_environment
    setup_ssl
    
    if [ "$cloud_provider" = "local" ]; then
        run_migrations
        deploy_application
        check_health
        show_info
    else
        deploy_to_cloud "$cloud_provider"
    fi
}

# Parse command line arguments
case "${1:-}" in
    "aws"|"digitalocean"|"vercel"|"railway")
        main "$1"
        ;;
    "local"|"")
        main "local"
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [local|aws|digitalocean|vercel|railway]"
        echo ""
        echo "Deploy the x402 Travel Booking System to production."
        echo ""
        echo "Options:"
        echo "  local         Deploy locally with Docker (default)"
        echo "  aws           Deploy to AWS ECS"
        echo "  digitalocean  Deploy to DigitalOcean App Platform"
        echo "  vercel        Deploy to Vercel"
        echo "  railway       Deploy to Railway"
        echo "  help          Show this help message"
        ;;
    *)
        echo -e "${RED}❌ Unknown option: $1${NC}"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac 