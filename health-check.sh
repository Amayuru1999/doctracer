#!/bin/bash

# DocTracer Health Check Script
echo "🏥 DocTracer Health Check"
echo "========================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_service() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Checking $service_name... "
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        return 1
    fi
}

check_docker_service() {
    local container_name=$1
    echo -n "Checking Docker container $container_name... "
    
    if docker ps --format "table {{.Names}}" | grep -q "$container_name"; then
        echo -e "${GREEN}✅ RUNNING${NC}"
        return 0
    else
        echo -e "${RED}❌ NOT RUNNING${NC}"
        return 1
    fi
}

echo "Docker Services:"
check_docker_service "doctracer-neo4j-prod"
check_docker_service "doctracer-backend-prod" 
check_docker_service "doctracer-frontend-prod"

echo ""
echo "HTTP Services:"
check_service "Frontend" "http://localhost"
check_service "Backend API" "http://localhost:5000/gazettes"
check_service "Neo4j Browser" "http://localhost:7474"

echo ""
echo "System Resources:"
echo -n "Disk Usage: "
df -h / | awk 'NR==2{printf "%s used of %s (%s)\n", $3, $2, $5}'

echo -n "Memory Usage: "
free -h | awk 'NR==2{printf "%s used of %s\n", $3, $2}'

echo -n "CPU Load: "
uptime | awk -F'load average:' '{print $2}'

echo ""
echo "Recent Logs (last 10 lines):"
echo "Backend:"
docker logs --tail 10 doctracer-backend-prod 2>/dev/null | tail -3

echo "Frontend:"
docker logs --tail 10 doctracer-frontend-prod 2>/dev/null | tail -3

echo ""
echo "Health check completed!"