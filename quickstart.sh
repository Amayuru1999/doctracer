#!/bin/bash

# DocTracer Quick Start Script
# This script will set up and run the entire DocTracer application

set -e

echo "🚀 DocTracer Quick Start Script"
echo "================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_APP=doctracer

# API Configuration
API_URL=http://localhost:5000
EOF
    echo "✅ Created .env file"
else
    echo "✅ .env file already exists"
fi

# Create frontend .env file if it doesn't exist
if [ ! -f frontend/.env ]; then
    echo "📝 Creating frontend .env file..."
    cat > frontend/.env << EOF
# API Configuration
VITE_API_URL=http://localhost:5000
VITE_APP_TITLE=DocTracer
VITE_DEV_MODE=true
EOF
    echo "✅ Created frontend .env file"
else
    echo "✅ Frontend .env file already exists"
fi

# Create web visualizer .env file if it doesn't exist
if [ ! -f backend/web_visualizer/.env ]; then
    echo "📝 Creating web visualizer .env file..."
    cat > backend/web_visualizer/.env << EOF
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=True
EOF
    echo "✅ Created web visualizer .env file"
else
    echo "✅ Web visualizer .env file already exists"
fi

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose down 2>/dev/null || true

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check service health
echo "🏥 Checking service health..."

# Check Neo4j
if curl -s http://localhost:7474 > /dev/null; then
    echo "✅ Neo4j is running at http://localhost:7474"
else
    echo "❌ Neo4j is not responding"
fi

# Check Backend
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "✅ Backend API is running at http://localhost:5000"
else
    echo "⏳ Backend API is starting up..."
    sleep 10
    if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
        echo "✅ Backend API is now running at http://localhost:5000"
    else
        echo "❌ Backend API is not responding"
    fi
fi

# Check Web Visualizer
if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo "✅ Web Visualizer is running at http://localhost:5001"
else
    echo "⏳ Web Visualizer is starting up..."
    sleep 10
    if curl -s http://localhost:5001/health > /dev/null 2>&1; then
        echo "✅ Web Visualizer is now running at http://localhost:5001"
    else
        echo "❌ Web Visualizer is not responding"
    fi
fi

# Check Frontend
if curl -s http://localhost:5173 > /dev/null; then
    echo "✅ Frontend is running at http://localhost:5173"
else
    echo "⏳ Frontend is starting up..."
    sleep 10
    if curl -s http://localhost:5173 > /dev/null; then
        echo "✅ Frontend is now running at http://localhost:5173"
    else
        echo "❌ Frontend is not responding"
    fi
fi

echo ""
echo "🎉 DocTracer is now running!"
echo ""
echo "📱 Access Points:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:5000"
echo "   Web Visualizer: http://localhost:5001"
echo "   Neo4j Browser: http://localhost:7474"
echo ""
echo "🔑 Neo4j Credentials:"
echo "   Username: neo4j"
echo "   Password: password123"
echo ""
echo "📚 Next Steps:"
echo "   1. Open http://localhost:5173 in your browser for the main app"
echo "   2. Open http://localhost:5001 for the web visualizer"
echo "   3. Check the README.md for detailed usage instructions"
echo ""
echo "🛑 To stop the services, run: docker-compose down"
echo "🔄 To restart, run: docker-compose restart"
echo "📊 To view logs, run: docker-compose logs -f"
echo ""
echo "Happy Tracking! 🎯📊"
