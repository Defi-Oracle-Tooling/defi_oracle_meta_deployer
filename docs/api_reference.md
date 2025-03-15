{
  "name": "CustomResourceGroup",
  "location": "westus",
  "resource_group": "CustomResourceGroup",
  "vm_name": "CustomVM",
  "image": "UbuntuLTS",
  "admin_username": "customuser",
  "vm_size": "Standard_DS1_v2",
  "network": {
    "vnet": "CustomVNet",
    "subnet": "CustomSubnet",
    "address_prefix": "10.1.0.0/16",
    "subnet_prefix": "10.1.0.0/24"
  },
  "security": {
    "nsg": "CustomNSG",
    "firewall_rules": [
      {
        "port": 8545,
        "protocol": "TCP",
        "access": "allow"
      }
    ]
  },
  "deployment": {
    "mode": "Incremental",
    "template_uri": "https://path-to-your-template/template.json",
    "parameters": {
      "vmName": "CustomVM",
      "adminUsername": "customuser",
      "adminPassword": "YourSecurePassword"
    }
  },
  "node_configuration": {
    "besu_config_file": "besu.conf",
    "node_type": "validator",
    "network_type": "permissioned"
  },
  "monitoring": {
    "enabled": true,
    "monitoring_tool": "Azure Monitor",
    "alert_rules": [
      {
        "metric": "CPU",
        "threshold": "80%",
        "action": "notify"
      }
    ]
  }
}

{
  "name": "ExpertResourceGroup",
  "location": "eastus",
  "resource_group": "ExpertResourceGroup",
  "vm_name": "ExpertVM",
  "image": "UbuntuLTS",
  "admin_username": "expertuser",
  "vm_size": "Standard_DS2_v2",
  "network": {
    "vnet": "ExpertVNet",
    "subnet": "ExpertSubnet",
    "address_prefix": "10.2.0.0/16",
    "subnet_prefix": "10.2.0.0/24"
  },
  "security": {
    "nsg": "ExpertNSG",
    "firewall_rules": [
      {
        "port": 8545,
        "protocol": "TCP",
        "access": "allow"
      },
      {
        "port": 30303,
        "protocol": "TCP",
        "access": "allow"
      }
    ]
  },
  "deployment": {
    "mode": "BlueGreen",
    "template_uri": "https://path-to-your-template/expert_template.json",
    "parameters": {
      "vmName": "ExpertVM",
      "adminUsername": "expertuser",
      "adminPassword": "ExpertSecurePassword"
    }
  },
  "node_configuration": {
    "besu_config_file": "besu_expert.conf",
    "node_type": "validator",
    "network_type": "consortium",
    "additional_nodes": [
      {
        "role": "bootnode",
        "config": "bootnode.conf"
      },
      {
        "role": "observer",
        "config": "observer.conf"
      }
    ]
  },
  "monitoring": {
    "enabled": true,
    "monitoring_tool": "Azure Monitor",
    "alert_rules": [
      {
        "metric": "CPU",
        "threshold": "75%",
        "action": "email"
      },
      {
        "metric": "Memory",
        "threshold": "80%",
        "action": "sms"
      }
    ]
  }
}

{
  "name": "AdvancedResourceGroup",
  "location": "centralus",
  "resource_group": "AdvancedResourceGroup",
  "vm_name": "AdvancedVM",
  "image": "UbuntuLTS",
  "admin_username": "advanceduser",
  "vm_size": "Standard_DS3_v2",
  "network": {
    "vnet": "AdvancedVNet",
    "subnet": "AdvancedSubnet",
    "address_prefix": "10.3.0.0/16",
    "subnet_prefix": "10.3.0.0/24"
  },
  "security": {
    "nsg": "AdvancedNSG",
    "firewall_rules": [
      {
        "port": 8545,
        "protocol": "TCP",
        "access": "allow"
      },
      {
        "port": 30303,
        "protocol": "TCP",
        "access": "allow"
      },
      {
        "port": 30303,
        "protocol": "UDP",
        "access": "allow"
      }
    ]
  },
  "deployment": {
    "mode": "Canary",
    "template_uri": "https://path-to-your-template/advanced_template.json",
    "parameters": {
      "vmName": "AdvancedVM",
      "adminUsername": "advanceduser",
      "adminPassword": "AdvancedSecurePassword"
    }
  },
  "node_configuration": {
    "besu_config_file": "besu_advanced.conf",
    "node_type": "validator",
    "network_type": "public",
    "additional_nodes": [
      {
        "role": "bootnode",
        "config": "bootnode.conf"
      },
      {
        "role": "observer",
        "config": "observer.conf"
      },
      {
        "role": "archiver",
        "config": "archiver.conf"
      }
    ]
  },
  "monitoring": {
    "enabled": true,
    "monitoring_tool": "Azure Monitor",
    "alert_rules": [
      {
        "metric": "CPU",
        "threshold": "70%",
        "action": "notify"
      },
      {
        "metric": "Disk",
        "threshold": "90%",
        "action": "email"
      }
    ]
  }
}

