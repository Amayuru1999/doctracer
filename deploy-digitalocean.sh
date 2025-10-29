#!/bin/bash

# Digital Ocean Deployment Script for DocTracer
# Run this script on your Digital Ocean droplet

set -e

echo "🚀 Starting DocTracer deployment on Digital Ocean..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    print_success "Docker installed successfully"
else
    print_success "Docker is already installed"
fi

# Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
    print_status "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose installed successfully"
else
    print_success "Docker Compose is already installed"
fi

# Install Git if not already installed
if ! command -v git &> /dev/null; then
    print_status "Installing Git..."
    sudo apt install -y git
    print_success "Git installed successfully"
else
    print_success "Git is already installed"
fi

# Clone or update the repository
REPO_URL="https://github.com/YOUR_USERNAME/doctracer.git"  # Update this with your actual repo URL
PROJECT_DIR="$HOME/doctracer"

if [ -d "$PROJECT_DIR" ]; then
    print_status "Updating existing repository..."
    cd "$PROJECT_DIR"
    git pull origin main
else
    print_status "Cloning repository..."
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f ".env.production" ]; then
        cp .env.production .env
        print_warning "Please edit .env file with your production values:"
        print_warning "  - Update NEO4J_PASSWORD with a secure password"
        print_warning "  - Update API_URL with your domain/IP"
        print_warning "  - Update SECRET_KEY and JWT_SECRET_KEY with secure random strings"
        echo ""
        print_status "Opening .env file for editing..."
        nano .env
    else
        print_error ".env.production template not found!"
        exit 1
    fi
else
    print_success ".env file already exists"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p data/backups

# Set up firewall (UFW)
print_status "Configuring firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 5001/tcp  # API
sudo ufw allow 7474/tcp  # Neo4j Browser
print_success "Firewall configured"

# Build and start the application
print_status "Building and starting DocTracer..."
docker-compose -f docker-compose.prod.yml down --remove-orphans
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Check service status
print_status "Checking service status..."
docker-compose -f docker-compose.prod.yml ps

# Test API endpoint
print_status "Testing API endpoint..."
if curl -f -s http://localhost:5001/gazettes > /dev/null; then
    print_success "API is responding correctly"
else
    print_warning "API might not be ready yet. Check logs with: docker-compose -f docker-compose.prod.yml logs"
fi

# Display access information
echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📋 Access Information:"
echo "  Frontend: http://$(curl -s ifconfig.me):80"
echo "  API: http://$(curl -s ifconfig.me):5001"
echo "  Neo4j Browser: http://$(curl -s ifconfig.me):7474"
echo ""
echo "🔧 Management Commands:"
echo "  View logs: docker-compose -f docker-compose.prod.yml logs"
echo "  Restart: docker-compose -f docker-compose.prod.yml restart"
echo "  Stop: docker-compose -f docker-compose.prod.yml down"
echo "  Update: git pull && docker-compose -f docker-compose.prod.yml up -d --build"
echo ""
echo "⚠️  Important Security Notes:"
echo "  1. Change default Neo4j password in .env file"
echo "  2. Set up SSL/HTTPS for production use"
echo "  3. Configure proper backup strategy"
echo "  4. Monitor logs regularly"
echo ""

print_success "DocTracer is now running on Digital Ocean!"