# DeFi Oracle Meta Deployer

Welcome to the DeFi Oracle Meta Deployer project. This project simplifies the deployment of decentralized finance (DeFi) oracles on various blockchain networks.

## Documentation
- [Introduction](docs/introduction.md)
- [Setup](docs/setup.md)
- [Usage](docs/usage.md)
- [API Reference](docs/api_reference.md)

## Features
- Simple Mode: Guided, minimal-input workflow.
- Expert Mode: Full customization and advanced options.

## Getting Started
To get started, follow the [Setup](docs/setup.md) instructions.

## Contributing
We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md) for more information.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Overview
This project is a simple web-based automation and orchestration tool for Azure. It allows you to create resource groups, deploy virtual machines, and perform deployments via REST API calls.

## Architecture
![Architecture Diagram](path/to/architecture-diagram.png)

## Prerequisites
- Python 3
- Azure CLI (make sure it’s in your system PATH)
- Python libraries: Flask, requests

## Installation
1. Clone the repository:
   ```sh
   git clone <repository_url>
   cd defi_oracle_meta_deployer
   ```
2. Install the required Python libraries:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```sh
   export AZURE_SUBSCRIPTION_ID=<your_subscription_id>
   export AZURE_ACCESS_TOKEN=<your_access_token>
   export AZURE_ADMIN_PASSWORD=<your_admin_password>
   export RESOURCE_GROUP=<your_resource_group>
   export ACR_NAME=<your_acr_name>
   export IMAGE_NAME=<your_image_name>
   ```

## Running the Application
1. Save and run the script:
   ```sh
   python app.py
   ```
2. Access the web interface:
   Open your browser and navigate to `http://localhost:5000`.

## Docker Usage
### Build Docker Image
To build the Docker image, run the following command:
```sh
docker build -t $ACR_NAME.azurecr.io/$IMAGE_NAME:latest .
```
### Run Docker Container
To run the Docker container, use the following command:
```sh
docker run -p 5000:5000 $ACR_NAME.azurecr.io/$IMAGE_NAME:latest
```
This will start the application in a Docker container and make it accessible at `http://localhost:5000`.

## Docker Setup
### Prerequisites
- Docker
- Docker Compose
- curl (for health checks)

### Configuration
1. Copy `.env.template` to `.env`:
```bash
cp .env.template .env
```
2. Update the `.env` file with your actual values:
- `SECRET_KEY`: Your Flask application secret key
- `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID
- `AZURE_ACCESS_TOKEN`: Your Azure access token
- `AZURE_ADMIN_PASSWORD`: Admin password for VM deployments
- `RESOURCE_GROUP`: Your Azure resource group
- `ACR_NAME`: Your Azure Container Registry name
- `IMAGE_NAME`: Your Docker image name

### Building and Running
Build and start the container:
```bash
docker-compose up --build
```
Run in detached mode:
```bash
docker-compose up -d
```
Stop the container:
```bash
docker-compose down
```

### Health Checks and Monitoring
The application includes:
- Health check endpoint at `/health`
- Prometheus metrics at `/metrics`
- Liveness probe at `/healthz/live`
- Readiness probe at `/healthz/ready`

### Resource Limits
The container is configured with:
- CPU limit: 1.0 cores
- Memory limit: 512MB
- CPU reservation: 0.25 cores
- Memory reservation: 256MB

### Volumes
- `./logs`: Application logs (persisted)
- `./ml_model.pkl`: Machine learning model (read-only)

### Security
- Non-root user inside container
- Read-only file system where possible
- Environment variables for sensitive data
- No sensitive data in image layers

## Usage
- **Create Resource Group**: Executes an Azure CLI command to create a resource group.
- **Deploy Virtual Machine**: Executes an Azure CLI command to deploy a VM.
- **Deploy via REST API**: Sends a sample REST API call to the Azure Resource Manager endpoint (ensure you set proper authentication details).

## Step-by-Step Guides
### Creating a Resource Group
1. Navigate to the web interface.
2. Select "Create Resource Group" from the dropdown menu.
3. Click "Execute".
4. Check the result section for the output.

### Deploying a Virtual Machine
1. Navigate to the web interface.
2. Select "Deploy Virtual Machine" from the dropdown menu.
3. Click "Execute".
4. Check the result section for the output.

### Deploying via REST API
1. Navigate to the web interface.
2. Select "Deploy via REST API" from the dropdown menu.
3. Click "Execute".
4. Check the result section for the output.

## Examples
### Configuration File Example
```json
{
  "vmName": { "value": "BesuNode1" },
  "adminUsername": { "value": "azureuser" },
  "adminPassword": { "value": "your_password" }
}
```

## Customization and Future Enhancements
- **Authentication for REST API Calls**: Replace the placeholders with valid values and consider integrating Azure Active Directory (OAuth2) for secure token management.
- **Extending Functionality**: Add more endpoints to handle additional Azure operations (such as provisioning networking components, setting up storage accounts, or monitoring deployments) following the pattern shown in the code.
- **User Interface Improvements**: Enhance the HTML interface with JavaScript and CSS to create a more dynamic, responsive dashboard. Consider integrating a visual workflow builder for orchestration tasks.

## Using Custom Configurations
1. Create a configuration file (e.g., `sample_config.json`) with the desired settings:
   ```json
   {
     "name": "CustomResourceGroup",
     "location": "westus",
     "resource_group": "CustomResourceGroup",
     "vm_name": "CustomVM",
     "image": "UbuntuLTS",
     "admin_username": "customuser"
   }
   ```
2. Navigate to the web interface.
3. Select the desired action (e.g., "Create Resource Group").
4. Provide the path to the configuration file in the input field.
5. Click "Execute".
6. Check the result section for the output.

## Version Information
- Python: 3.8 or higher
- Flask: 2.0.2
- Requests: 2.26.0
- Scikit-learn: 0.24.2
- Joblib: 1.0.1

## Prerequisites
- Azure CLI
- Docker

## Environment Variables
Create a `.env` file with the following variables:
```
AZURE_SUBSCRIPTION_ID=<your_subscription_id>
AZURE_ACCESS_TOKEN=<your_access_token>
AZURE_ADMIN_PASSWORD=<your_admin_password>
RESOURCE_GROUP=<your_resource_group>
ACR_NAME=<your_acr_name>
IMAGE_NAME=<your_image_name>
```

## Deployment Steps
1. **Create Azure Container Registry and Push Docker Image**:
    - Run the deploy script to create an Azure Container Registry (ACR) and push the Docker image to it.
    ```bash
    ./deploy.sh
    ```
    This script will:
    - Create an ACR if it doesn't exist.
    - Log in to the ACR.
    - Build the Docker image.
    - Tag the Docker image.
    - Push the Docker image to the ACR.

2. **Deploy to Azure**:
    - Follow the remaining steps in the deploy script to deploy your application to Azure.

## Additional Information
- For more details on Azure Container Registry, visit [Azure Container Registry Documentation](https://docs.microsoft.com/en-us/azure/container-registry/).

## Developer Documentation

### GitHub Actions CI/CD

The CI/CD pipeline is configured using GitHub Actions. The workflow file is located at `.github/workflows/ci.yml`.

### Environment Variables for CI/CD

Ensure the following secrets are set in your GitHub repository:

- `AZURE_SUBSCRIPTION_ID`
- `AZURE_ACCESS_TOKEN`
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_TENANT_ID`
- `RESOURCE_GROUP`
- `ACR_NAME`

