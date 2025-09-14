#!/bin/bash

# Start the Extraction MCP Server
echo "Starting Extraction MCP Server..."

# Set Python path to include the main doctracer package
export PYTHONPATH="../../:$PYTHONPATH"

# Check if virtual environment exists and activate it
if [ -d "../../venv" ]; then
    echo "Activating virtual environment..."
    source ../../venv/bin/activate
fi

# Install dependencies if needed
if [ ! -f "requirements_installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch requirements_installed
fi

# Start the server
echo "Starting server..."
python server.py
