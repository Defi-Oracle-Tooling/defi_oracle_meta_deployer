#!/bin/bash
set -e

# Load environment variables
source .env

# Generate unique passwords if not already set
if [ -z "$REDIS_PASSWORD" ]; then
    export REDIS_PASSWORD=$(openssl rand -base64 32)
    echo "Generated Redis password"
fi

if [ -z "$GRAFANA_PASSWORD" ]; then
    export GRAFANA_PASSWORD=$(openssl rand -base64 32)
    echo "Generated Grafana password"
fi

# Save passwords to .env file
cat > .env << EOL
REDIS_PASSWORD=${REDIS_PASSWORD}
GRAFANA_PASSWORD=${GRAFANA_PASSWORD}
EOL

# Create necessary directories
mkdir -p logs data

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
fi

if ! command -v docker compose &> /dev/null; then
    echo "Docker Compose is not installed. Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Pull the latest images
echo "Pulling latest Docker images..."
docker compose pull

# Build and start the services
echo "Building and starting services..."
docker compose up --build -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Check service health
echo "Checking service health..."
docker compose ps

# Initialize Grafana datasource and dashboards
echo "Configuring Grafana..."
until curl -s "http://localhost:3000/api/health" > /dev/null; do
    echo "Waiting for Grafana to be ready..."
    sleep 5
done

# Add Prometheus data source
curl -X POST -H "Content-Type: application/json" \
    -d '{"name":"Prometheus","type":"prometheus","url":"http://prometheus:9090","access":"proxy"}' \
    http://admin:${GRAFANA_PASSWORD}@localhost:3000/api/datasources

echo "Deployment completed successfully!"
echo "Access the services at:"
echo "Application: http://localhost:5000"
echo "Grafana: http://localhost:3000 (admin:${GRAFANA_PASSWORD})"
echo "Prometheus: http://localhost:9090"
echo "Node Exporter metrics: http://localhost:9100/metrics"
echo "cAdvisor: http://localhost:8080"

# Save sensitive information
echo "Saving credentials to credentials.txt (keep this file secure)"
cat > credentials.txt << EOL
Grafana:
URL: http://localhost:3000
Username: admin
Password: ${GRAFANA_PASSWORD}

Redis:
Password: ${REDIS_PASSWORD}
EOL

chmod 600 credentials.txt

echo "
Don't forget to:"
echo "1. Set up your firewall rules to restrict access to monitoring endpoints"
echo "2. Save the credentials.txt file in a secure location"
echo "3. Change the default passwords in production"

# Create Azure Container Registry if it doesn't exist
az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP &>/dev/null
if [ $? -ne 0 ]; then
  az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic
fi

# Log in to Azure Container Registry
az acr login --name $ACR_NAME

# Build Docker image
docker build -t $ACR_NAME.azurecr.io/$IMAGE_NAME:latest .

# Tag Docker image
docker tag $IMAGE_NAME:latest $ACR_NAME.azurecr.io/$IMAGE_NAME:latest

# Push Docker image to ACR
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:latest

# Call deploy_node_mappings.sh to map RPC nodes and integrate with Cloudflare
./deploy_node_mappings.sh
