#!/bin/bash

# DocTracer Deployment Script for Digital Ocean
set -e

echo "🚀 DocTracer Deployment Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.production template..."
    cp .env.production .env
    print_warning "Please edit .env file with your actual values before continuing."
    read -p "Press Enter to continue after editing .env file..."
fi

# Load environment variables
source .env

# Validate required environment variables
if [ -z "$NEO4J_PASSWORD" ] || [ "$NEO4J_PASSWORD" = "your_secure_password_here" ]; then
    print_error "Please set a secure NEO4J_PASSWORD in .env file"
    exit 1
fi

print_status "Building Docker images..."

# Build images
docker-compose -f docker-compose.prod.yml build --no-cache

print_status "Starting services..."

# Start services
docker-compose -f docker-compose.prod.yml up -d

print_status "Waiting for services to be ready..."

# Wait for Neo4j to be ready
echo "Waiting for Neo4j to start..."
timeout=60
counter=0
while ! docker-compose -f docker-compose.prod.yml exec -T neo4j cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" "RETURN 1" &> /dev/null; do
    if [ $counter -eq $timeout ]; then
        print_error "Neo4j failed to start within $timeout seconds"
        exit 1
    fi
    echo -n "."
    sleep 1
    ((counter++))
done
echo ""
print_status "Neo4j is ready!"

# Wait for backend to be ready
echo "Waiting for backend to start..."
timeout=60
counter=0
while ! curl -f http://localhost:5000/gazettes &> /dev/null; do
    if [ $counter -eq $timeout ]; then
        print_error "Backend failed to start within $timeout seconds"
        exit 1
    fi
    echo -n "."
    sleep 1
    ((counter++))
done
echo ""
print_status "Backend is ready!"

print_status "Deployment completed successfully! 🎉"
echo ""
echo "Access your application:"
echo "  Frontend: http://localhost"
echo "  Backend API: http://localhost:5000"
echo "  Neo4j Browser: http://localhost:7474"
echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose -f docker-compose.prod.yml down"