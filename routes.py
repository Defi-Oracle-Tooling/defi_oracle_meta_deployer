import os
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, current_app as app, abort
from flask_login import login_required, current_user
import time
import traceback
import re
from azure_operations import create_resource_group, deploy_vm, deploy_via_rest_api, create_network, create_storage_account, setup_monitoring_and_alerts, initialize_azure_integration
from ml_model import model, predict_optimal_config
import pyotp
from markdown_helper import MarkdownConverter
from auth import requires_roles, rate_limit, token_required
import logging
from datetime import datetime

routes_bp = Blueprint('routes', __name__)
markdown_converter = MarkdownConverter()
logger = logging.getLogger(__name__)

class ValidationError(Exception):
    pass

def validate_resource_name(name):
    if not re.match(r'^[a-zA-Z0-9-_]{3,64}$', name):
        raise ValidationError('Resource name must be 3-64 characters long and contain only letters, numbers, hyphens, and underscores')

def validate_location(location):
    valid_locations = ['eastus', 'westus', 'northeurope', 'westeurope']
    if location not in valid_locations:
        raise ValidationError(f'Invalid location. Must be one of: {", ".join(valid_locations)}')

@routes_bp.route('/', methods=['GET'])
def index():
    app.logger.info('Index page accessed')
    regions = [
        {"value": "eastus", "name": "East US"},
        {"value": "westus", "name": "West US"},
        {"value": "centralus", "name": "Central US"},
        {"value": "northcentralus", "name": "North Central US"},
        {"value": "southcentralus", "name": "South Central US"}
    ]
    return render_template('index.html', regions=regions)

@routes_bp.route('/about')
def about():
    return render_template('about.html')

@routes_bp.route('/docs')
def docs():
    return render_template('docs.html')

@routes_bp.route('/contact')
def contact():
    return render_template('contact.html')

@routes_bp.route('/deploy')
def deploy():
    return render_template('deploy.html')

@routes_bp.route('/terms')
def terms():
    return render_template('terms.html')

@routes_bp.route('/execute', methods=['POST'])
@login_required
def execute_action():
    try:
        action = request.form.get('action')
        config = request.form.get('config')
        if not config:
            config = load_default_config(action)
        app.logger.info(f'Action: {action} executed with config: {config}')
        emit_status('processing', f'Starting {action}...')
        result = handle_decision_point(action, config)
        if 'error' in result.lower():
            emit_status('error', result)
        else:
            emit_status('success', result)
        return jsonify({'result': result})
    except Exception as e:
        app.logger.error(f'Error in execute_action: {str(e)}\n{traceback.format_exc()}')
        emit_status('error', str(e))
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/validate_config', methods=['POST'])
@login_required
def validate_config():
    config = request.json
    app.logger.info(f'Config validation requested: {config}')
    config_data, error = validate_config_data(config)
    if error:
        app.logger.error(f'Config validation error: {error}')
        return jsonify({'valid': False, 'error': error})
    return jsonify({'valid': True})

@routes_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    message = request.json.get('message')
    app.logger.info(f'Chat message received: {message}')
    response = 'This is a placeholder response from the LLM.'
    return jsonify({'response': response})

@routes_bp.route('/predict', methods=['POST'])
@login_required
def predict():
    config = request.form.get('config')
    app.logger.info(f'Prediction requested for config: {config}')
    config_data, error = validate_config(config)
    if error:
        app.logger.error(f'Prediction error: {error}')
        return jsonify({'error': error})
    features = [
        config_data.get('vm_name', ''),
        config_data.get('admin_username', ''),
        config_data.get('resource_group', ''),
        config_data.get('location', ''),
        config_data.get('image', '')
    ]
    prediction = model.predict([features])
    app.logger.info(f'Prediction result: {prediction[0]}')
    return jsonify({'prediction': prediction[0]})

@routes_bp.route('/create_network', methods=['POST'])
@login_required
def create_network_route():
    config = request.json
    app.logger.info(f'Network creation requested: {config}')
    result = create_network(config)
    return jsonify({'result': result})

@routes_bp.route('/create_storage_account', methods=['POST'])
@login_required
def create_storage_account_route():
    config = request.json
    app.logger.info(f'Storage account creation requested: {config}')
    result = create_storage_account(config)
    return jsonify({'result': result})

