FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY mcp_servers/prompt_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main doctracer package
COPY doctracer/ ./doctracer/
COPY pyproject.toml .

# Copy the MCP server
COPY mcp_servers/prompt_server/ ./mcp_servers/prompt_server/

# Set Python path
ENV PYTHONPATH=/app

# Expose port (if needed for HTTP interface)
EXPOSE 8000

# Default command
CMD ["python", "mcp_servers/prompt_server/server.py"]
