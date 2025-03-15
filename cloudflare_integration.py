#!/usr/bin/env python3

import os
import json
import argparse
import requests
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_cloudflare_credentials():
    """Get Cloudflare credentials from environment variables"""
    api_key = os.getenv('CF_API_KEY')
    email = os.getenv('CF_EMAIL')
    zone_id = os.getenv('CF_ZONE_ID')
    
    # Check if credentials are available
    if not all([api_key, email, zone_id]):
        raise ValueError(
            "Missing Cloudflare credentials. Please set CF_API_KEY, CF_EMAIL, and CF_ZONE_ID "
            "environment variables in your .env file."
        )
    
    return api_key, email, zone_id

def create_dns_record(api_key, email, zone_id, record):
    """Create a DNS record in Cloudflare"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "X-Auth-Email": email,
        "X-Auth-Key": api_key,
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json=record)
    
    if response.status_code == 200 and response.json()["success"]:
        print(f"Successfully created DNS record for {record['name']}")
        return response.json()["result"]
    else:
        print(f"Failed to create DNS record for {record['name']}")
        print(f"Response: {response.json()}")
        return None

def update_dns_record(api_key, email, zone_id, record_id, record):
    """Update a DNS record in Cloudflare"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {
        "X-Auth-Email": email,
        "X-Auth-Key": api_key,
        "Content-Type": "application/json"
    }
    
    response = requests.put(url, headers=headers, json=record)
    
    if response.status_code == 200 and response.json()["success"]:
        print(f"Successfully updated DNS record for {record['name']}")
        return response.json()["result"]
    else:
        print(f"Failed to update DNS record for {record['name']}")
        print(f"Response: {response.json()}")
        return None

