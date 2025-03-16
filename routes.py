import os
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, current_app as app
from flask_login import login_required, current_user
import time
import traceback
from azure_operations import create_resource_group, deploy_vm, deploy_via_rest_api, create_network, create_storage_account, setup_monitoring_and_alerts, initialize_azure_integration
from ml_model import model, predict_optimal_config
import pyotp

routes_bp = Blueprint('routes', __name__)

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
