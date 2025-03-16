import re
import html
import json
from typing import Dict, Any, Tuple, Optional, List
import ipaddress

class InputValidationError(Exception):
    pass

def sanitize_input(value: str) -> str:
    """Sanitize input string to prevent XSS and injection attacks"""
    # HTML encode special characters
    sanitized = html.escape(value)
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[;&<>`\'"]', '', sanitized)
    return sanitized

def validate_ip_address(ip: str) -> bool:
    """Validate IP address format"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def validate_port_range(port: int) -> bool:
    """Validate port number is within valid range"""
    return 1 <= port <= 65535

def validate_resource_name(name: str) -> Tuple[bool, Optional[str]]:
    """Validate Azure resource name"""
    if not re.match(r'^[a-zA-Z0-9-_]{3,64}$', name):
        return False, "Resource name must be 3-64 characters and contain only letters, numbers, hyphens, and underscores"
    return True, None

def validate_location(location: str, valid_locations: List[str]) -> Tuple[bool, Optional[str]]:
    """Validate Azure location"""
    if location not in valid_locations:
        return False, f"Invalid location. Must be one of: {', '.join(valid_locations)}"
    return True, None

def validate_subnet_prefix(prefix: str) -> Tuple[bool, Optional[str]]:
    """Validate subnet prefix format and range"""
    if not re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}\/[0-9]{1,2}$', prefix):
        return False, "Invalid subnet prefix format (e.g., 10.0.0.0/24)"
    
    try:
        network = ipaddress.ip_network(prefix)
        prefix_length = int(prefix.split('/')[-1])
        if not 16 <= prefix_length <= 29:
            return False, "Subnet prefix must be between /16 and /29"
        return True, None
    except ValueError as e:
        return False, str(e)

def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Validate email address format"""
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return False, "Invalid email address format"
    return True, None

def validate_monitoring_config(config: Dict[str, Any]) -> List[str]:
    """Validate monitoring configuration"""
    errors = []
    
    if config.get('enabled'):
        try:
            retention = int(config.get('retention', 0))
            if not 1 <= retention <= 90:
                errors.append("Retention period must be between 1 and 90 days")
        except ValueError:
            errors.append("Invalid retention period value")

        if config.get('alertEmail'):
            valid, error = validate_email(config['alertEmail'])
            if not valid:
                errors.append(error)
                
    return errors

def validate_firewall_rules(rules: List[Dict[str, Any]]) -> List[str]:
    """Validate firewall rules configuration"""
    errors = []
    
    for rule in rules:
        try:
            port = int(rule.get('port', -1))
            if not validate_port_range(port):
                errors.append(f"Invalid port number: {port}. Must be between 1 and 65535")
        except ValueError:
            errors.append(f"Invalid port value: {rule.get('port')}")

        if rule.get('protocol', '').upper() not in ['TCP', 'UDP']:
            errors.append(f"Invalid protocol: {rule.get('protocol')}. Must be TCP or UDP")
            
        if 'sourceAddress' in rule:
            if not validate_ip_address(rule['sourceAddress']):
                errors.append(f"Invalid source IP address: {rule['sourceAddress']}")
                
    return errors

def sanitize_json_input(json_str: str) -> Tuple[Dict[str, Any], Optional[str]]:
    """Sanitize and validate JSON input"""
    try:
        # First try to parse JSON
        data = json.loads(json_str)
        
        # Recursively sanitize strings in the parsed data
        def sanitize_dict(d):
            if isinstance(d, dict):
                return {k: sanitize_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [sanitize_dict(v) for v in d]
            elif isinstance(d, str):
                return sanitize_input(d)
            else:
                return d
                
        return sanitize_dict(data), None
    except json.JSONDecodeError as e:
        return {}, f"Invalid JSON format: {str(e)}"
    except Exception as e:
        return {}, f"Validation error: {str(e)}"