#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to log messages
log() {
    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if a container is healthy
check_health() {
    local container=$1
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if [ "$(docker inspect --format='{{.State.Health.Status}}' $container 2>/dev/null)" == "healthy" ]; then
            return 0
        fi
        log "${YELLOW}Waiting for $container to become healthy (attempt $attempt/$max_attempts)${NC}"
        sleep 2
        ((attempt++))
    done
    return 1
}

# Function to check application logs
check_logs() {
    local container=$1
    local lines=${2:-100}
    docker logs --tail $lines $container
}

case "$1" in
    "start")
        log "${GREEN}Starting services...${NC}"
        docker-compose up -d
        if check_health defi_oracle_app; then
            log "${GREEN}Application is healthy!${NC}"
        else
            log "${RED}Application failed to become healthy${NC}"
            check_logs defi_oracle_app
            exit 1
        fi
        ;;
    
    "stop")
        log "${YELLOW}Stopping services...${NC}"
        docker-compose down
        ;;
    
    "restart")
        log "${YELLOW}Restarting services...${NC}"
        docker-compose down
        docker-compose up -d
        if check_health defi_oracle_app; then
            log "${GREEN}Application successfully restarted!${NC}"
        else
            log "${RED}Application failed to restart properly${NC}"
            check_logs defi_oracle_app
            exit 1
        fi
        ;;
    
    "logs")
        container=${2:-defi_oracle_app}
        lines=${3:-100}
        check_logs $container $lines
        ;;
    
    "status")
        log "Checking service status..."
        docker-compose ps
        ;;
    
    "test")
        log "${YELLOW}Running smoke tests...${NC}"
        ./docker-smoke-test.sh
        ;;
    
    "monitor")
        log "Opening Prometheus monitoring..."
        xdg-open http://localhost:9090 2>/dev/null || open http://localhost:9090 2>/dev/null || echo "Please open http://localhost:9090 in your browser"
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|logs|status|test|monitor}"
        echo "  start    - Start all services"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - View logs (optional: container name and number of lines)"
        echo "  status   - Check service status"
        echo "  test     - Run smoke tests"
        echo "  monitor  - Open Prometheus monitoring"
        exit 1
        ;;
esac