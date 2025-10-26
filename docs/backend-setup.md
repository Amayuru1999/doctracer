# Backend Setup Guide

This guide will help you set up the DocTracer backend API, a Python Flask-based service that provides data processing, analysis, and API endpoints for the DocTracer application.

## 📋 Prerequisites

- **Python 3.8+** - Download from [python.org](https://python.org/)
- **pip** - Python package manager
- **Neo4j Database** - Running Neo4j instance
- **Git** - For version control

## 🚀 Quick Start

### 1. Navigate to Project Root

```bash
cd /path/to/doctracer
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install backend-specific dependencies
pip install -r backend/requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_APP=doctracer

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000

# Optional: External API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 5. Start Backend Server

```bash
# Development mode
python -m flask run --host=0.0.0.0 --port=5000

# Or using the CLI
python -m doctracer.cli.server

# Or using uvicorn (if using FastAPI)
uvicorn backend.api:app --host 0.0.0.0 --port 5000 --reload
```

The API will be available at: **http://localhost:5000**

## 🛠️ Development Commands

### Available Scripts

```bash
# Start development server
python -m flask run

# Start with debug mode
python -m flask run --debug

# Run tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=doctracer

# Code formatting
black doctracer/
isort doctracer/

# Type checking
mypy doctracer/
```

## 🏗️ Project Structure

```
backend/
├── api.py                   # FastAPI application
├── requirements.txt         # Python dependencies
└── web_visualizer/          # Standalone Flask app
    ├── app.py              # Flask application entry point
    ├── web_visualizer.py   # Core application logic
    ├── templates/          # HTML templates
    ├── requirements.txt    # Dependencies
    └── Dockerfile          # Container configuration

doctracer/                   # Main Python package
├── cli/                    # Command-line interface
│   ├── extract.py         # Data extraction
│   ├── track.py           # Change tracking
│   └── track_changes.py   # Gazette comparison
├── extract/                # Data extraction modules
│   ├── gazette/           # Gazette-specific extractors
│   └── pdf_extractor.py   # PDF processing
├── models/                 # Data models
│   ├── gazette.py         # Gazette model
│   └── gazette_change.py  # Change tracking model
├── services/               # Business logic
│   └── gazette_change_tracker.py
├── prompt/                 # AI prompt management
│   ├── catalog.py         # Prompt catalog
│   ├── config.py          # Configuration
│   └── executor.py        # Prompt execution
└── neo4j_interface.py     # Database interface
```

## 🎨 Technologies Used

- **Flask** - Web framework
- **FastAPI** - Modern API framework
- **Neo4j** - Graph database
- **Pandas** - Data manipulation
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## 🔧 Configuration

### Flask Configuration

Key configuration in the Flask application:

```python
# backend/api.py
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
app.config['NEO4J_URI'] = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
app.config['NEO4J_USER'] = os.getenv('NEO4J_USER', 'neo4j')
app.config['NEO4J_PASSWORD'] = os.getenv('NEO4J_PASSWORD', 'password123')
```

### FastAPI Configuration

If using FastAPI (in `backend/api.py`):

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="DocTracer API",
    description="Government Gazette Change Tracking API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Neo4j database URI | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `password123` |
| `FLASK_ENV` | Flask environment | `development` |
| `FLASK_DEBUG` | Debug mode | `1` |
| `API_HOST` | API host | `0.0.0.0` |
| `API_PORT` | API port | `5000` |

## 🌐 API Endpoints

### Core Endpoints

```bash
# Health check
GET /api/health

# Get government structure
GET /api/structure

# Get changes between gazettes
GET /api/changes?old=2023-01&new=2023-02

# Get analytics data
GET /api/analytics

# Upload new gazette
POST /api/gazette
```

### Web Visualizer Endpoints

```bash
# Main dashboard
GET /

# Department analysis
GET /departments

# API endpoints
GET /api/structure
GET /api/changes
```

### Example API Usage

```bash
# Health check
curl http://localhost:5000/api/health

# Get structure
curl http://localhost:5000/api/structure

# Get changes
curl "http://localhost:5000/api/changes?old=2023-01&new=2023-02"

# Upload gazette
curl -X POST http://localhost:5000/api/gazette \
  -H "Content-Type: application/json" \
  -d '{"gazette_id": "2023-01", "data": {...}}'
```

## 🗄️ Database Integration

### Neo4j Connection

```python
# doctracer/neo4j_interface.py
from neo4j import GraphDatabase

class Neo4jInterface:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def get_structure(self):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (g:Gazette)-[:CONTAINS]->(m:Minister)
                RETURN g, m
            """)
            return [record for record in result]
```

### Database Schema

```cypher
// Create constraints
CREATE CONSTRAINT IF NOT EXISTS FOR (g:Gazette) REQUIRE g.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (m:Minister) REQUIRE m.name IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (d:Department) REQUIRE d.name IS UNIQUE;

// Create indexes
CREATE INDEX IF NOT EXISTS FOR (g:Gazette) ON (g.published_date);
CREATE INDEX IF NOT EXISTS FOR (m:Minister) ON (m.name);
CREATE INDEX IF NOT EXISTS FOR (d:Department) ON (d.name);
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=doctracer --cov-report=html

# Run integration tests
pytest tests/integration/
```

### Test Structure

```
tests/
├── test_api.py              # API endpoint tests
├── test_neo4j.py            # Database tests
├── test_extract.py          # Extraction tests
├── test_prompt.py           # AI prompt tests
└── integration/             # Integration tests
    ├── test_full_flow.py    # End-to-end tests
    └── test_data_loading.py # Data loading tests
```

### Example Test

```python
# tests/test_api.py
import pytest
from doctracer import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_endpoint(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
```

## 🚀 Deployment

### Production Setup

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "doctracer:create_app()"

# Or with uvicorn
uvicorn backend.api:app --host 0.0.0.0 --port 5000 --workers 4
```

### Docker Deployment

```bash
# Build Docker image
docker build -t doctracer-backend .

# Run container
docker run -p 5000:5000 \
  -e NEO4J_URI=bolt://neo4j:7687 \
  -e NEO4J_USER=neo4j \
  -e NEO4J_PASSWORD=password123 \
  doctracer-backend
```

### Environment Variables for Production

```bash
FLASK_ENV=production
FLASK_DEBUG=0
NEO4J_URI=bolt://your-neo4j-instance:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=secure_password
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Neo4j Connection Issues

```bash
# Check Neo4j is running
docker ps | grep neo4j

# Test connection
python -c "from neo4j import GraphDatabase; print('Connection successful')"

# Check Neo4j logs
docker logs neo4j
```

#### 2. Import Errors

```bash
# Check Python path
echo $PYTHONPATH

# Install in development mode
pip install -e .

# Check installed packages
pip list | grep doctracer
```

#### 3. Port Already in Use

```bash
# Kill process using port 5000
lsof -ti:5000 | xargs kill -9

# Or use a different port
python -m flask run --port 5001
```

#### 4. Database Connection Issues

```bash
# Verify Neo4j credentials
cypher-shell -u neo4j -p password123 -a localhost:7687

# Check environment variables
echo $NEO4J_URI
echo $NEO4J_USER
echo $NEO4J_PASSWORD
```

### Performance Optimization

#### 1. Database Optimization

```cypher
// Create indexes for better performance
CREATE INDEX IF NOT EXISTS FOR (g:Gazette) ON (g.published_date);
CREATE INDEX IF NOT EXISTS FOR (m:Minister) ON (m.name);

// Enable query caching
// Add to neo4j.conf:
dbms.query_cache_size=100
```

#### 2. API Optimization

```python
# Enable caching
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.memoize(timeout=300)
def get_structure():
    # Expensive operation
    pass
```

#### 3. Connection Pooling

```python
# Configure Neo4j connection pool
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    uri,
    auth=(user, password),
    max_connection_lifetime=30 * 60,
    max_connection_pool_size=50,
    connection_acquisition_timeout=2 * 60
)
```

## 📚 Development Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings
- Implement proper error handling

### Example Code Structure

```python
# doctracer/services/gazette_change_tracker.py
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class GazetteChange:
    """Represents a change between two gazettes."""
    type: str
    old_value: Optional[str]
    new_value: Optional[str]
    department: str

class GazetteChangeTracker:
    """Tracks changes between gazette publications."""
    
    def __init__(self, neo4j_interface):
        self.neo4j = neo4j_interface
    
    def track_changes(self, old_gazette_id: str, new_gazette_id: str) -> List[GazetteChange]:
        """Track changes between two gazettes."""
        # Implementation
        pass
```

### Error Handling

```python
# Proper error handling
from flask import jsonify
import logging

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500
```

## 🔗 Related Documentation

- [Frontend Setup Guide](./frontend-setup.md)
- [Neo4j Data Loading Guide](./neo4j-setup.md)
- [API Documentation](./api-documentation.md)
- [Deployment Guide](./deployment.md)

## 🆘 Support

If you encounter issues:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review the [GitHub Issues](https://github.com/yourusername/doctracer/issues)
3. Check Neo4j connectivity
4. Verify environment variables

---

**Happy Coding! 🚀**
