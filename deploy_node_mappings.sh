#!/bin/bash

# DeFi Oracle Meta Deployer - Node Mapping and Cloudflare Integration Script
# This script handles the complete process of mapping RPC nodes and integrating with Cloudflare

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default values
DOMAIN="deployer.defi-oracle.io"
OUTPUT_DIR="nginx_configs"
DOCKER_PS_FILE="docker_ps_output.txt"
SERVER_IP="127.0.0.1" # Default, will be overridden by actual server IP
ENV_FILE=".env"
CONFIG_FILE="deployment_config.json"

# Function to display script usage
usage() {
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  -d, --domain DOMAIN       Domain name for node subdomains (default: deployer.defi-oracle.io)"
    echo "  -i, --ip IP               Server IP address (will attempt to detect if not provided)"
    echo "  -o, --output DIR          Output directory for nginx configurations (default: nginx_configs)"
    echo "  -f, --docker-file FILE    Docker PS output file (default: docker_ps_output.txt)"
    echo "  -e, --env-file FILE       Environment file for Cloudflare credentials (default: .env)"
    echo "  -c, --config-file FILE    Configuration file for deployment (default: deployment_config.json)"
    echo "  -h, --help                Display this help message"
    echo
}

# Function to create a configuration file
create_config_file() {
    cat > "$CONFIG_FILE" << EOF
{
  "name": "CustomResourceGroup",
  "location": "westus",
  "resource_group": "CustomResourceGroup",
  "vm_name": "CustomVM",
  "image": "UbuntuLTS",
  "admin_username": "customuser"
}
EOF
    echo -e "${GREEN}✓ Created configuration file: $CONFIG_FILE${NC}"
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain)
            DOMAIN="$2"
            shift 2
            ;;
        -i|--ip)
            SERVER_IP="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -f|--docker-file)
            DOCKER_PS_FILE="$2"
            shift 2
            ;;
        -e|--env-file)
            ENV_FILE="$2"
            shift 2
            ;;
        -c|--config-file)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option: $1${NC}"
            usage
            exit 1
            ;;
    esac
done

# Create configuration file
create_config_file

echo -e "${GREEN}=======================================================${NC}"
echo -e "${GREEN}DeFi Oracle Meta Deployer - Node Mapping and Cloudflare Integration${NC}"
echo -e "${GREEN}=======================================================${NC}"

# Step 1: Check for required tools
echo -e "\n${YELLOW}Step 1: Checking prerequisites...${NC}"
for cmd in docker python3 curl jq; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "${RED}Error: $cmd is required but not installed. Please install it and try again.${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✓ All required tools are installed.${NC}"

# Step 2: Check or create environment file for Cloudflare credentials
echo -e "\n${YELLOW}Step 2: Checking Cloudflare credentials...${NC}"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}Environment file $ENV_FILE not found. Creating it...${NC}"
    
    # Prompt for Cloudflare credentials
    read -p "Enter your Cloudflare API key: " CF_API_KEY
    read -p "Enter your Cloudflare email: " CF_EMAIL
    read -p "Enter your Cloudflare zone ID: " CF_ZONE_ID
    
    # Create .env file
    cat > "$ENV_FILE" << EOF
# Cloudflare credentials
CF_API_KEY=$CF_API_KEY
CF_EMAIL=$CF_EMAIL
CF_ZONE_ID=$CF_ZONE_ID
EOF
    
    echo -e "${GREEN}✓ Created $ENV_FILE file with Cloudflare credentials.${NC}"
else
    echo -e "${GREEN}✓ Environment file $ENV_FILE exists.${NC}"
    
    # Check if Cloudflare credentials are present
    if ! grep -q "CF_API_KEY" "$ENV_FILE" || ! grep -q "CF_EMAIL" "$ENV_FILE" || ! grep -q "CF_ZONE_ID" "$ENV_FILE"; then
        echo -e "${YELLOW}Cloudflare credentials not found in $ENV_FILE. Adding them...${NC}"
        
        # Prompt for Cloudflare credentials
        read -p "Enter your Cloudflare API key: " CF_API_KEY
        read -p "Enter your Cloudflare email: " CF_EMAIL
        read -p "Enter your Cloudflare zone ID: " CF_ZONE_ID
        
        # Append to .env file
        cat >> "$ENV_FILE" << EOF

