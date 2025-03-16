# DeFi Oracle Meta Deployer Guide

## Overview

The DeFi Oracle Meta Deployer provides two deployment modes:
- Simple Mode: Quick deployment with pre-configured settings
- Expert Mode: Advanced deployment with full customization options

## Simple Mode Deployment

### Prerequisites
- Azure account with active subscription
- Network access to Azure regions
- Valid authentication credentials

### Steps

1. **Resource Group Selection**
   - Enter a unique resource group name (3-64 characters)
   - Select target Azure region
   - Validation occurs in real-time

2. **Node Configuration**
   - Choose node type (validator/observer/bootnode)
   - Select VM size based on requirements
   - Basic configuration is automatically applied

3. **Deployment**
   - Review configuration
   - Click "Deploy Oracle Node"
   - Monitor deployment progress

### Example Configuration
```json
{
    "mode": "simple",
    "resourceGroup": "my-oracle-rg",
    "location": "eastus",
    "nodeType": "validator",
    "vmSize": "Standard_D2s_v3"
}
```

## Expert Mode Deployment

### Prerequisites
- Advanced understanding of blockchain networks
- Knowledge of consensus protocols
- Network architecture planning

### Steps

1. **Network Configuration**
   - Configure virtual network settings
   - Define subnet ranges
   - Set up network security rules

2. **Node Configuration**
   - Specify number of nodes
   - Select consensus protocol
   - Configure node roles and relationships

3. **Monitoring Setup**
   - Enable/disable monitoring
   - Configure retention period
   - Set up alert notifications

4. **Deployment**
   - Validate complete configuration
   - Deploy network infrastructure
   - Deploy and configure nodes
   - Set up monitoring if enabled

### Example Configuration
```json
{
    "mode": "expert",
    "network": {
        "vnetName": "oracle-network",
        "subnetPrefix": "10.0.0.0/24"
    },
    "nodes": {
        "count": 3,
        "consensusProtocol": "ibft2"
    },
    "monitoring": {
        "enabled": true,
        "retention": 30,
        "alertEmail": "admin@example.com"
    }
}
```

## Validation Rules

### Simple Mode
- Resource group name: 3-64 characters, alphanumeric, dashes, underscores
- Location: Must be valid Azure region
- Node type: validator, observer, or bootnode
- VM size: From approved list (Standard_D2s_v3, Standard_D4s_v3, Standard_D8s_v3)

### Expert Mode
- Network:
  - VNet name: 2-64 characters, alphanumeric, dashes, underscores
  - Subnet prefix: Valid CIDR notation
- Nodes:
  - Count: 1-10 nodes
  - Protocol: ibft2, qbft, or clique
- Monitoring (if enabled):
  - Retention: 1-90 days
  - Alert email: Valid email format

## Troubleshooting

### Common Issues

1. **Resource Group Creation Fails**
   - Check name uniqueness
   - Verify Azure region availability
   - Confirm subscription permissions

2. **Node Deployment Issues**
   - Verify network configuration
   - Check resource quotas
   - Validate consensus settings

3. **Monitoring Setup Problems**
   - Confirm email format
   - Check retention period limits
   - Verify alert configurations

### Support

For additional assistance:
- Check documentation
- Use interactive API tester
- Contact support team