@routes_bp.route('/create_resource_group', methods=['POST'])
@login_required
def create_resource_group_route():
    config = request.json
    app.logger.info(f'Resource group creation requested: {config}')
    try:
        resource_group_params = {'location': config['location']}
        resource_client.resource_groups.create_or_update(config['name'], resource_group_params)
        return jsonify({'result': 'Resource group created successfully'})
    except Exception as e:
        app.logger.error(f'Error creating resource group: {str(e)}')
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/deploy_vm', methods=['POST'])
@login_required
def deploy_vm_route():
    config = request.json
    app.logger.info(f'VM deployment requested: {config}')
    try:
        return jsonify({'result': 'VM deployed successfully'})
    except Exception as e:
        app.logger.error(f'Error deploying VM: {str(e)}')
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/setup_monitoring', methods=['POST'])
@login_required
def setup_monitoring_route():
    config = request.json
    app.logger.info(f'Monitoring setup requested: {config}')
    result = setup_monitoring_and_alerts(config['resource_group'], config['vm_name'])
    return jsonify({'result': result})

@routes_bp.route('/predict_optimal_config', methods=['POST'])
@login_required
def predict_optimal_config_route():
    config = request.json
    app.logger.info(f'Optimal config prediction requested: {config}')
    features = [
        config.get('vm_name', ''),
        config.get('admin_username', ''),
        config.get('resource_group', ''),
        config.get('location', ''),
        config.get('image', '')
    ]
    prediction = predict_optimal_config(features)
    if prediction:
        return jsonify({'prediction': prediction})
    else:
        return jsonify({'error': 'Prediction failed'}), 500

@routes_bp.route('/docs/introduction')
def docs_introduction():
    return render_template('docs/introduction.md')

@routes_bp.route('/docs/setup')
def docs_setup():
    return render_template('docs/setup.md')

@routes_bp.route('/docs/usage')
def docs_usage():
    return render_template('docs/usage.md')

@routes_bp.route('/docs/api_reference')
def docs_api_reference():
    return render_template('docs/api_reference.md')

@routes_bp.route('/deployer', methods=['GET'])
def deployer_landing():
    realtime_data = get_realtime_data()
    return render_template('deployer-landing.html', realtimeData=realtime_data)

@routes_bp.route('/2fa', methods=['POST'])
def two_factor_auth():
    code = request.form.get('code')
    if not code:
        return jsonify({'error': 'No 2FA code provided'}), 400
    if validate_2fa_code(code):
        session['authenticated'] = True
        return jsonify({'message': 'Authentication successful'}), 200
    return jsonify({'error': 'Authentication failed'}), 401

@routes_bp.route('/deploy', methods=['GET'])
def deployer_interface():
    if not session.get('authenticated'):
        return redirect(url_for('routes.deployer_landing'))
    initialize_azure_integration()
    return render_template('deployer-full.html')

