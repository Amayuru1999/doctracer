#!/bin/bash

echo "🌐 Starting Government Structure Changes Web Visualizer..."
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements_web.txt

# Check if templates directory exists
if [ ! -d "templates" ]; then
    echo "📁 Creating templates directory..."
    mkdir -p templates
fi

# Start the web server
echo "🚀 Starting web server..."
echo "🌐 Open your browser and go to: http://localhost:5001"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

python web_visualizer.py
