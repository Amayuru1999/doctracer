#!/bin/bash

# Digital Ocean Droplet Setup Script for DocTracer
# Run this script ONCE on your fresh Digital Ocean droplet

set -e

echo "🚀 Setting up Digital Ocean droplet for DocTracer..."

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

# Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install essential packages
print_status "Installing essential packages..."
apt install -y curl wget git ufw htop nano

# Install Docker
print_status "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker $USER
rm get-docker.sh

# Install Docker Compose
print_status "Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Setup firewall
print_status "Configuring firewall..."
ufw --force enable
ufw allow ssh
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5001/tcp
ufw allow 7474/tcp
ufw allow 7687/tcp

# Create project directory
print_status "Setting up project directory..."
mkdir -p /root/doctracer
cd /root/doctracer

# Clone repository
print_status "Cloning DocTracer repository..."
git clone https://github.com/Amayuru1999/doctracer.git .

# Setup environment file
print_status "Setting up environment file..."
if [ -f ".env.production" ]; then
    cp .env.production .env
    print_warning "Please edit /root/doctracer/.env with your production values:"
    print_warning "  - NEO4J_PASSWORD: Set a secure password"
    print_warning "  - API_URL: Set to http://YOUR_DROPLET_IP:5001"
    print_warning "  - SECRET_KEY and JWT_SECRET_KEY: Generate secure random strings"
else
    print_error ".env.production not found in repository"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs data/backups

# Start Docker service
print_status "Starting Docker service..."
systemctl enable docker
systemctl start docker

# Test Docker installation
print_status "Testing Docker installation..."
docker --version
docker-compose --version

print_success "✅ Digital Ocean droplet setup completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Edit /root/doctracer/.env with your production values"
echo "2. Configure GitHub repository secrets:"
echo "   - DO_HOST: $(curl -s ifconfig.me)"
echo "   - DO_USERNAME: root"
echo "   - DO_SSH_KEY: Your private SSH key content"
echo "3. Push to main branch to trigger deployment"
echo ""
echo "🔧 Manual deployment command:"
echo "cd /root/doctracer && docker-compose -f docker-compose.prod.yml up -d --build"
echo ""