@routes_bp.route('/api/deploy', methods=['POST'])
@login_required
@requires_roles('admin', 'deployer')
@rate_limit(max_requests=10, window=3600)  # Limit deployments to 10 per hour
def deploy():
    """Handle deployment requests with enhanced security and validation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate the configuration
        if data.get('mode') == 'expert':
            validation_result = validate_expert_config()
        else:
            validation_result = validate_simple_config()

        if not validation_result.json['valid']:
            return validation_result

        # Log deployment attempt
        app.logger.info(f'Deployment requested by user {current_user.id}')
        
        # Additional security checks
        try:
            validate_resource_name(data.get('resourceGroup', ''))
            validate_location(data.get('location', ''))
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400

        # Start deployment process
        deployment_id = f"dep-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        # Emit initial status
        app.logger.info(f'Starting deployment {deployment_id}')
        app.emit_status_update('info', f'Starting deployment {deployment_id}')

        # TODO: Implement actual deployment logic here
        # This would typically be handled by a background task

        return jsonify({
            'status': 'initiated',
            'deployment_id': deployment_id,
            'message': 'Deployment process started'
        })

    except Exception as e:
        app.logger.error(f'Deployment error: {str(e)}')
        app.emit_status_update('error', f'Deployment failed: {str(e)}')
        return jsonify({'error': str(e)}), 500

def handle_simple_deployment(data):
    """Process simple mode deployment"""
    required_fields = ['resourceGroup', 'location', 'nodeType', 'vmSize']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        # Create resource group
        resource_group = create_resource_group(data['resourceGroup'], data['location'])
        
        # Deploy VM with oracle node
        deployment_config = {
            'resource_group': data['resourceGroup'],
            'vm_name': f"{data['nodeType']}-{int(time.time())}",
            'location': data['location'],
            'vm_size': data['vmSize'],
            'node_type': data['nodeType']
        }
        
        result = deploy_vm(deployment_config)
        return jsonify({'result': result})
        
    except Exception as e:
        app.logger.error(f'Simple deployment error: {str(e)}')
        return jsonify({'error': str(e)}), 500

def handle_expert_deployment(data):
    """Process expert mode deployment"""
    # Validate network configuration
    network = data.get('network', {})
    if not network.get('vnetName') or not network.get('subnetPrefix'):
        return jsonify({'error': 'Invalid network configuration'}), 400
        
    # Validate node configuration
    nodes = data.get('nodes', {})
    if not nodes.get('count') or not nodes.get('consensusProtocol'):
        return jsonify({'error': 'Invalid node configuration'}), 400
    
    try:
        # Create network infrastructure
        network_config = {
            'vnet_name': network['vnetName'],
            'subnet_prefix': network['subnetPrefix']
        }
        network_result = create_network(network_config)
        
        # Deploy nodes
        node_results = []
        for i in range(int(nodes['count'])):
            node_config = {
                'resource_group': f"{network['vnetName']}-rg",
                'vm_name': f"node-{i+1}",
                'consensus_protocol': nodes['consensusProtocol']
            }
            node_result = deploy_vm(node_config)
            node_results.append(node_result)
        
        # Setup monitoring if enabled
        monitoring = data.get('monitoring', {})
        if monitoring.get('enabled'):
            monitoring_config = {
                'retention_days': monitoring.get('retention', 30),
                'alert_email': monitoring.get('alertEmail')
            }
            setup_monitoring_and_alerts(monitoring_config)
        
        return jsonify({
            'network': network_result,
            'nodes': node_results,
            'monitoring': monitoring.get('enabled', False)
        })
        
    except Exception as e:
        app.logger.error(f'Expert deployment error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/api/validate/simple', methods=['POST'])
@login_required
def validate_simple_config():
    """Validate simple mode configuration"""
    try:
        data = request.get_json()
        errors = []
        
        # Resource group validation
        rg_name = data.get('resourceGroup', '')
        if not re.match(r'^[a-zA-Z0-9-_]{3,64}$', rg_name):
            errors.append('Invalid resource group name')
            
        # Location validation
        location = data.get('location', '')
        valid_locations = ['eastus', 'westus', 'northeurope']  # Add more as needed
        if location not in valid_locations:
            errors.append('Invalid location')
            
        # Node type validation
        node_type = data.get('nodeType', '')
        valid_types = ['validator', 'observer', 'bootnode']
        if node_type not in valid_types:
            errors.append('Invalid node type')
            
        # VM size validation
        vm_size = data.get('vmSize', '')
        valid_sizes = ['Standard_D2s_v3', 'Standard_D4s_v3', 'Standard_D8s_v3']
        if vm_size not in valid_sizes:
            errors.append('Invalid VM size')
            
        return jsonify({
            'valid': len(errors) == 0,
            'errors': errors
        })
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'errors': [str(e)]
        }), 500

@routes_bp.route('/api/validate/expert', methods=['POST'])
@login_required
@rate_limit(max_requests=100, window=60)
def validate_expert_config():
    """Validate expert mode configuration with enhanced security"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'valid': False, 'errors': ['No data provided']}), 400

        errors = []
        
        # Network validation with detailed error messages
        network = data.get('network', {})
        if not isinstance(network, dict):
            errors.append('Network configuration must be an object')
        else:
            vnet_name = network.get('vnetName')
            if not vnet_name or not re.match(r'^[a-zA-Z0-9-_]{2,64}$', vnet_name):
                errors.append('Invalid virtual network name (2-64 chars, alphanumeric, hyphens, underscores)')
            
            subnet_prefix = network.get('subnetPrefix')
            if subnet_prefix:
                if not re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}\/[0-9]{1,2}$', subnet_prefix):
                    errors.append('Invalid subnet prefix format (e.g., 10.0.0.0/24)')
                else:
                    # Validate subnet range
                    try:
                        prefix = int(subnet_prefix.split('/')[-1])
                        if not 16 <= prefix <= 29:
                            errors.append('Subnet prefix must be between /16 and /29')
                    except ValueError:
                        errors.append('Invalid subnet prefix number')

        # Node configuration validation
        nodes = data.get('nodes', {})
        if not isinstance(nodes, dict):
            errors.append('Node configuration must be an object')
        else:
            try:
                node_count = int(nodes.get('count', 0))
                if not 1 <= node_count <= 10:
                    errors.append('Node count must be between 1 and 10')
            except ValueError:
                errors.append('Invalid node count')

            # Validate consensus protocol
            valid_protocols = ['ibft2', 'qbft', 'clique']
            protocol = nodes.get('consensusProtocol')
            if not protocol or protocol not in valid_protocols:
                errors.append(f'Invalid consensus protocol. Must be one of: {", ".join(valid_protocols)}')

        # Monitoring configuration validation
        monitoring = data.get('monitoring', {})
        if monitoring.get('enabled'):
            try:
                retention = int(monitoring.get('retention', 0))
                if not 1 <= retention <= 90:
                    errors.append('Retention period must be between 1 and 90 days')
            except ValueError:
                errors.append('Invalid retention period')

            if monitoring.get('alertEmail'):
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, monitoring['alertEmail']):
                    errors.append('Invalid email address format')

        # Security configuration validation
        security = data.get('security', {})
        if security:
            firewall_rules = security.get('firewall_rules', [])
            for rule in firewall_rules:
                try:
                    port = int(rule.get('port', -1))
                    if not 1 <= port <= 65535:
                        errors.append(f'Invalid port number: {port}. Must be between 1 and 65535')
                except ValueError:
                    errors.append(f'Invalid port value: {rule.get("port")}')

                if rule.get('protocol', '').upper() not in ['TCP', 'UDP']:
                    errors.append(f'Invalid protocol: {rule.get("protocol")}. Must be TCP or UDP')

        app.logger.info(f'Expert config validation completed with {len(errors)} errors')
        return jsonify({
            'valid': len(errors) == 0,
            'errors': errors
        })

    except Exception as e:
        app.logger.error(f'Validation error: {str(e)}')
        return jsonify({
            'valid': False,
            'errors': [str(e)]
        }), 500