# Cloudflare credentials
CF_API_KEY=$CF_API_KEY
CF_EMAIL=$CF_EMAIL
CF_ZONE_ID=$CF_ZONE_ID
EOF
        
        echo -e "${GREEN}✓ Added Cloudflare credentials to $ENV_FILE file.${NC}"
    else
        echo -e "${GREEN}✓ Cloudflare credentials found in $ENV_FILE.${NC}"
    fi
fi

# Step 3: Get server IP address if not provided
if [ "$SERVER_IP" == "127.0.0.1" ]; then
    echo -e "\n${YELLOW}Step 3: Detecting server IP address...${NC}"
    
    # Try to get public IP address using multiple services
    SERVER_IP=$(curl -s https://api.ipify.org || curl -s https://ifconfig.me || curl -s https://icanhazip.com)
    
    if [ -z "$SERVER_IP" ]; then
        echo -e "${RED}Error: Could not automatically detect server IP address. Please provide it with the -i option.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Detected server IP address: $SERVER_IP${NC}"
else
    echo -e "\n${YELLOW}Step 3: Using provided server IP address: $SERVER_IP${NC}"
fi

# Step 4: Generate or update Docker PS output file
echo -e "\n${YELLOW}Step 4: Generating Docker container information...${NC}"
if [ ! -f "$DOCKER_PS_FILE" ] || [ "$(find "$DOCKER_PS_FILE" -mmin +60)" ]; then
    echo -e "${YELLOW}Docker PS output file is missing or older than 60 minutes. Generating a new one...${NC}"
    docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Command}}\t{{.CreatedAt}}\t{{.Status}}\t{{.Ports}}\t{{.Names}}" > "$DOCKER_PS_FILE"
    echo -e "${GREEN}✓ Generated fresh Docker PS output in $DOCKER_PS_FILE.${NC}"
else
    echo -e "${GREEN}✓ Using existing Docker PS output file: $DOCKER_PS_FILE${NC}"
fi

# Step 5: Generate nginx configurations and Cloudflare DNS records
echo -e "\n${YELLOW}Step 5: Generating nginx configurations and Cloudflare DNS records...${NC}"
python3 generate_nginx_configs.py --docker-ps-file "$DOCKER_PS_FILE" --domain "$DOMAIN" --server-ip "$SERVER_IP" --output-dir "$OUTPUT_DIR"

# Check if generation was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to generate nginx configurations.${NC}"
    exit 1
fi

# Step 6: Deploy nginx configurations to system
echo -e "\n${YELLOW}Step 6: Deploying nginx configurations...${NC}"
if command -v nginx &> /dev/null; then
    # Check if nginx is installed
    NGINX_AVAILABLE_DIR="/etc/nginx/sites-available"
    NGINX_ENABLED_DIR="/etc/nginx/sites-enabled"
    
    # Create directories if they don't exist (useful for some distributions)
    if [ ! -d "$NGINX_AVAILABLE_DIR" ]; then
        sudo mkdir -p "$NGINX_AVAILABLE_DIR"
    fi
    if [ ! -d "$NGINX_ENABLED_DIR" ]; then
        sudo mkdir -p "$NGINX_ENABLED_DIR"
    fi
    
    # Deploy nginx configurations
    echo -e "${YELLOW}Copying nginx configurations to $NGINX_AVAILABLE_DIR...${NC}"
    for config_file in "$OUTPUT_DIR"/nginx_*.conf; do
        config_name=$(basename "$config_file")
        
        # Copy configuration to sites-available
        sudo cp "$config_file" "$NGINX_AVAILABLE_DIR/$config_name"
        
        # Create symlink in sites-enabled
        if [ ! -L "$NGINX_ENABLED_DIR/$config_name" ]; then
            sudo ln -sf "$NGINX_AVAILABLE_DIR/$config_name" "$NGINX_ENABLED_DIR/$config_name"
        fi
        
        echo -e "${GREEN}✓ Deployed $config_name configuration.${NC}"
    done
    
    # Test nginx configuration
    echo -e "${YELLOW}Testing nginx configuration...${NC}"
    if sudo nginx -t; then
        echo -e "${GREEN}✓ nginx configuration test successful.${NC}"
        
        # Reload nginx to apply changes
        echo -e "${YELLOW}Reloading nginx...${NC}"
        sudo systemctl reload nginx || sudo service nginx reload
        echo -e "${GREEN}✓ nginx reloaded.${NC}"
    else
        echo -e "${RED}Error: nginx configuration test failed.${NC}"
        echo -e "${YELLOW}Please check your nginx configurations and fix any issues.${NC}"
        echo -e "${YELLOW}Your generated configurations are in $OUTPUT_DIR/ directory.${NC}"
    fi
