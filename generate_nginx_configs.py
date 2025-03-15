#!/usr/bin/env python3

import os
import json
import argparse
from collections import defaultdict

def parse_docker_ps_output(file_path):
    """Parse docker ps output file to extract container information"""
    nodes = []
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Skip the header line
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) < 2:
            continue
            
        container_id = parts[0]
        image = parts[1]
        
        # Extract ports - this is simplified and might need adjustment
        ports_section = ' '.join(parts)
        ports = []
        
        # Extract name (last column)
        name = parts[-1]
        
        # Identify node type and extract ports
        node_type = None
        node_name = None
        node_port = None
        
        if "validator" in name:
            node_type = "validator"
            node_name = name.split('-')[-1]
            
            # Find port mapping like "0.0.0.0:21001->8545/tcp"
            port_mappings = [p for p in ports_section.split() if "->8545/tcp" in p]
            if port_mappings:
                port_mapping = port_mappings[0]
                node_port = port_mapping.split(':')[1].split('->')[0]
        
        elif "member" in name and "besu" in name:
            node_type = "member"
            node_name = name.split('-')[-1]
            
            # Find port mapping like "0.0.0.0:20000->8545/tcp"
            port_mappings = [p for p in ports_section.split() if "->8545/tcp" in p]
            if port_mappings:
                port_mapping = port_mappings[0]
                node_port = port_mapping.split(':')[1].split('->')[0]
        
        elif name == "rpcnode":
            node_type = "rpc"
            node_name = "rpcnode"
            
            # For RPC node, look for "0.0.0.0:8545-8546->8545-8546/tcp"
            port_mappings = [p for p in ports_section.split() if "8545" in p]
            if port_mappings:
                port_mapping = port_mappings[0]
                node_port = "8545"  # RPC node typically exposes 8545
        
        if node_type and node_name and node_port:
            nodes.append({
                "type": node_type,
                "name": node_name,
                "port": node_port,
                "container_name": name
            })
            
    return nodes

def generate_nginx_config(node, domain="deployer.defi-oracle.io", output_dir="nginx_configs"):
    """Generate nginx config file for a node"""
    node_subdomain = f"{node['type']}-{node['name']}"
    server_name = f"{node_subdomain}.{domain}"
    
    config = f"""worker_processes 1;

events {{
    worker_connections 1024;
}}

http {{
    include       mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    keepalive_timeout  65;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    server {{
        listen 80;
        server_name {server_name};

        location / {{
            proxy_pass http://localhost:{node['port']};
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}

        # JSON-RPC specific settings
        location /json-rpc {{
            proxy_pass http://localhost:{node['port']};
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Set headers for CORS
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type';
            
            # Handle OPTIONS requests
            if ($request_method = 'OPTIONS') {{
                add_header 'Access-Control-Allow-Origin' '*';
                add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
                add_header 'Access-Control-Allow-Headers' 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type';
                add_header 'Access-Control-Max-Age' 1728000;
                add_header 'Content-Type' 'text/plain charset=UTF-8';
                add_header 'Content-Length' 0;
                return 204;
            }}
        }}

        # Add security headers
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; frame-ancestors 'none';";
        add_header Referrer-Policy "no-referrer-when-downgrade";
        add_header Permissions-Policy "geolocation=(), microphone=(), camera=()";
    }}
}}
"""
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Write config to file
    with open(f"{output_dir}/nginx_{node_subdomain}.conf", "w") as f:
        f.write(config)
    
    return {
        "subdomain": node_subdomain,
        "domain": domain,
        "server_name": server_name,
        "port": node['port']
    }

def generate_cloudflare_dns_config(node_configs, domain="deployer.defi-oracle.io", server_ip="SERVER_IP_ADDRESS"):
    """Generate Cloudflare DNS configuration JSON"""
    dns_records = []
    
    for node_config in node_configs:
        dns_records.append({
            "type": "A",
            "name": node_config["subdomain"],
            "content": server_ip,
            "ttl": 120,
            "proxied": True
        })
    
    return dns_records

def main():
    parser = argparse.ArgumentParser(description='Generate nginx configurations for Besu nodes')
    parser.add_argument('--docker-ps-file', default='docker_ps_output.txt', 
                        help='Path to docker ps output file')
    parser.add_argument('--domain', default='deployer.defi-oracle.io',
                        help='Base domain name')
    parser.add_argument('--server-ip', default='127.0.0.1',
                        help='Server IP address')
    parser.add_argument('--output-dir', default='nginx_configs',
                        help='Output directory for nginx configuration files')
    
    args = parser.parse_args()
    
    # Parse docker ps output to extract node information
    nodes = parse_docker_ps_output(args.docker_ps_file)
    
    # Generate nginx configuration for each node
    node_configs = []
    for node in nodes:
        node_config = generate_nginx_config(node, domain=args.domain, output_dir=args.output_dir)
        node_configs.append(node_config)
    
    print(f"Generated {len(node_configs)} nginx configuration files in '{args.output_dir}' directory")
    
    # Generate Cloudflare DNS configuration
    dns_records = generate_cloudflare_dns_config(node_configs, domain=args.domain, server_ip=args.server_ip)
    
    # Write Cloudflare DNS configuration to file
    with open(f"{args.output_dir}/cloudflare_dns_records.json", "w") as f:
        json.dump(dns_records, f, indent=2)
    
    print(f"Generated Cloudflare DNS configuration in '{args.output_dir}/cloudflare_dns_records.json'")

if __name__ == "__main__":
    main()