def get_realtime_data():
    return {
        'deployments': 5,  # Example metric
        'uptime': '99.9%'  # Example metric
    }

# Get secret key from environment variable
SECRET_KEY = os.getenv('TOTP_SECRET_KEY', 'base32secret3232')

def validate_2fa_code(code):
    try:
        totp = pyotp.TOTP(SECRET_KEY)
        return totp.verify(code, valid_window=1)  # Allow 30s window
    except Exception:
        app.logger.error('TOTP validation error')
        return False

@routes_bp.route('/docs/<path:page>')
def docs_page(page):
    """Render markdown documentation pages with proper HTML conversion"""
    try:
        content = markdown_converter.convert_file(page)
        if content is None:
            abort(404)
        return render_template('markdown.html', content=content)
    except Exception as e:
        app.logger.error(f'Error rendering documentation: {str(e)}')
        abort(500)

@routes_bp.route('/deployer')
@login_required
def deployer():
    """Main deployer interface with proper authorization flow"""
    if not session.get('authenticated'):
        return redirect(url_for('routes.deployer_landing'))
    
    regions = [
        {"value": "eastus", "name": "East US"},
        {"value": "westus", "name": "West US"},
        {"value": "centralus", "name": "Central US"},
        {"value": "northcentralus", "name": "North Central US"},
        {"value": "southcentralus", "name": "South Central US"}
    ]
    return render_template('deployer-interface.html', regions=regions)

@routes_bp.route('/deployer/landing')
def deployer_landing():
    """Landing page for the deployer with auth check"""
    realtime_data = get_realtime_data()
    return render_template('deployer-landing.html', realtimeData=realtime_data)

# Update path for clarity and consistency
@routes_bp.route('/deployer/deploy', methods=['POST'])
@login_required
def deploy_action():
    """Handle deployment requests for both simple and expert modes"""
    return deploy()

# Validator endpoints with consistent paths
@routes_bp.route('/deployer/validate/simple', methods=['POST'])
@login_required
def validate_simple():
    return validate_simple_config()

@routes_bp.route('/deployer/validate/expert', methods=['POST'])
@login_required
def validate_expert():
    return validate_expert_config()