def get_dns_records(api_key, email, zone_id, name=None):
    """Get DNS records from Cloudflare"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "X-Auth-Email": email,
        "X-Auth-Key": api_key,
        "Content-Type": "application/json"
    }
    
    params = {}
    if name:
        params["name"] = name
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200 and response.json()["success"]:
        return response.json()["result"]
    else:
        print("Failed to get DNS records")
        print(f"Response: {response.json()}")
        return []

def purge_cache(api_key, email, zone_id, urls=None):
    """Purge Cloudflare cache for specific URLs or everything"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache"
    headers = {
        "X-Auth-Email": email,
        "X-Auth-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # If URLs are specified, purge cache for those URLs.
    # Otherwise, purge everything
    if urls:
        data = {"files": urls}
    else:
        data = {"purge_everything": True}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200 and response.json()["success"]:
        print("Successfully purged cache")
        return True
    else:
        print("Failed to purge cache")
        print(f"Response: {response.json()}")
        return False

def setup_page_rules(api_key, email, zone_id, node_configs):
    """Set up page rules for caching and security"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/pagerules"
    headers = {
        "X-Auth-Email": email,
        "X-Auth-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Create page rules for each node
    for node_config in node_configs:
        server_name = node_config["server_name"]
        
        # Create a rule to bypass cache for JSON-RPC endpoints
        rule1 = {
            "targets": [
                {
                    "target": "url",
                    "constraint": {
                        "operator": "matches",
                        "value": f"*{server_name}/json-rpc*"
                    }
                }
            ],
            "actions": [
                {
                    "id": "cache_level",
                    "value": "bypass"
                }
            ],
            "priority": 1,
            "status": "active"
        }
        
        # Create a rule to set security level to high for all other requests
        rule2 = {
            "targets": [
                {
                    "target": "url",
                    "constraint": {
                        "operator": "matches",
                        "value": f"*{server_name}/*"
                    }
                }
            ],
            "actions": [
                {
                    "id": "security_level",
                    "value": "high"
                }
            ],
            "priority": 2,
            "status": "active"
        }
        
        # Send request to create rules
        for rule in [rule1, rule2]:
            response = requests.post(url, headers=headers, json=rule)
            if response.status_code == 200 and response.json()["success"]:
                print(f"Successfully created page rule for {server_name}")
            else:
                print(f"Failed to create page rule for {server_name}")
                print(f"Response: {response.json()}")

def setup_firewall_rules(api_key, email, zone_id):
    """Set up firewall rules to protect against common attacks"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/firewall/rules"
    headers = {
        "X-Auth-Email": email,
        "X-Auth-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Create some basic firewall rules
    rules = [
        {
            "filter": {
                "expression": "(http.request.method eq \"POST\") and (http.request.uri.path contains \"/json-rpc\")",
                "paused": False
            },
            "action": "allow",
            "description": "Allow JSON-RPC POST requests",
            "paused": False
        },
        {
            "filter": {
                "expression": "(http.request.uri.path contains \"/json-rpc\") and (not http.request.method in {\"POST\", \"OPTIONS\"})",
                "paused": False
            },
            "action": "block",
            "description": "Block non-POST/OPTIONS requests to JSON-RPC",
            "paused": False
        },
        {
            "filter": {
                "expression": "(http.request.uri.path contains \"/json-rpc\") and (not ip.geoip.country in {\"US\", \"CA\", \"GB\"})",
                "paused": True  # Disabled by default - enable if you want geo-restrictions
            },
            "action": "block",
            "description": "Block JSON-RPC requests from outside allowed countries",
            "paused": True
        }
    ]
    
    # Send request to create rules
    for rule in rules:
        response = requests.post(url, headers=headers, json=rule)
        if response.status_code == 200 and response.json()["success"]:
            print(f"Successfully created firewall rule: {rule['description']}")
        else:
            print(f"Failed to create firewall rule: {rule['description']}")
            print(f"Response: {response.json()}")

def deploy_dns_records(api_key, email, zone_id, dns_records):
    """Deploy DNS records to Cloudflare"""
    for record in dns_records:
        # Check if record already exists
        existing_records = get_dns_records(api_key, email, zone_id, f"{record['name']}.{record['zone_name']}")
        
        if existing_records:
            # Update existing record
            record_id = existing_records[0]["id"]
            update_dns_record(api_key, email, zone_id, record_id, record)
        else:
            # Create new record
            create_dns_record(api_key, email, zone_id, record)

def main():
    parser = argparse.ArgumentParser(description='Deploy Cloudflare DNS records and configure CDN')
    parser.add_argument('--dns-records-file', required=True, 
                        help='Path to JSON file containing DNS records')
    parser.add_argument('--zone-name', default='deployer.defi-oracle.io',
                        help='Zone name (domain)')
    parser.add_argument('--setup-page-rules', action='store_true', 
                        help='Set up page rules for caching and security')
    parser.add_argument('--setup-firewall', action='store_true',
                        help='Set up firewall rules')
    parser.add_argument('--purge-cache', action='store_true',
                        help='Purge cache after deployment')
    
    args = parser.parse_args()
    
    try:
        # Get Cloudflare credentials
        api_key, email, zone_id = get_cloudflare_credentials()
        
        # Load DNS records from file
        with open(args.dns_records_file, 'r') as f:
            dns_records = json.load(f)
        
        # Add zone name to records
        for record in dns_records:
            record['zone_name'] = args.zone_name
        
        # Deploy DNS records
        deploy_dns_records(api_key, email, zone_id, dns_records)
        
        # Set up page rules if requested
        if args.setup_page_rules:
            # Extract node configurations from DNS records
            node_configs = [
                {
                    "server_name": f"{record['name']}.{args.zone_name}"
                }
                for record in dns_records
            ]
            setup_page_rules(api_key, email, zone_id, node_configs)
        
        # Set up firewall rules if requested
        if args.setup_firewall:
            setup_firewall_rules(api_key, email, zone_id)
        
        # Purge cache if requested
        if args.purge_cache:
            purge_cache(api_key, email, zone_id)
        
        print("Deployment completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())