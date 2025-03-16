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
from azure.mgmt.monitor import MonitorManagementClient
from azure.core.exceptions import AzureError
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Initialize Azure credentials and Resource Management client
credential = DefaultAzureCredential()
subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
resource_client = ResourceManagementClient(credential, subscription_id)
network_client = NetworkManagementClient(credential, subscription_id)
storage_client = StorageManagementClient(credential, subscription_id)

# Function to validate configuration data

def validate_config_data(config):
    """Enhanced config validation with detailed error checking"""
    try:
        if isinstance(config, str):
            config_data = json.loads(config)
        else:
            config_data = config

        errors = []
        
        # Required fields validation
        required_fields = {
            'name': r'^[a-zA-Z0-9-_]{3,64}$',
            'location': r'^[a-zA-Z][a-zA-Z0-9-]+$',
            'resource_group': r'^[a-zA-Z0-9-_]{3,64}$',
            'vm_name': r'^[a-zA-Z][a-zA-Z0-9-]{2,63}$',
            'admin_username': r'^[a-zA-Z][a-zA-Z0-9-]{2,31}$'
        }

        for field, pattern in required_fields.items():
            value = config_data.get(field)
            if not value:
                errors.append(f"Missing required field: {field}")
            elif not re.match(pattern, value):
                errors.append(f"Invalid {field} format")

        # Network configuration validation
        if 'network' in config_data:
            network = config_data['network']
            if not re.match(r'^[a-zA-Z0-9-_]{2,64}$', network.get('vnet', '')):
                errors.append("Invalid virtual network name")
            if 'subnet_prefix' in network:
                if not re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}\/[0-9]{1,2}$', network['subnet_prefix']):
                    errors.append("Invalid subnet prefix format")

        # Security validation
        if 'security' in config_data:
            security = config_data['security']
            for rule in security.get('firewall_rules', []):
                if not 0 <= int(rule.get('port', -1)) <= 65535:
                    errors.append(f"Invalid port number: {rule.get('port')}")

        # Monitoring validation
        if config_data.get('monitoring', {}).get('enabled'):
            monitoring = config_data['monitoring']
            try:
                retention = int(monitoring.get('retention', 0))
                if not 1 <= retention <= 365:
                    errors.append("Retention period must be between 1 and 365 days")
            except ValueError:
                errors.append("Invalid retention period value")

        return (None, errors) if errors else (config_data, None)

    except json.JSONDecodeError as e:
        return None, f"Invalid JSON format: {str(e)}"
    except Exception as e:
        logger.error(f"Configuration validation error: {str(e)}")
        return None, f"Validation error: {str(e)}"

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

def setup_monitoring_and_alerts(config):
    """Enhanced monitoring setup with comprehensive alerting"""
    try:
        credential = DefaultAzureCredential()
        monitor_client = MonitorManagementClient(credential, config['subscription_id'])
        
        # Create action group for alerts
        action_group = {
            'location': 'global',
            'group_short_name': 'NodeAlerts',
            'enabled': True,
            'email_receivers': [{
                'name': 'AdminAlert',
                'email_address': config.get('alert_email'),
                'use_common_alert_schema': True
            }] if config.get('alert_email') else [],
            'webhook_receivers': [{
                'name': 'WebhookAlert',
                'service_uri': config.get('webhook_url')
            }] if config.get('webhook_url') else []
        }
        
        monitor_client.action_groups.create_or_update(
            config['resource_group'],
            'NodeActionGroup',
            action_group
        )
        
        # Set up metric alerts
        metrics = {
            'CPU': {'threshold': 80, 'window': 'PT5M', 'frequency': 'PT1M'},
            'Memory': {'threshold': 85, 'window': 'PT5M', 'frequency': 'PT1M'},
            'Disk': {'threshold': 90, 'window': 'PT15M', 'frequency': 'PT5M'},
            'NetworkIn': {'threshold': 95, 'window': 'PT15M', 'frequency': 'PT5M'},
            'NetworkOut': {'threshold': 95, 'window': 'PT15M', 'frequency': 'PT5M'}
        }
        
        for metric, settings in metrics.items():
            alert_rule = {
                'location': config['location'],
                'description': f'{metric} usage alert',
                'severity': 2,
                'enabled': True,
                'scopes': [f"/subscriptions/{config['subscription_id']}/resourceGroups/{config['resource_group']}/providers/Microsoft.Compute/virtualMachines/{config['vm_name']}"],
                'evaluation_frequency': settings['frequency'],
                'window_size': settings['window'],
                'criteria': {
                    'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria',
                    'all_of': [{
                        'criterion_type': 'StaticThresholdCriterion',
                        'metric_name': metric,
                        'metric_namespace': 'Microsoft.Compute/virtualMachines',
                        'operator': 'GreaterThan',
                        'threshold': settings['threshold'],
                        'time_aggregation': 'Average'
                    }]
                },
                'actions': [{
                    'action_group_id': f"/subscriptions/{config['subscription_id']}/resourceGroups/{config['resource_group']}/providers/Microsoft.Insights/actionGroups/NodeActionGroup"
                }]
            }
            
            monitor_client.metric_alerts.create_or_update(
                config['resource_group'],
                f'{metric.lower()}-alert',
                alert_rule
            )
        
        # Set up diagnostic settings
        diagnostic_settings = {
            'logs': [{
                'category': 'Administrative',
                'enabled': True,
                'retention_policy': {
                    'enabled': True,
                    'days': config.get('retention_days', 30)
                }
            }],
            'metrics': [{
                'category': 'AllMetrics',
                'enabled': True,
                'retention_policy': {
                    'enabled': True,
                    'days': config.get('retention_days', 30)
                }
            }]
        }
        
        monitor_client.diagnostic_settings.create_or_update(
            resource_uri=f"/subscriptions/{config['subscription_id']}/resourceGroups/{config['resource_group']}/providers/Microsoft.Compute/virtualMachines/{config['vm_name']}",
            name='NodeDiagnostics',
            parameters=diagnostic_settings
        )
        
        return {'result': 'Monitoring and alerts configured successfully'}
        
    except AzureError as e:
        logger.error(f"Azure monitoring setup error: {str(e)}")
        return {'error': f"Monitoring setup failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in monitoring setup: {str(e)}")
        return {'error': f"Unexpected error: {str(e)}"}

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
