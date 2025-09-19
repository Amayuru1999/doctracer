# DocTracer Documentation

Welcome to the DocTracer documentation! This folder contains comprehensive setup guides for all components of the DocTracer system.

## 📚 Documentation Overview

### Setup Guides

- **[Frontend Setup Guide](./frontend-setup.md)** - Complete guide for setting up the React-based web interface
- **[Backend Setup Guide](./backend-setup.md)** - Python Flask/FastAPI backend setup and configuration
- **[Neo4j Data Loading Guide](./neo4j-setup.md)** - Database setup and data loading instructions

### Quick Start

1. **Start Neo4j Database**
   ```bash
   docker-compose up -d neo4j
   ```

2. **Set Up Backend**
   ```bash
   pip install -r requirements.txt
   python -m flask run
   ```

3. **Set Up Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Load Sample Data**
   ```bash
   python -m doctracer.cli.load_sample_data
   ```

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Neo4j         │
│   (React)       │◄──►│   (Flask/FastAPI)│◄──►│   Database      │
│   Port: 5173    │    │   Port: 5000    │    │   Port: 7474    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Access Points

- **Frontend Application**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Neo4j Browser**: http://localhost:7474
- **API Documentation**: http://localhost:5000/docs

## 📋 Prerequisites

- **Docker** - For Neo4j database
- **Python 3.8+** - For backend services
- **Node.js 18+** - For frontend development
- **Git** - For version control

## 🔧 Environment Configuration

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
```

## 🧪 Testing

### Run All Tests

```bash
# Backend tests
pytest

# Frontend tests
cd frontend && npm test

# Integration tests
pytest tests/integration/
```

### Test Data

```bash
# Load sample data
python -m doctracer.cli.load_sample_data

# Load specific government period
python -m doctracer.cli.load_sample_data --period=maithripala
```

## 🐛 Troubleshooting

### Common Issues

1. **Neo4j Connection Issues**
   - Check if Neo4j is running: `docker ps | grep neo4j`
   - Verify credentials in `.env` file
   - Check Neo4j logs: `docker logs neo4j`

2. **Backend Issues**
   - Verify Python dependencies: `pip list`
   - Check Flask logs: `python -m flask run --debug`
   - Test Neo4j connection: `python -c "from neo4j import GraphDatabase"`

3. **Frontend Issues**
   - Clear cache: `rm -rf node_modules package-lock.json && npm install`
   - Check build: `npm run build`
   - Verify API connection: `curl http://localhost:5000/api/health`

## 📖 Additional Resources

- [Main Project README](../README.md)
- [API Documentation](./api-documentation.md)
- [Deployment Guide](./deployment.md)
- [Contributing Guidelines](../CONTRIBUTOR.md)

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting sections in each guide
2. Review the [GitHub Issues](https://github.com/yourusername/doctracer/issues)
3. Check the logs for specific error messages
4. Verify all prerequisites are installed

---

**Happy Setup! 🚀**