else
    echo -e "${YELLOW}nginx not installed. Skipping deployment.${NC}"
    echo -e "${YELLOW}Your generated configurations are in $OUTPUT_DIR/ directory.${NC}"
    echo -e "${YELLOW}Manual installation:${NC}"
    echo -e "${YELLOW}1. Install nginx: sudo apt-get install nginx${NC}"
    echo -e "${YELLOW}2. Copy configurations: sudo cp $OUTPUT_DIR/nginx_*.conf /etc/nginx/sites-available/${NC}"
    echo -e "${YELLOW}3. Enable configurations: sudo ln -s /etc/nginx/sites-available/nginx_*.conf /etc/nginx/sites-enabled/${NC}"
    echo -e "${YELLOW}4. Test and reload: sudo nginx -t && sudo systemctl reload nginx${NC}"
fi

# Step 7: Deploy Cloudflare DNS records and configure CDN
echo -e "\n${YELLOW}Step 7: Deploying Cloudflare DNS records and configuring CDN...${NC}"
read -p "Do you want to deploy Cloudflare DNS records? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Deploy DNS records
    echo -e "${YELLOW}Deploying DNS records from $OUTPUT_DIR/cloudflare_dns_records.json...${NC}"
    python3 cloudflare_integration.py --dns-records-file "$OUTPUT_DIR/cloudflare_dns_records.json" --zone-name "$DOMAIN"
    
    # Ask about additional Cloudflare configurations
    read -p "Do you want to set up Cloudflare page rules for caching and security? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Setting up Cloudflare page rules...${NC}"
        python3 cloudflare_integration.py --dns-records-file "$OUTPUT_DIR/cloudflare_dns_records.json" --zone-name "$DOMAIN" --setup-page-rules
    fi
    
    read -p "Do you want to set up Cloudflare firewall rules? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Setting up Cloudflare firewall rules...${NC}"
        python3 cloudflare_integration.py --dns-records-file "$OUTPUT_DIR/cloudflare_dns_records.json" --zone-name "$DOMAIN" --setup-firewall
    fi
    
    read -p "Do you want to purge Cloudflare cache? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Purging Cloudflare cache...${NC}"
        python3 cloudflare_integration.py --dns-records-file "$OUTPUT_DIR/cloudflare_dns_records.json" --zone-name "$DOMAIN" --purge-cache
    fi
    
    echo -e "${GREEN}✓ Cloudflare deployment completed.${NC}"
else
    echo -e "${YELLOW}Skipping Cloudflare deployment.${NC}"
    echo -e "${YELLOW}You can manually deploy later using:${NC}"
    echo -e "${YELLOW}python3 cloudflare_integration.py --dns-records-file $OUTPUT_DIR/cloudflare_dns_records.json --zone-name $DOMAIN${NC}"
fi

# Step 8: Generate a summary report
echo -e "\n${YELLOW}Step 8: Generating summary report...${NC}"
REPORT_FILE="$OUTPUT_DIR/deployment_report.txt"

cat > "$REPORT_FILE" << EOF
# DeFi Oracle Meta Deployer - Deployment Report
Date: $(date)
Domain: $DOMAIN
Server IP: $SERVER_IP

## Node Configurations
EOF

