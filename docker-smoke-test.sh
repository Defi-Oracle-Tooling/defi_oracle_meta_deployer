#!/bin/bash
set -e

# Load environment variables
source .env

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

check_endpoint() {
    local name=$1
    local url=$2
    local expected_status=$3

    echo -n "Checking $name... "
    status=$(curl -s -o /dev/null -w "%{http_code}" $url)
    
    if [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}OK${NC} (Status: $status)"
        return 0
    else
        echo -e "${RED}FAILED${NC} (Expected: $expected_status, Got: $status)"
        return 1
    fi
}

check_redis() {
    echo -n "Checking Redis connection... "
    if docker exec defi_oracle_meta_deployer-redis-1 redis-cli -a "$REDIS_PASSWORD" ping | grep -q "PONG"; then
        echo -e "${GREEN}OK${NC}"
        return 0
    else
        echo -e "${RED}FAILED${NC}"
        return 1
    fi
}

check_container_health() {
    local container=$1
    echo -n "Checking $container container health... "
    
    if [ "$(docker inspect --format='{{.State.Health.Status}}' defi_oracle_meta_deployer-$container-1)" = "healthy" ]; then
        echo -e "${GREEN}OK${NC}"
        return 0
    else
        echo -e "${RED}FAILED${NC}"
        return 1
    fi
}

# Initialize counters
TOTAL_TESTS=0
FAILED_TESTS=0

# Test main application endpoints
echo "Testing application endpoints..."
check_endpoint "Main application" "http://localhost:5000/health/live" "200" || ((FAILED_TESTS++))
((TOTAL_TESTS++))

check_endpoint "Metrics endpoint" "http://localhost:5000/metrics" "200" || ((FAILED_TESTS++))
((TOTAL_TESTS++))

# Test monitoring stack
echo -e "\nTesting monitoring stack..."
check_endpoint "Prometheus" "http://localhost:9090/-/healthy" "200" || ((FAILED_TESTS++))
((TOTAL_TESTS++))

check_endpoint "Grafana" "http://localhost:3000/api/health" "200" || ((FAILED_TESTS++))
((TOTAL_TESTS++))

check_endpoint "Node Exporter" "http://localhost:9100/metrics" "200" || ((FAILED_TESTS++))
((TOTAL_TESTS++))

check_endpoint "cAdvisor" "http://localhost:8080/healthz" "200" || ((FAILED_TESTS++))
((TOTAL_TESTS++))

# Test Redis connection
echo -e "\nTesting Redis..."
check_redis || ((FAILED_TESTS++))
((TOTAL_TESTS++))

# Test container health
echo -e "\nChecking container health..."
for container in app redis prometheus grafana; do
    check_container_health $container || ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
done

# Print summary
echo -e "\nTest Summary:"
echo "Total tests: $TOTAL_TESTS"
echo "Failed tests: $FAILED_TESTS"

# Check Prometheus targets
echo -e "\nChecking Prometheus targets..."
curl -s http://localhost:9090/api/v1/targets | grep -q '"health":"up"' || {
    echo -e "${RED}Some Prometheus targets are down${NC}"
    ((FAILED_TESTS++))
}
((TOTAL_TESTS++))

# Check Grafana datasource
echo -e "\nChecking Grafana Prometheus datasource..."
curl -s -u "admin:$GRAFANA_PASSWORD" http://localhost:3000/api/datasources/1/health | grep -q '"status":"success"' || {
    echo -e "${RED}Grafana Prometheus datasource is not healthy${NC}"
    ((FAILED_TESTS++))
}
((TOTAL_TESTS++))

# Final result
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed successfully!${NC}"
    exit 0
else
    echo -e "\n${RED}$FAILED_TESTS test(s) failed!${NC}"
    exit 1
fi