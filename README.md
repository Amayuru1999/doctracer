# DocTracer - Government Gazette Change Tracking System

DocTracer is a powerful system for tracking and analyzing changes in government gazettes. It helps you monitor modifications in ministerial appointments, departments, laws, and functions across different gazette publications with a beautiful web interface.

## 🚀 Features

- **Interactive Web Dashboard** - Beautiful React-based UI for visualizing government structure
- **Network Visualization** - Interactive network graphs showing relationships between entities
- **Web Visualizer Backend** - Standalone Flask application for traditional web-based analysis
- **Change Tracking** - Monitor ministerial appointments, departments, laws, and functions
- **Real-time Analytics** - Track changes between different gazette publications
- **Neo4j Database** - Graph database for storing and querying complex relationships
- **RESTful API** - Python Flask backend for data processing and analysis
- **Command-line Interface** - CLI tool for batch processing and automation

## 🏗️ Architecture

```
DocTracer/
├── backend/                 # Python backend services
│   ├── web_visualizer/     # Standalone Flask web visualizer
│   │   ├── app.py         # Main Flask application entry point
│   │   ├── web_visualizer.py # Core Flask application logic
│   │   ├── templates/     # HTML templates for web interface
│   │   ├── requirements.txt # Python dependencies
│   │   └── Dockerfile     # Container configuration
│   └── __init__.py        # Backend package initialization
├── frontend/               # React TypeScript web application
├── doctracer/              # Core Python package
├── neo4j/                  # Neo4j graph database
├── data/                   # Gazette data files
├── output/                 # Generated reports and analysis
└── tests/                  # Test suite and examples
```

## 📋 Prerequisites

- **Docker & Docker Compose** - For running Neo4j and services
- **Python 3.8+** - For backend API and web visualizer
- **Node.js 18+** - For frontend development
- **Git** - For version control

## 🚀 Production Deployment

### Digital Ocean Deployment (Recommended)

Deploy DocTracer to Digital Ocean with one command:

```bash
# On your Digital Ocean droplet
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/doctracer/main/deploy-digitalocean.sh | bash
```

See [README-DEPLOYMENT.md](README-DEPLOYMENT.md) for detailed deployment instructions.

### Local Development

## 🐳 Quick Start with Docker

The fastest way to get everything running locally:

```bash
# Clone the repository
git clone https://github.com/yourusername/doctracer.git
cd doctracer

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:5000
# Web Visualizer: http://localhost:5001
# Neo4j Browser: http://localhost:7474
```

## 🔧 Detailed Setup Instructions

### 1. Clone and Setup Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/doctracer.git
cd doctracer

# Create environment file
cp env.example .env
```

### 2. Neo4j Database Setup

#### Option A: Using Docker (Recommended)

```bash
# Create Neo4j container
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  -e NEO4J_PLUGINS='["apoc"]' \
  -v neo4j_data:/data \
  -v neo4j_logs:/logs \
  -v neo4j_import:/var/lib/neo4j/import \
  neo4j:5.15

# Wait for Neo4j to start (check logs)
docker logs -f neo4j
```

#### Option B: Using Docker Compose

Create `docker-compose.yml` in the root directory:

```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:5.15
    container_name: doctracer-neo4j
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/password123
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_import:/var/lib/neo4j/import
      - ./conf/neo4j.conf:/var/lib/neo4j/conf/neo4j.conf
    networks:
      - doctracer-network
    restart: unless-stopped

  backend:
    build: .
    container_name: doctracer-backend
    ports:
      - "5000:5000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=password123
      - FLASK_ENV=development
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    networks:
      - doctracer-network
    depends_on:
      - neo4j
    restart: unless-stopped

  web-visualizer:
    build: ./backend/web_visualizer
    container_name: doctracer-web-visualizer
    ports:
      - "5001:5001"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=password123
      - FLASK_HOST=0.0.0.0
      - FLASK_PORT=5001
      - FLASK_DEBUG=1
    volumes:
      - ./data:/app/data:ro
      - ./output:/app/output:ro
    networks:
      - doctracer-network
    depends_on:
      - neo4j
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: doctracer-frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:5000
    networks:
      - doctracer-network
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  neo4j_data:
  neo4j_logs:
  neo4j_import:

networks:
  doctracer-network:
    driver: bridge
```

Then run:

```bash
docker-compose up -d
```

### 3. Backend Setup

#### Install Python Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install additional development dependencies
pip install -r requirements-dev.txt  # if available
```

#### Environment Configuration

Create `.env` file in the root directory:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_APP=doctracer

# API Keys (if using external services)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/doctracer
```

#### Run Backend Server

```bash
# Development mode
python -m flask run --host=0.0.0.0 --port=5000

# Or using the CLI
python -m doctracer.cli.server

# Production mode
gunicorn -w 4 -b 0.0.0.0:5000 "doctracer:create_app()"
```

### 4. Web Visualizer Backend Setup

The web visualizer is a standalone Flask application that provides traditional web-based analysis:

#### Install Dependencies

```bash
cd backend/web_visualizer
pip install -r requirements.txt
```

#### Environment Configuration

Create `.env` file in the `backend/web_visualizer` directory:

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

#### Run Web Visualizer

```bash
# Development mode
python app.py

# Or using Flask CLI
export FLASK_APP=web_visualizer
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5001

# Or using the startup script
chmod +x run_web_visualizer.sh
./run_web_visualizer.sh
```

**Access the web visualizer at**: http://localhost:5001

### 5. Frontend Setup

#### Install Node.js Dependencies

```bash
cd frontend

# Install dependencies
npm install

# Or using yarn
yarn install
```

#### Environment Configuration

Create `.env` file in the frontend directory:

```bash
# API Configuration
VITE_API_URL=http://localhost:5000
VITE_APP_TITLE=DocTracer

# Development Configuration
VITE_DEV_MODE=true
```

#### Run Frontend Development Server

```bash
# Development mode
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### 6. Database Initialization

#### Connect to Neo4j

```bash
# Using cypher-shell
cypher-shell -u neo4j -p password123 -a localhost:7687

# Or access Neo4j Browser at http://localhost:7474
# Username: neo4j
# Password: password123
```

#### Create Initial Schema

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

## 🚀 Running the Application

### Start All Services

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or start individually:
# 1. Start Neo4j
docker start neo4j

# 2. Start Backend
source .venv/bin/activate
python -m flask run

# 3. Start Web Visualizer
cd backend/web_visualizer
python app.py

# 4. Start Frontend
cd frontend
npm run dev
```

### Access Points

- **Frontend Application**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Web Visualizer**: http://localhost:5001
- **Neo4j Browser**: http://localhost:7474
- **API Documentation**: http://localhost:5000/docs (if Swagger is enabled)

## 📊 Using the Application

### 1. Modern Web Interface (Frontend)

1. **Open** http://localhost:5173 in your browser
2. **Navigate** between different views:
   - Dashboard: Overview of government structure
   - Ministries: Tree visualization of ministries and departments
   - Departments: Detailed department analysis
   - Analytics: Change tracking and statistics
   - Network: Interactive network graph

### 2. Traditional Web Interface (Web Visualizer)

1. **Open** http://localhost:5001 in your browser
2. **Use** the traditional web-based interface for:
   - Government structure analysis
   - Department change tracking
   - Gazette comparison
   - Data export and reporting

### 3. API Endpoints

```bash
# Get government structure
curl http://localhost:5000/api/structure

# Get changes between gazettes
curl http://localhost:5000/api/changes?old=2023-01&new=2023-02

# Get analytics data
curl http://localhost:5000/api/analytics

# Web visualizer endpoints
curl http://localhost:5001/api/structure
curl http://localhost:5001/api/changes
```

### 4. Command Line Interface

```bash
# Track changes between gazettes
python -m doctracer.cli.track_changes old_gazette.json new_gazette.json

# Extract data from PDF
python -m doctracer.cli.extract gazette.pdf

# Generate reports
python -m doctracer.cli.report --format=json --output=report.json
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_extract.py

# Run with coverage
pytest --cov=doctracer

# Run frontend tests
cd frontend
npm test

