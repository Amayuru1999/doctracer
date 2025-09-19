# Neo4j Data Loading Guide

This guide will help you set up Neo4j database and load data for the DocTracer application. Neo4j is used to store and query the complex relationships between government entities, ministers, departments, and gazettes.

## 📋 Prerequisites

- **Docker** - For running Neo4j container
- **Python 3.8+** - For data loading scripts
- **Git** - For version control

## 🚀 Quick Start

### 1. Start Neo4j with Docker

```bash
# Using Docker Compose (recommended)
docker-compose up -d neo4j

# Or using Docker directly
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  -e NEO4J_PLUGINS='["apoc"]' \
  -v neo4j_data:/data \
  -v neo4j_logs:/logs \
  -v neo4j_import:/var/lib/neo4j/import \
  neo4j:5.15
```

### 2. Wait for Neo4j to Start

```bash
# Check if Neo4j is running
docker ps | grep neo4j

# Check Neo4j logs
docker logs -f neo4j

# Wait for "Started" message in logs
```

### 3. Access Neo4j Browser

Open your browser and go to: **http://localhost:7474**

- **Username**: `neo4j`
- **Password**: `password123`

### 4. Load Sample Data

```bash
# Load sample gazette data
python -m doctracer.cli.load_sample_data

# Or load specific data files
python -m doctracer.cli.load_gazette data/gazettes_v4.csv
```

## 🛠️ Detailed Setup

### Docker Compose Configuration

The project includes a `docker-compose.yml` file with Neo4j configuration:

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
      - NEO4J_dbms_memory_heap_initial__size=512m
      - NEO4J_dbms_memory_heap_max__size=2G
      - NEO4J_dbms_memory_pagecache_size=1G
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_import:/var/lib/neo4j/import
      - neo4j_conf:/var/lib/neo4j/conf
      - ./conf/neo4j.conf:/var/lib/neo4j/conf/neo4j.conf:ro
    networks:
      - doctracer-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "password123", "RETURN 1"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Neo4j Configuration

The `conf/neo4j.conf` file contains important settings:

```properties
# Memory settings
dbms.memory.heap.initial_size=512m
dbms.memory.heap.max_size=2G
dbms.memory.pagecache.size=1G

# Security settings
dbms.security.procedures.unrestricted=apoc.*
dbms.security.procedures.allowlist=apoc.*

# Performance settings
dbms.query_cache_size=100
dbms.transaction.timeout=60s

# Logging
dbms.logs.http.enabled=true
dbms.logs.query.enabled=true
```

## 🗄️ Database Schema

### Node Types

```cypher
// Gazette nodes
CREATE (g:Gazette {
  id: '2023-01',
  published_date: '2023-01-15',
  title: 'Extraordinary Gazette No. 2023/01',
  url: 'https://example.com/gazette/2023-01'
});

// Minister nodes
CREATE (m:Minister {
  name: 'John Doe',
  position: 'Minister of Health',
  party: 'SLPP',
  start_date: '2023-01-15'
});

// Department nodes
CREATE (d:Department {
  name: 'Ministry of Health',
  type: 'Ministry',
  parent: 'Cabinet',
  established_date: '2020-01-01'
});

// Function nodes
CREATE (f:Function {
  name: 'Healthcare Policy',
  description: 'Development of healthcare policies',
  category: 'Policy'
});
```

### Relationship Types

```cypher
// Gazette contains ministers
(g:Gazette)-[:CONTAINS]->(m:Minister)

// Minister heads department
(m:Minister)-[:HEADS]->(d:Department)

// Department has functions
(d:Department)-[:HAS_FUNCTION]->(f:Function)

// Gazette appoints minister
(g:Gazette)-[:APPOINTS]->(m:Minister)

// Minister changes position
(m1:Minister)-[:SUCCEEDED_BY]->(m2:Minister)
```

### Constraints and Indexes

```cypher
// Create constraints
CREATE CONSTRAINT IF NOT EXISTS FOR (g:Gazette) REQUIRE g.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (m:Minister) REQUIRE m.name IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (d:Department) REQUIRE d.name IS UNIQUE;

// Create indexes for performance
CREATE INDEX IF NOT EXISTS FOR (g:Gazette) ON (g.published_date);
CREATE INDEX IF NOT EXISTS FOR (m:Minister) ON (m.name);
CREATE INDEX IF NOT EXISTS FOR (d:Department) ON (d.name);
CREATE INDEX IF NOT EXISTS FOR (f:Function) ON (f.category);
```

