#!/bin/bash

# Start the Prompt MCP Server
echo "Starting Prompt MCP Server..."

# Set Python path to include the main doctracer package
export PYTHONPATH="../../:$PYTHONPATH"

# Check if virtual environment exists and activate it
if [ -d "../../venv" ]; then
    echo "Activating virtual environment..."
    source ../../venv/bin/activate
fi

# Check for required API keys
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY environment variable not set"
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Warning: ANTHROPIC_API_KEY environment variable not set"
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
