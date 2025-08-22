#!/bin/bash

# Setup script for DocTracer MCP Servers
echo "Setting up DocTracer MCP Servers environment..."

# Check if we're in the right directory
if [ ! -d "extraction_server" ] || [ ! -d "prompt_server" ]; then
    echo "Error: Please run this script from the mcp_servers directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies for extraction server
echo "Installing extraction server dependencies..."
cd extraction_server
pip install -r requirements.txt
cd ..

# Install dependencies for prompt server
echo "Installing prompt server dependencies..."
cd prompt_server
pip install -r requirements.txt
cd ..

# Install main doctracer package in development mode
echo "Installing main doctracer package..."
cd ..
pip install -e .
cd mcp_servers

echo "Environment setup complete!"
echo ""
echo "To start the servers:"
echo "  Extraction server: ./extraction_server/start_server.sh"
echo "  Prompt server: ./prompt_server/start_server.sh"
echo ""
echo "To test the setup:"
echo "  python test_servers.py"
