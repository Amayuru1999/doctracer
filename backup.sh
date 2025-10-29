#!/bin/bash

# DocTracer Backup Script
# Creates backups of Neo4j database and application data

set -e

# Configuration
BACKUP_DIR="./data/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="doctracer_backup_$DATE"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[BACKUP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

print_status "Starting DocTracer backup..."

# Backup Neo4j database
print_status "Backing up Neo4j database..."
docker-compose -f docker-compose.prod.yml exec -T neo4j neo4j-admin database dump --to-path=/backups neo4j "$BACKUP_NAME.dump" || {
    print_error "Neo4j backup failed"
    exit 1
}

# Backup application configuration
print_status "Backing up application configuration..."
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_config.tar.gz" \
    .env \
    docker-compose.prod.yml \
    docker-compose.override.yml \
    nginx.conf 2>/dev/null || true

# Create backup manifest
print_status "Creating backup manifest..."
cat > "$BACKUP_DIR/${BACKUP_NAME}_manifest.txt" << EOF
DocTracer Backup Manifest
========================
Backup Date: $(date)
Backup Name: $BACKUP_NAME
Neo4j Dump: ${BACKUP_NAME}.dump
Config Archive: ${BACKUP_NAME}_config.tar.gz

Files Included:
- Neo4j database dump
- Environment configuration (.env)
- Docker Compose files
- Nginx configuration

Restore Instructions:
1. Copy backup files to target server
2. Restore Neo4j: docker-compose exec neo4j neo4j-admin database load --from-path=/backups neo4j ${BACKUP_NAME}.dump --overwrite-destination
3. Extract config: tar -xzf ${BACKUP_NAME}_config.tar.gz
4. Restart services: docker-compose -f docker-compose.prod.yml restart
EOF

# Cleanup old backups (keep last 7 days)
print_status "Cleaning up old backups..."
find "$BACKUP_DIR" -name "doctracer_backup_*" -type f -mtime +7 -delete 2>/dev/null || true

# Display backup info
BACKUP_SIZE=$(du -sh "$BACKUP_DIR/${BACKUP_NAME}.dump" 2>/dev/null | cut -f1 || echo "Unknown")
print_success "Backup completed successfully!"
print_success "Backup location: $BACKUP_DIR"
print_success "Backup size: $BACKUP_SIZE"
print_success "Files created:"
echo "  - ${BACKUP_NAME}.dump (Neo4j database)"
echo "  - ${BACKUP_NAME}_config.tar.gz (Configuration)"
echo "  - ${BACKUP_NAME}_manifest.txt (Backup info)"

print_status "Backup process finished."