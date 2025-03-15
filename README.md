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
docker build -t defi_oracle_meta_deployer .
```

### Run Docker Container

To run the Docker container, use the following command:

```sh
docker run -p 5000:5000 defi_oracle_meta_deployer
```

This will start the application in a Docker container and make it accessible at `http://localhost:5000`.

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