# Count the number of nginx configurations
CONFIG_COUNT=$(find "$OUTPUT_DIR" -name "nginx_*.conf" | wc -l)
echo "Total node configurations: $CONFIG_COUNT" >> "$REPORT_FILE"

# List configurations
echo "Configurations:" >> "$REPORT_FILE"
for config_file in "$OUTPUT_DIR"/nginx_*.conf; do
    config_name=$(basename "$config_file")
    server_name=$(grep "server_name" "$config_file" | head -1 | awk '{print $2}' | sed 's/;//')
    echo "- $config_name -> $server_name" >> "$REPORT_FILE"
done

# Add Cloudflare information
cat >> "$REPORT_FILE" << EOF

## Cloudflare Integration
DNS records file: $OUTPUT_DIR/cloudflare_dns_records.json
Cloudflare credentials file: $ENV_FILE

## Manual Steps
If you haven't deployed the nginx configurations:
1. Install nginx: sudo apt-get install nginx
2. Copy configurations: sudo cp $OUTPUT_DIR/nginx_*.conf /etc/nginx/sites-available/
3. Enable configurations: sudo ln -s /etc/nginx/sites-available/nginx_*.conf /etc/nginx/sites-enabled/
4. Test and reload: sudo nginx -t && sudo systemctl reload nginx

If you haven't deployed Cloudflare DNS records:
python3 cloudflare_integration.py --dns-records-file $OUTPUT_DIR/cloudflare_dns_records.json --zone-name $DOMAIN
EOF

echo -e "${GREEN}✓ Generated summary report: $REPORT_FILE${NC}"

# Step 9: Verify deployment
echo -e "\n${YELLOW}Step 9: Verifying deployment...${NC}"
if command -v curl &> /dev/null; then
    # Check if nginx is listening on port 80
    if netstat -tulpn 2>/dev/null | grep -q ":80 "; then
        echo -e "${GREEN}✓ nginx is listening on port 80.${NC}"
    else
        echo -e "${YELLOW}! nginx does not appear to be listening on port 80.${NC}"
    fi
    
    # Try to connect to one of the configured servers
    FIRST_SERVER=$(grep "server_name" "$OUTPUT_DIR"/nginx_*.conf | head -1 | awk '{print $2}' | sed 's/;//')
    if [ -n "$FIRST_SERVER" ]; then
        echo -e "${YELLOW}Attempting to connect to $FIRST_SERVER...${NC}"
        if curl -s --connect-timeout 5 -I "http://$FIRST_SERVER" &>/dev/null; then
            echo -e "${GREEN}✓ Successfully connected to $FIRST_SERVER.${NC}"
        else
            echo -e "${YELLOW}! Could not connect to $FIRST_SERVER.${NC}"
            echo -e "${YELLOW}  This is normal if DNS records haven't propagated yet.${NC}"
            echo -e "${YELLOW}  You may need to add an entry to your local hosts file for testing:${NC}"
            echo -e "${YELLOW}  $SERVER_IP $FIRST_SERVER${NC}"
        fi
    fi
fi

# Final message
echo -e "\n${GREEN}=======================================================${NC}"
echo -e "${GREEN}Deployment completed!${NC}"
echo -e "${GREEN}=======================================================${NC}"
echo -e "${YELLOW}Summary:${NC}"
echo -e "${YELLOW}- nginx configurations: $OUTPUT_DIR/nginx_*.conf${NC}"
echo -e "${YELLOW}- Cloudflare DNS records: $OUTPUT_DIR/cloudflare_dns_records.json${NC}"
echo -e "${YELLOW}- Deployment report: $REPORT_FILE${NC}"
echo
echo -e "${YELLOW}Next steps:${NC}"
echo -e "${YELLOW}1. Verify that your nginx configurations are working correctly${NC}"
echo -e "${YELLOW}2. Verify that your Cloudflare DNS records have propagated${NC}"
echo -e "${YELLOW}3. Test your RPC endpoints using curl or web browser${NC}"
echo
echo -e "${GREEN}Thank you for using DeFi Oracle Meta Deployer!${NC}"