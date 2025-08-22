# DocTracer Web Visualizer Backend

A standalone Flask-based web application for visualizing government structure data and tracking changes in gazettes.

## 🚀 Features

- **Interactive Web Interface** - Beautiful HTML templates for data visualization
- **Neo4j Integration** - Direct connection to graph database
- **Change Tracking** - Monitor modifications in government structure
- **Graph Analysis** - Compare different gazette versions
- **RESTful API** - JSON endpoints for data access

## 🏗️ Architecture

```
web_visualizer/
├── app.py                 # Main Flask application entry point
├── web_visualizer.py     # Core Flask application logic
├── templates/            # HTML templates
│   ├── index.html       # Main dashboard
│   └── departments.html # Department analysis view
├── requirements.txt      # Python dependencies
├── run_web_visualizer.sh # Startup script
└── README.md            # This file
```

## 📋 Prerequisites

- Python 3.8+
- Neo4j database running
- Access to doctracer core modules

## 🔧 Setup

### 1. Install Dependencies

```bash
cd backend/web_visualizer
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the web_visualizer directory:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=True
```

### 3. Run the Application

#### Option A: Using Python directly
```bash
python app.py
```

#### Option B: Using Flask CLI
```bash
export FLASK_APP=web_visualizer
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5001
```

#### Option C: Using the startup script
```bash
chmod +x run_web_visualizer.sh
./run_web_visualizer.sh
```

## 🌐 Access Points

- **Main Application**: http://localhost:5001
- **API Endpoints**: http://localhost:5001/api/*
- **Health Check**: http://localhost:5001/health

## 📊 API Endpoints

### Core Endpoints

- `GET /` - Main dashboard
- `GET /departments` - Department analysis view
- `GET /api/health` - Health check
- `GET /api/structure` - Get government structure
- `GET /api/changes` - Get changes between gazettes

### Data Endpoints

- `GET /api/ministries` - List all ministries
- `GET /api/departments` - List all departments
- `GET /api/analytics` - Get analytics data
- `POST /api/compare` - Compare two gazettes

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=web_visualizer

# Run specific test file
pytest test_web_visualizer.py
```

## 🔍 Usage Examples

### 1. View Government Structure

Open http://localhost:5001 in your browser to see the main dashboard.

### 2. Analyze Department Changes

Navigate to the departments view to see detailed analysis of department modifications.

### 3. API Integration

```bash
# Get government structure
curl http://localhost:5001/api/structure

# Get changes between gazettes
curl "http://localhost:5001/api/changes?old=2023-01&new=2023-02"
```

## 🐳 Docker Support

The web visualizer can be run as part of the main DocTracer Docker setup:

```bash
# From the root directory
docker-compose up -d

# Or run standalone
cd backend/web_visualizer
docker build -t doctracer-web-visualizer .
docker run -p 5001:5001 doctracer-web-visualizer
```

## 🚀 Production Deployment

For production deployment:

```bash
# Set production environment
export FLASK_ENV=production
export FLASK_DEBUG=False

# Use Gunicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 "web_visualizer:app"
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j connection URI |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `password123` | Neo4j password |
| `FLASK_HOST` | `0.0.0.0` | Flask host binding |
| `FLASK_PORT` | `5001` | Flask port |
| `FLASK_DEBUG` | `False` | Enable debug mode |

### Neo4j Configuration

Ensure your Neo4j database has the required schema:

```cypher
// Create constraints and indexes
CREATE CONSTRAINT IF NOT EXISTS FOR (g:Gazette) REQUIRE g.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (m:Minister) REQUIRE m.name IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (d:Department) REQUIRE d.name IS UNIQUE;

// Create indexes for better performance
CREATE INDEX IF NOT EXISTS FOR (g:Gazette) ON (g.published_date);
CREATE INDEX IF NOT EXISTS FOR (m:Minister) ON (m.name);
CREATE INDEX IF NOT EXISTS FOR (d:Department) ON (d.name);
```

## 🐛 Troubleshooting

### Common Issues

1. **Neo4j Connection Failed**
   - Check if Neo4j is running
   - Verify connection credentials
   - Check firewall settings

2. **Module Import Errors**
   - Ensure doctracer core modules are accessible
   - Check Python path configuration
   - Verify all dependencies are installed

3. **Template Rendering Issues**
   - Check template file paths
   - Verify HTML syntax
   - Check Flask template configuration

### Debug Mode

Enable debug mode for detailed error information:

```bash
export FLASK_DEBUG=True
python app.py
```

## 📚 Related Documentation

- [Main DocTracer README](../README.md)
- [API Documentation](../api/README.md)
- [Neo4j Integration Guide](../neo4j/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

---

**Happy Visualizing! 🎯📊**