## 📊 Data Loading

### 1. Load Gazette Data

```bash
# Load from CSV file
python -m doctracer.cli.load_gazette data/gazettes_v4.csv

# Load with relationships
python -m doctracer.cli.load_gazette_relationships data/gazette_relationships_with_dates_v4.csv
```

### 2. Load Sample Data

```bash
# Load all sample data
python -m doctracer.cli.load_sample_data

# Load specific government period
python -m doctracer.cli.load_sample_data --period=maithripala
```

### 3. Load from JSON Files

```bash
# Load from output directory
python -m doctracer.cli.load_from_output output/base/maithripala/

# Load specific files
python -m doctracer.cli.load_from_output output/amendment/ranil/
```

### Data Loading Scripts

#### Gazette Loader

```python
# doctracer/cli/load_gazette.py
import pandas as pd
from neo4j import GraphDatabase

def load_gazette_data(csv_file):
    """Load gazette data from CSV file."""
    df = pd.read_csv(csv_file)
    
    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        with driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    CREATE (g:Gazette {
                        id: $id,
                        published_date: $date,
                        title: $title
                    })
                """, id=row['id'], date=row['date'], title=row['title'])
```

#### Relationship Loader

```python
# doctracer/cli/load_relationships.py
def load_relationships(csv_file):
    """Load relationships between entities."""
    df = pd.read_csv(csv_file)
    
    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        with driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MATCH (g:Gazette {id: $gazette_id})
                    MATCH (m:Minister {name: $minister_name})
                    CREATE (g)-[:APPOINTS]->(m)
                """, gazette_id=row['gazette_id'], minister_name=row['minister'])
```

## 🔍 Querying Data

### Basic Queries

```cypher
// Get all gazettes
MATCH (g:Gazette)
RETURN g
ORDER BY g.published_date DESC;

// Get ministers in a specific gazette
MATCH (g:Gazette {id: '2023-01'})-[:CONTAINS]->(m:Minister)
RETURN m;

// Get department structure
MATCH (d:Department)
OPTIONAL MATCH (d)-[:HAS_FUNCTION]->(f:Function)
RETURN d, f;
```

### Complex Queries

```cypher
// Get changes between gazettes
MATCH (g1:Gazette {id: '2023-01'})-[:CONTAINS]->(m1:Minister)
MATCH (g2:Gazette {id: '2023-02'})-[:CONTAINS]->(m2:Minister)
WHERE NOT (g2)-[:CONTAINS]->(m1)
RETURN m1.name as removed_minister, m2.name as new_minister;

// Get minister succession
MATCH (m1:Minister)-[:SUCCEEDED_BY]->(m2:Minister)
RETURN m1.name as previous, m2.name as current;

// Get department hierarchy
MATCH (d:Department)
OPTIONAL MATCH (d)-[:REPORTS_TO]->(parent:Department)
RETURN d.name as department, parent.name as parent_department;
```

### Analytics Queries

```cypher
// Count ministers by gazette
MATCH (g:Gazette)-[:CONTAINS]->(m:Minister)
RETURN g.id, g.published_date, count(m) as minister_count
ORDER BY g.published_date;

// Get most active departments
MATCH (d:Department)-[:HAS_FUNCTION]->(f:Function)
RETURN d.name, count(f) as function_count
ORDER BY function_count DESC;

// Track changes over time
MATCH (g:Gazette)
OPTIONAL MATCH (g)-[:CONTAINS]->(m:Minister)
RETURN g.published_date, count(m) as minister_count
ORDER BY g.published_date;
```

## 🧪 Testing Database

### Connection Test

```bash
# Test Neo4j connection
cypher-shell -u neo4j -p password123 -a localhost:7687

# Run test query
cypher-shell -u neo4j -p password123 -a localhost:7687 "RETURN 1 as test"
```

### Data Validation

```cypher
// Check data integrity
MATCH (g:Gazette)
RETURN count(g) as gazette_count;

MATCH (m:Minister)
RETURN count(m) as minister_count;

MATCH (d:Department)
RETURN count(d) as department_count;

// Check relationships
MATCH ()-[r]->()
RETURN type(r) as relationship_type, count(r) as count
ORDER BY count DESC;
```