{
  "name": "HybridResourceGroup",
  "location": "northcentralus",
  "resource_group": "HybridResourceGroup",
  "vm_name": "HybridVM",
  "image": "UbuntuLTS",
  "admin_username": "hybriduser",
  "vm_size": "Standard_DS2_v2",
  "network": {
    "vnet": "HybridVNet",
    "subnet": "HybridSubnet",
    "address_prefix": "10.4.0.0/16",
    "subnet_prefix": "10.4.0.0/24"
  },
  "security": {
    "nsg": "HybridNSG",
    "firewall_rules": [
      {
        "port": 8545,
        "protocol": "TCP",
        "access": "allow"
      }
    ]
  },
  "deployment": {
    "mode": "Incremental",
    "template_uri": "https://path-to-your-template/hybrid_template.json",
    "parameters": {
      "vmName": "HybridVM",
      "adminUsername": "hybriduser",
      "adminPassword": "HybridSecurePassword"
    }
  },
  "node_configuration": {
    "besu_config_file": "besu_hybrid.conf",
    "node_type": "validator",
    "network_type": "permissioned",
    "additional_nodes": [
      {
        "role": "bootnode",
        "config": "bootnode.conf"
      }
    ]
  },
  "monitoring": {
    "enabled": true,
    "monitoring_tool": "Azure Monitor",
    "alert_rules": [
      {
        "metric": "CPU",
        "threshold": "80%",
        "action": "notify"
      }
    ]
  }
}

# API Reference

## Endpoints

### `GET /`
- Description: Renders the index page.
- Response: HTML page.

### `POST /execute`
- Description: Executes the selected action with the provided configuration.
- Request Body: `application/x-www-form-urlencoded`
  - `action`: The action to execute (e.g., `create_rg`, `deploy_vm`, `rest_deploy`).
  - `config`: The configuration JSON.
- Response: HTML page with the result of the action.

### `POST /validate_config`
- Description: Validates the provided configuration JSON.
- Request Body: `application/json`
  - `config`: The configuration JSON.
- Response: `application/json`
  - `valid`: Boolean indicating whether the configuration is valid.
  - `error`: Error message if the configuration is invalid.

### `POST /predict`
- Description: Provides a prediction based on the provided configuration JSON.
- Request Body: `application/json`
  - `config`: The configuration JSON.
- Response: `application/json`
  - `prediction`: The prediction result.
  - `error`: Error message if the prediction fails.

### `GET /login`
- Description: Renders the login page.
- Response: HTML page.

### `POST /login`
- Description: Authenticates the user.
- Request Body: `application/x-www-form-urlencoded`
  - `username`: The username.
  - `password`: The password.
- Response: Redirects to the index page if successful, otherwise returns an error message.

### `GET /logout`
- Description: Logs out the user.
- Response: Redirects to the login page.

### `GET /protected`
- Description: Renders a protected page that requires authentication.
- Response: HTML page with the current user's ID.

### `POST /create_resource_group`
- Description: Creates a new resource group with the provided configuration.
- Request Body: `application/json`
  - `name`: The name of the resource group.
  - `location`: The location of the resource group.
- Response: `application/json`
  - `result`: Success message or error message.

### `POST /deploy_vm`
- Description: Deploys a virtual machine with the provided configuration.
- Request Body: `application/json`
  - `resource_group`: The resource group to deploy the VM in.
  - `vm_name`: The name of the VM.
  - `image`: The image to use for the VM.
  - `admin_username`: The admin username for the VM.
- Response: `application/json`
  - `result`: Success message or error message.

### `POST /create_network`
- Description: Creates a virtual network with the provided configuration.
- Request Body: `application/json`
  - `resource_group`: The resource group to create the network in.
  - `name`: The name of the network.
  - `location`: The location of the network.
  - `address_prefix`: The address prefix for the network.
- Response: `application/json`
  - `result`: Success message or error message.

### `POST /create_storage_account`
- Description: Creates a storage account with the provided configuration.
- Request Body: `application/json`
  - `resource_group`: The resource group to create the storage account in.
  - `name`: The name of the storage account.
  - `sku`: The SKU of the storage account.
  - `kind`: The kind of the storage account.
  - `location`: The location of the storage account.
- Response: `application/json`
  - `result`: Success message or error message.

### `POST /setup_monitoring`
- Description: Sets up monitoring and alerts for the provided resource group and VM.
- Request Body: `application/json`
  - `resource_group`: The resource group to set up monitoring for.
  - `vm_name`: The name of the VM to set up monitoring for.
- Response: `application/json`
  - `result`: Success message or error message.

### `POST /predict_optimal_config`
- Description: Provides a prediction for the optimal configuration based on the provided features.
- Request Body: `application/json`
  - `vm_name`: The name of the VM.
  - `admin_username`: The admin username for the VM.
  - `resource_group`: The resource group.
  - `location`: The location.
  - `image`: The image to use for the VM.
- Response: `application/json`
  - `prediction`: The prediction result.
  - `error`: Error message if the prediction fails.