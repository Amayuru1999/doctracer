#!/bin/bash

# DocTracer Frontend Startup Script

echo "🚀 Starting DocTracer Frontend..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment file..."
    cat > .env << EOF
VITE_API_BASE=http://localhost:5001
VITE_APP_TITLE=DocTracer
VITE_APP_DESCRIPTION=Government Structure Change Tracker
EOF
    echo "✅ Environment file created"
fi

echo "🌐 Starting development server..."
echo "📱 Frontend will be available at: http://localhost:5173"
echo "🔗 Backend API should be running at: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
