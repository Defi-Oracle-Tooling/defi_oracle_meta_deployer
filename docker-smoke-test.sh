#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "Starting smoke tests..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running${NC}"
    exit 1
fi

# Build and start the container
echo "Building and starting container..."
docker-compose up -d --build

# Wait for container to be ready
echo "Waiting for container to be ready..."
sleep 15

# Test 1: Check if services are running
echo "Testing if all services are running..."
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Services are running${NC}"
else
    echo -e "${RED}✗ Services are not running${NC}"
    exit 1
fi

# Test 2: Check application health endpoint
echo "Testing application health endpoint..."
if curl -s http://localhost:5000/health | grep -q "healthy"; then
    echo -e "${GREEN}✓ Application is healthy${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
    exit 1
fi

# Test 3: Check Prometheus metrics endpoint
echo "Testing Prometheus metrics endpoint..."
if curl -s http://localhost:5000/metrics | grep -q "web_requests_total"; then
    echo -e "${GREEN}✓ Metrics endpoint is working${NC}"
else
    echo -e "${RED}✗ Metrics endpoint is not working${NC}"
    exit 1
fi

# Test 4: Check Prometheus connection
echo "Testing Prometheus connection..."
if curl -s http://localhost:9090/-/healthy | grep -q "Prometheus is Healthy"; then
    echo -e "${GREEN}✓ Prometheus is connected${NC}"
else
    echo -e "${RED}✗ Prometheus connection failed${NC}"
    exit 1
fi

# Test 5: Check Grafana
echo "Testing Grafana connection..."
if curl -s http://localhost:3000/api/health | grep -q "ok"; then
    echo -e "${GREEN}✓ Grafana is accessible${NC}"
else
    echo -e "${RED}✗ Grafana connection failed${NC}"
    exit 1
fi

# Clean up
echo "Cleaning up..."
docker-compose down

echo -e "\n${GREEN}All smoke tests passed successfully!${NC}"