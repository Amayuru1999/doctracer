#!/bin/bash

# Deployment Troubleshooting Script for DocTracer
# Run this script to diagnose deployment issues

set -e

echo "🔍 DocTracer Deployment Troubleshooting"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    print_error "docker-compose.prod.yml not found. Are you in the project directory?"
    exit 1
fi

print_status "Checking Docker installation..."
if command -v docker &> /dev/null; then
    print_success "Docker is installed: $(docker --version)"
else
    print_error "Docker is not installed!"
    exit 1
fi

print_status "Checking Docker Compose installation..."
if command -v docker-compose &> /dev/null; then
    print_success "Docker Compose is installed: $(docker-compose --version)"
else
    print_error "Docker Compose is not installed!"
    exit 1
fi

print_status "Checking .env file..."
if [ -f ".env" ]; then
    print_success ".env file exists"
    print_status "Environment variables:"
    grep -E "^[A-Z_]+" .env | head -5
else
    print_warning ".env file not found"
    if [ -f ".env.production" ]; then
        print_status "Found .env.production template. Copying to .env..."
        cp .env.production .env
        print_warning "Please edit .env file with your production values"
    fi
fi

print_status "Checking Git repository status..."
git status --porcelain
if [ $? -eq 0 ]; then
    print_success "Git repository is clean"
    print_status "Latest commits:"
    git log --oneline -3
else
    print_warning "Git repository has uncommitted changes"
fi

print_status "Checking Docker containers..."
docker-compose -f docker-compose.prod.yml ps

print_status "Checking Docker images..."
docker images | grep doctracer || print_warning "No DocTracer images found"

print_status "Checking container logs (last 20 lines)..."
echo ""
print_status "Backend logs:"
docker-compose -f docker-compose.prod.yml logs --tail=20 backend || print_warning "Backend container not running"

echo ""
print_status "Frontend logs:"
docker-compose -f docker-compose.prod.yml logs --tail=20 frontend || print_warning "Frontend container not running"

echo ""
print_status "Neo4j logs:"
docker-compose -f docker-compose.prod.yml logs --tail=20 neo4j || print_warning "Neo4j container not running"

print_status "Checking network connectivity..."
if curl -f -s --max-time 10 http://localhost:5001/gazettes > /dev/null; then
    print_success "API is responding on localhost:5001"
else
    print_warning "API is not responding on localhost:5001"
fi

if curl -f -s --max-time 10 http://localhost:80 > /dev/null; then
    print_success "Frontend is responding on localhost:80"
else
    print_warning "Frontend is not responding on localhost:80"
fi

print_status "Checking disk space..."
df -h | head -2

print_status "Checking memory usage..."
free -h

echo ""
print_status "Troubleshooting complete!"
echo ""
print_status "Common solutions:"
echo "  1. If containers aren't running: docker-compose -f docker-compose.prod.yml up -d --build"
echo "  2. If API not responding: Check backend logs and .env configuration"
echo "  3. If build fails: docker system prune -f && docker-compose -f docker-compose.prod.yml build --no-cache"
echo "  4. If Git issues: git pull origin main"
echo ""