### CI/CD Workflow

The CI/CD workflow performs the following steps:

1. **Checkout Code**: Checks out the code from the repository.
2. **Set up Docker Buildx**: Sets up Docker Buildx for building multi-platform images.
3. **Log in to Azure**: Logs in to Azure using a service principal.
4. **Create ACR if it doesn't exist**: Checks if the ACR exists and creates it if it doesn't.
5. **Log in to ACR**: Logs in to the Azure Container Registry.
6. **Build and Push Docker Image**: Builds the Docker image and pushes it to the ACR.

For more details on configuring GitHub Actions, visit [GitHub Actions Documentation](https://docs.github.com/en/actions).

# Azure Region Validator

## Setup

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

2. Run the CLI:
   ```sh
   python -m azure_region_validator.cli --subscription-id <SUBSCRIPTION_ID> --config-file <CONFIG_FILE>
   ```

## Configuration

Create a JSON configuration file with the following structure:

```json
{
  "excluded_regions": ["westus", "eastus2"]
}
```

### Configuration Files

The following configuration files are available:

- `sample_config.json`: Basic configuration for deploying a resource group and VM.
- `sample_config1.json`: Configuration for deploying a network and storage account.
- `sample_config2.json`: Advanced configuration for deploying multiple VMs and networks.
- `sample_config3.json`: Expert configuration for deploying a full infrastructure setup.

## Testing

Run tests using `pytest`:

```sh
pytest tests/
```

## Usage

To use the Azure Region Validator, run the CLI with the required parameters:

```sh
python -m azure_region_validator.cli --subscription-id <SUBSCRIPTION_ID> --config-file <CONFIG_FILE>
```

This will output the filtered regions in JSON format.

## Example Configuration File

Create a configuration file (e.g., `config.json`) with the desired settings:

```json
{
  "excluded_regions": ["westus", "eastus2"]
}
```

## CI/CD Pipeline

The CI/CD pipeline is configured using GitHub Actions. The workflow file is located at `.github/workflows/ci.yml`.

### Environment Variables for CI/CD

Ensure the following secrets are set in your GitHub repository:
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_ACCESS_TOKEN`
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_TENANT_ID`
- `RESOURCE_GROUP`
- `ACR_NAME`

### CI/CD Workflow

The CI/CD workflow performs the following steps:
1. **Checkout Code**: Checks out the code from the repository.
2. **Set up Python**: Sets up Python environment.
3. **Install Dependencies**: Installs the required dependencies.
4. **Run Tests**: Runs the unit tests.
5. **Lint Code**: Lints the code for style and quality.

For more details on configuring GitHub Actions, visit [GitHub Actions Documentation](https://docs.github.com/en/actions).