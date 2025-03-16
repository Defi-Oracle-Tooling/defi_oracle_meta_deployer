#!/bin/bash
set -e

# Load environment variables
source .env

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
CONFIG_DIR="./config"
BACKUP_DIR="./backups"
LOG_DIR="./logs"
MONITOR_INTERVAL=30  # seconds

# Create necessary directories
mkdir -p "$CONFIG_DIR" "$BACKUP_DIR" "$LOG_DIR"

# Error handling
trap 'handle_error $? $LINENO $BASH_LINENO "$BASH_COMMAND" $(printf "::%s" ${FUNCNAME[@]:-})' ERR

handle_error() {
    local exit_code=$1
    local line_no=$2
    local bash_lineno=$3
    local last_command=$4
    local func_trace=$5

    echo "Error occurred in script at line: $line_no"
    echo "Command: $last_command"
    echo "Exit code: $exit_code"
    echo "Function trace: $func_trace"
    
    # Log error
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Error: $last_command (exit code: $exit_code) at line $line_no" >> "$LOG_DIR/error.log"
    
    # Cleanup on error
    cleanup
}

cleanup() {
    echo "Performing cleanup..."
    # Save container logs before cleanup
    if [ "$(docker ps -q)" ]; then
        docker ps -q | xargs -I {} docker logs {} > "$LOG_DIR/container_logs_$(date '+%Y%m%d_%H%M%S').log" 2>&1 || true
    fi
}

# Functions
check_deps() {
    local missing_deps=0
    declare -a required_deps=("docker" "docker-compose" "curl" "jq")
    
    for dep in "${required_deps[@]}"; do
        if ! command -v "$dep" >/dev/null 2>&1; then
            echo "Error: $dep is required but not installed."
            missing_deps=1
        fi
    done
    
    if [ $missing_deps -eq 1 ]; then
        echo "Please install missing dependencies and try again."
        exit 1
    fi
}

check_health() {
    local retries=0
    local max_retries=30
    echo "Checking application health..."
    while [ $retries -lt $max_retries ]; do
        if curl -s http://localhost:5000/health | jq -e '.status == "healthy"' >/dev/null; then
            echo "Application is healthy!"
            return 0
        fi
        ((retries++))
        echo "Health check attempt $retries of $max_retries..."
        sleep 2
    done
    echo "Application failed to become healthy after $max_retries attempts"
    return 1
}

monitor_resources() {
    echo "Starting resource monitoring..."
    while true; do
        DATE=$(date '+%Y-%m-%d %H:%M:%S')
        echo "=== Resource Usage at $DATE ===" >> "$LOG_DIR/resources.log"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" >> "$LOG_DIR/resources.log"
        echo "" >> "$LOG_DIR/resources.log"
        sleep $MONITOR_INTERVAL
    done
}

backup_config() {
    local backup_file="$BACKUP_DIR/config_$(date '+%Y%m%d_%H%M%S').tar.gz"
    echo "Creating configuration backup: $backup_file"
    tar -czf "$backup_file" -C "$CONFIG_DIR" .
    echo "Backup created successfully"
}

restore_config() {
    local backup_file=$1
    if [ ! -f "$backup_file" ]; then
        echo "Error: Backup file not found: $backup_file"
        return 1
    fi
    echo "Restoring configuration from: $backup_file"
    tar -xzf "$backup_file" -C "$CONFIG_DIR"
    echo "Configuration restored successfully"
}

start_services() {
    echo "Starting services..."
    docker-compose up -d
    echo -e "${GREEN}Services started${NC}"
    check_health
}

stop_services() {
    echo "Stopping services..."
    docker-compose down
    echo -e "${GREEN}Services stopped${NC}"
}

restart_services() {
    echo "Restarting services..."
    docker-compose restart
    echo -e "${GREEN}Services restarted${NC}"
}

scale_service() {
    local service=$1
    local replicas=$2
    echo "Scaling service $service to $replicas replicas..."
    docker-compose up -d --scale "$service=$replicas"
    echo -e "${GREEN}Service scaled${NC}"
}

