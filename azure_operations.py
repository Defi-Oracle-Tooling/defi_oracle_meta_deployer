import os
import json
import logging
import subprocess
import requests
from flask import jsonify
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.storage import StorageManagementClient

# Initialize Azure credentials and Resource Management client
credential = DefaultAzureCredential()
subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
resource_client = ResourceManagementClient(credential, subscription_id)
network_client = NetworkManagementClient(credential, subscription_id)
storage_client = StorageManagementClient(credential, subscription_id)

# Function to validate configuration data

def validate_config_data(config):
    try:
        config_data = json.loads(config)
        required_fields = ['name', 'location', 'resource_group', 'vm_name', 'image', 'admin_username']
        for field in required_fields:
            if field not in config_data:
                return None, f"Missing required field: {field}"
        return config_data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid configuration: {str(e)}"

# Function to run a command

def run_command(cmd):
    try:
        logging.info("Executing command: %s", " ".join(cmd))
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
        return output
    except subprocess.CalledProcessError as e:
        logging.error("Command failed: %s", e.output)
        return f"Error: {e.output}"

# Function to create a resource group

def create_resource_group(config):
    config_data, error = validate_config_data(config)
    if error:
        return error
    cmd = ["az", "group", "create", "--name", config_data.get("name", "BesuResourceGroup"), "--location", config_data.get("location", "eastus")]
    return run_command(cmd)

# Function to deploy a virtual machine

def deploy_vm(config):
    config_data, error = validate_config_data(config)
    if error:
        return error
    cmd = [
        "az", "vm", "create",
        "--resource-group", config_data.get("resource_group", "BesuResourceGroup"),
        "--name", config_data.get("vm_name", "BesuNode1"),
        "--image", config_data.get("image", "UbuntuLTS"),
        "--admin-username", config_data.get("admin_username", "azureuser"),
        "--generate-ssh-keys"
    ]
    return run_command(cmd)

# Function to deploy via REST API

def deploy_via_rest_api(config):
    config_data, error = validate_config_data(config)
    if error:
        return error
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group = config_data.get("resource_group", "BesuResourceGroup")
    deployment_name = config_data.get("deployment_name", "BesuDeployment")
    api_version = "2021-04-01"
    url = (f"https://management.azure.com/subscriptions/{subscription_id}/"
           f"resourcegroups/{resource_group}/providers/Microsoft.Resources/deployments/"
           f"{deployment_name}?api-version={api_version}")
    payload = {
        "properties": {
            "mode": "Incremental",
            "templateLink": {
                "uri": config_data.get("template_uri", "https://path-to-your-template/template.json")
            },
            "parameters": {
                "vmName": { "value": config_data.get("vm_name", "BesuNode1") },
                "adminUsername": { "value": config_data.get("admin_username", "azureuser") },
                "adminPassword": { "value": os.getenv("AZURE_ADMIN_PASSWORD") }
            }
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('AZURE_ACCESS_TOKEN')}"
    }
    try:
        logging.info("Making REST API call to URL: %s", url)
        response = requests.put(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return json.dumps(response.json(), indent=4)
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        logging.error("REST API call failed: %s", str(e))
        return f"Exception occurred: {str(e)}"

# Function to create a network

def create_network(config):
    config_data, error = validate_config_data(config)
    if error:
        return error
    cmd = [
        "az", "network", "vnet", "create",
        "--resource-group", config_data.get("resource_group", "BesuResourceGroup"),
        "--name", config_data.get("vnet_name", "BesuVNet"),
        "--address-prefix", config_data.get("address_prefix", "10.0.0.0/16")
    ]
    return run_command(cmd)

# Function to create a storage account

def create_storage_account(config):
    config_data, error = validate_config_data(config)
    if error:
        return error
    cmd = [
        "az", "storage", "account", "create",
        "--resource-group", config_data.get("resource_group", "BesuResourceGroup"),
        "--name", config_data.get("storage_account_name", "besustorage"),
        "--sku", config_data.get("sku", "Standard_LRS"),
        "--kind", config_data.get("kind", "StorageV2"),
        "--location", config_data.get("location", "eastus")
    ]
    return run_command(cmd)

# Function to setup monitoring and alerts

def setup_monitoring_and_alerts(resource_group, vm_name):
    try:
        log_analytics_workspace = run_command([
            'az', 'monitor', 'log-analytics', 'workspace', 'create',
            '--resource-group', resource_group,
            '--workspace-name', f'{vm_name}-log-analytics'
        ])
        logging.info('Log Analytics workspace created: %s', log_analytics_workspace)
        enable_monitoring = run_command([
            'az', 'monitor', 'diagnostic-settings', 'create',
            '--resource-group', resource_group,
            '--workspace', f'{vm_name}-log-analytics',
            '--name', f'{vm_name}-monitoring',
            '--vm', vm_name,
            '--metrics', 'AllMetrics',
            '--logs', 'AllLogs'
        ])
        logging.info('Monitoring enabled for VM: %s', enable_monitoring)
        create_alert = run_command([
            'az', 'monitor', 'metrics', 'alert', 'create',
            '--resource-group', resource_group,
            '--name', f'{vm_name}-cpu-alert',
            '--scopes', f'/subscriptions/{os.getenv("AZURE_SUBSCRIPTION_ID")}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}',
            '--condition', 'avg Percentage CPU > 80',
            '--description', 'Alert when CPU usage is over 80%',
            '--action', 'email@example.com'
        ])
        logging.info('Alert rule created: %s', create_alert)
        return 'Monitoring and alerts setup successfully.'
    except Exception as e:
        logging.error('Failed to setup monitoring and alerts: %s', str(e))
        return f'Exception occurred: {str(e)}'

# Function to initialize Azure integrations

def initialize_azure_integration():
    try:
        # Example: Connect to Azure services using secure configurations
        subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        access_token = os.getenv('AZURE_ACCESS_TOKEN')
        if not subscription_id or not access_token:
            raise ValueError('Azure credentials are not set in environment variables')
        # Initialize Azure SDK or CLI commands here
        # Example: az login --service-principal -u <client_id> -p <client_secret> --tenant <tenant_id>
        logging.info('Azure integration initialized successfully')
    except Exception as e:
        logging.error(f'Failed to initialize Azure integration: {str(e)}')
        raise