# Run web visualizer tests
cd backend/web_visualizer
pytest
```

### Test Data

Sample data is available in the `data/` directory:

```bash
# Load sample gazette data
python -m doctracer.cli.load_sample_data

# Or manually load specific files
python -m doctracer.cli.load_gazette data/gazettes_v4.csv
```

## 🔧 Development

### Project Structure

```
doctracer/
├── backend/                 # Backend services
│   ├── web_visualizer/     # Standalone web visualizer
│   │   ├── app.py         # Flask application entry point
│   │   ├── web_visualizer.py # Core application logic
│   │   ├── templates/     # HTML templates
│   │   ├── requirements.txt # Dependencies
│   │   └── Dockerfile     # Container configuration
│   └── __init__.py        # Package initialization
├── doctracer/              # Main Python package
│   ├── cli/               # Command-line interface
│   ├── extract/           # Data extraction modules
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   └── prompt/            # AI prompt management
├── frontend/              # React application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts
│   │   └── assets/        # Static assets
│   └── public/            # Public files
├── tests/                 # Test suite
├── data/                  # Data files
├── output/                # Generated output
└── docs/                  # Documentation
```

### Adding New Features

1. **Backend**: Add new models, services, and API endpoints
2. **Web Visualizer**: Extend Flask application with new views
3. **Frontend**: Create new React components and routes
4. **Database**: Update Neo4j schema and queries
5. **Tests**: Add corresponding test cases

### Code Style

```bash
# Python formatting
black doctracer/
isort doctracer/

# Frontend formatting
cd frontend
npm run lint
npm run format
```

## 🐛 Troubleshooting

### Common Issues

#### Neo4j Connection Issues

```bash
# Check if Neo4j is running
docker ps | grep neo4j

# Check Neo4j logs
docker logs neo4j

# Reset Neo4j password
docker exec -it neo4j neo4j-admin set-initial-password newpassword
```

#### Backend Issues

```bash
# Check Flask logs
python -m flask run --debug

# Verify environment variables
echo $NEO4J_URI
echo $NEO4J_USER
echo $NEO4J_PASSWORD

# Test Neo4j connection
python -c "from neo4j import GraphDatabase; print('Connection successful')"
```

#### Web Visualizer Issues

```bash
# Check Flask logs
cd backend/web_visualizer
python app.py

# Verify environment variables
echo $NEO4J_URI
echo $NEO4J_USER
echo $NEO4J_PASSWORD

# Test standalone operation
python -c "from web_visualizer import app; print('App loaded successfully')"
```

#### Frontend Issues

```bash
# Clear node modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check for build errors
npm run build

# Verify API connection
curl http://localhost:5000/api/health
```

### Performance Optimization

```bash
# Enable Neo4j query caching
# Add to neo4j.conf:
dbms.query_cache_size=100

# Enable Flask caching
pip install flask-caching

# Optimize frontend build
npm run build:analyze
```

## 📚 API Documentation

### Main Endpoints

- `GET /api/structure` - Get government structure
- `GET /api/changes` - Get changes between gazettes
- `GET /api/analytics` - Get analytics data
- `POST /api/gazette` - Upload new gazette
- `GET /api/health` - Health check

### Web Visualizer Endpoints

- `GET /` - Main dashboard
- `GET /departments` - Department analysis view
- `GET /api/structure` - Get government structure
- `GET /api/changes` - Get changes between gazettes

### Authentication

Currently, the API is open for development. For production:

```bash
# Enable authentication
pip install flask-jwt-extended

# Set secret key
export JWT_SECRET_KEY=your_secret_key
```

## 🚀 Deployment

### Production Setup

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Or deploy to cloud platforms
# - AWS ECS
# - Google Cloud Run
# - Azure Container Instances
```

### Environment Variables for Production

```bash
FLASK_ENV=production
FLASK_DEBUG=0
NEO4J_URI=bolt://your-neo4j-instance:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=secure_password
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/doctracer/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/doctracer/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/doctracer/discussions)

## 🙏 Acknowledgments

- Neo4j team for the excellent graph database
- React team for the amazing frontend framework
- Flask team for the lightweight Python web framework
- All contributors and users of DocTracer

---

**Happy Tracking! 🎯📊**
