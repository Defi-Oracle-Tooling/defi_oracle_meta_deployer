# Usage

This section will guide you through the usage of the DeFi Oracle Meta Deployer project.

## Simple Mode

1. Run the deployment script in simple mode:

```bash
python app.py --mode simple
```

2. Follow the on-screen instructions to complete the deployment.

## Expert Mode

1. Run the deployment script in expert mode:

```bash
python app.py --mode expert
```

2. Customize the configuration files as needed.

3. Follow the on-screen instructions to complete the deployment.

## Features

- **Create Resource Group**: Executes an Azure CLI command to create a resource group.
- **Deploy Virtual Machine**: Executes an Azure CLI command to deploy a virtual machine.
- **Deploy via REST API**: Sends a sample REST API call to the Azure Resource Manager endpoint (ensure you set proper authentication details).
- **Interactive Web Interface**: Provides a user-friendly web interface for executing actions.
- **Logging and Error Handling**: Implements detailed logging for all operations and provides error handling and feedback for failed operations.

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