### Performance Testing

```cypher
// Test query performance
PROFILE MATCH (g:Gazette)-[:CONTAINS]->(m:Minister)
RETURN g.id, count(m) as minister_count
ORDER BY g.published_date;

// Check index usage
EXPLAIN MATCH (g:Gazette {id: '2023-01'})
RETURN g;
```

## 🚀 Production Setup

### Memory Configuration

```properties
# neo4j.conf for production
dbms.memory.heap.initial_size=1G
dbms.memory.heap.max_size=4G
dbms.memory.pagecache.size=2G
```

### Security Configuration

```properties
# Enable authentication
dbms.security.auth_enabled=true

# Configure SSL
dbms.ssl.policy.https.enabled=true
dbms.ssl.policy.bolt.enabled=true
```

### Backup and Recovery

```bash
# Create backup
docker exec neo4j neo4j-admin dump --database=neo4j --to=/var/lib/neo4j/import/backup.dump

# Restore from backup
docker exec neo4j neo4j-admin load --from=/var/lib/neo4j/import/backup.dump --database=neo4j --force
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Connection Refused

```bash
# Check if Neo4j is running
docker ps | grep neo4j

# Check Neo4j logs
docker logs neo4j

# Restart Neo4j
docker restart neo4j
```

#### 2. Authentication Failed

```bash
# Reset password
docker exec -it neo4j neo4j-admin set-initial-password newpassword

# Check auth configuration
docker exec -it neo4j cat /var/lib/neo4j/conf/neo4j.conf | grep auth
```

#### 3. Memory Issues

```bash
# Check memory usage
docker stats neo4j

# Increase memory limits
docker run -d \
  -e NEO4J_dbms_memory_heap_max__size=4G \
  -e NEO4J_dbms_memory_pagecache_size=2G \
  neo4j:5.15
```

#### 4. Data Loading Issues

```bash
# Check import directory
docker exec -it neo4j ls -la /var/lib/neo4j/import/

# Check file permissions
docker exec -it neo4j chmod 644 /var/lib/neo4j/import/*.csv
```

### Performance Optimization

#### 1. Index Optimization

```cypher
// Create composite indexes
CREATE INDEX IF NOT EXISTS FOR (g:Gazette) ON (g.published_date, g.id);

// Create full-text indexes
CREATE FULLTEXT INDEX gazette_title FOR (g:Gazette) ON EACH [g.title];
```

#### 2. Query Optimization

```cypher
// Use EXPLAIN to analyze queries
EXPLAIN MATCH (g:Gazette)-[:CONTAINS]->(m:Minister)
RETURN g.id, count(m);

// Use PROFILE to measure performance
PROFILE MATCH (g:Gazette)-[:CONTAINS]->(m:Minister)
RETURN g.id, count(m);
```

#### 3. Memory Optimization

```properties
# neo4j.conf optimizations
dbms.query_cache_size=100
dbms.transaction.timeout=60s
dbms.memory.pagecache.size=2G
```

## 📚 Data Management

### Export Data

```bash
# Export to CSV
cypher-shell -u neo4j -p password123 -a localhost:7687 \
  "MATCH (g:Gazette) RETURN g.id, g.published_date, g.title" \
  --format=csv > gazettes.csv
```

### Import Data

```bash
# Import from CSV
cypher-shell -u neo4j -p password123 -a localhost:7687 \
  "LOAD CSV WITH HEADERS FROM 'file:///gazettes.csv' AS row
   CREATE (g:Gazette {id: row.id, published_date: row.date, title: row.title})"
```

### Data Migration

```cypher
// Migrate data between databases
MATCH (g:Gazette)
CALL apoc.export.cypher.data([g], null, "export.cypher", {})
YIELD file, source, format, nodes, relationships, properties, time, rows, batchSize, batches, done, data
RETURN file, source, format, nodes, relationships, properties, time, rows, batchSize, batches, done, data;
```

## 🔗 Related Documentation

- [Frontend Setup Guide](./frontend-setup.md)
- [Backend Setup Guide](./backend-setup.md)
- [API Documentation](./api-documentation.md)
- [Deployment Guide](./deployment.md)

## 🆘 Support

If you encounter issues:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review Neo4j logs: `docker logs neo4j`
3. Check database connectivity
4. Verify data loading scripts

---

**Happy Data Loading! 🚀**
