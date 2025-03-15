#!/bin/bash

# Load environment variables
source .env

# ...existing code...

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

# ...existing code...