view_logs() {
    if [ -z "$1" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$1"
    fi
}

view_metrics() {
    echo "Prometheus metrics available at: http://localhost:9090"
    echo "Grafana dashboard available at: http://localhost:3000"
    echo "Default Grafana credentials: admin/admin"
    
    # Display current container metrics
    echo "Current container metrics:"
    docker stats --no-stream
}

prune_system() {
    echo "Pruning unused Docker resources..."
    docker system prune -f
    docker volume prune -f
}

check_security() {
    echo "Running security checks..."
    # Check for containers running as root
    echo "Containers running as root:"
    docker ps -q | xargs docker inspect -f '{{.Name}} - User: {{.Config.User}}' | grep -E ": $|: root"
    
    # Check for exposed ports
    echo -e "\nExposed ports:"
    docker ps --format "{{.Names}} - {{.Ports}}"
}

show_help() {
    echo "Usage: $0 [command]"
    echo "Commands:"
    echo "  start               - Start all services"
    echo "  stop                - Stop all services"
    echo "  restart             - Restart all services"
    echo "  scale SERVICE NUM   - Scale a service to NUM instances"
    echo "  logs [SERVICE]      - View logs from all or specific service"
    echo "  metrics             - Show metrics dashboard URLs"
    echo "  health              - Check application health"
    echo "  monitor             - Start resource monitoring"
    echo "  backup-config       - Backup current configuration"
    echo "  restore-config FILE - Restore configuration from backup"
    echo "  prune              - Remove unused Docker resources"
    echo "  security           - Run security checks"
    echo "  help               - Show this help message"
}

clean_environment() {
    echo -e "${YELLOW}Warning: This will remove all containers and volumes. Are you sure? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]; then
        docker-compose down -v
        echo -e "${GREEN}Environment cleaned${NC}"
    fi
}

backup_data() {
    BACKUP_DIR="backups"
    BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    mkdir -p "$BACKUP_DIR"
    
    echo "Creating backup..."
    docker-compose stop
    
    # Create tarball of volume data
    tar -czf "$BACKUP_DIR/$BACKUP_NAME" -C /var/lib/docker/volumes/ defi_oracle_meta_deployer_app_data defi_oracle_meta_deployer_redis_data
    
    docker-compose start
    echo -e "${GREEN}Backup created: $BACKUP_DIR/$BACKUP_NAME${NC}"
}

restore_backup() {
    echo "Available backups:"
    ls -1 backups/*.tar.gz
    echo "Enter backup name to restore:"
    read -r BACKUP_NAME
    
    if [ -f "backups/$BACKUP_NAME" ]; then
        echo "Restoring from backup..."
        docker-compose down
        tar -xzf "backups/$BACKUP_NAME" -C /var/lib/docker/volumes/
        docker-compose up -d
        echo -e "${GREEN}Restore completed${NC}"
    else
        echo -e "${RED}Backup file not found${NC}"
    fi
}

update_containers() {
    echo "Updating containers..."
    docker-compose pull
    docker-compose up -d
    echo -e "${GREEN}Containers updated${NC}"
}

monitor_containers() {
    echo "Monitoring containers (press Ctrl+C to exit)..."
    docker stats
}

run_tests() {
    echo "Running smoke tests..."
    ./docker-smoke-test.sh
}

# Function to display script usage
show_usage() {
    echo "Usage: $0 [command]"
    echo "Commands:"
    echo "  start       - Start all services"
    echo "  stop        - Stop all services"
    echo "  restart     - Restart all services"
    echo "  logs        - View logs from all services"
    echo "  status      - Check status of all services"
    echo "  clean       - Remove all containers and volumes"
    echo "  update      - Update all container images"
    echo "  monitoring  - Show monitoring dashboard URLs"
}

# Function to check if docker-compose exists
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        echo "Error: docker-compose is not installed"
        exit 1
    fi
}

# Main script
check_deps

case "$1" in
    "start")
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        restart_services
        ;;
    "scale")
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "Error: Please provide service name and number of replicas"
            exit 1
        fi
        scale_service "$2" "$3"
        ;;
    "logs")
        view_logs "$2"
        ;;
    "metrics")
        view_metrics
        ;;
    "health")
        check_health
        ;;
    "monitor")
        monitor_resources
        ;;
    "backup-config")
        backup_config
        ;;
    "restore-config")
        if [ -z "$2" ]; then
            echo "Error: Please provide backup file path"
            exit 1
        fi
        restore_config "$2"
        ;;
    "prune")
        prune_system
        ;;
    "security")
        check_security
        ;;
    "help"|"")
        show_help
        ;;
    "status")
        show_status
        ;;
    "clean")
        clean_environment
        ;;
    "backup")
        backup_data
        ;;
    "restore")
        restore_backup
        ;;
    "update")
        update_containers
        ;;
    "monitor")
        monitor_containers
        ;;
    "test")
        run_tests
        ;;
    *)
        show_usage
        exit 1
        ;;
esac