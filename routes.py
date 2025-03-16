import os
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, current_app as app
from flask_login import login_required, current_user
import time
import traceback
from azure_operations import create_resource_group, deploy_vm, deploy_via_rest_api, create_network, create_storage_account, setup_monitoring_and_alerts, initialize_azure_integration
from ml_model import model, predict_optimal_config
import pyotpimport os

routes_bp = Blueprint('routes', __name__)routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/', methods=['GET'])oute('/', methods=['GET'])
def index():
    app.logger.info('Index page accessed')info('Index page accessed')
    regions = [
        {"value": "eastus", "name": "East US"},
        {"value": "westus", "name": "West US"},
        {"value": "centralus", "name": "Central US"},
        {"value": "northcentralus", "name": "North Central US"},,
        {"value": "southcentralus", "name": "South Central US"}   {"value": "southcentralus", "name": "South Central US"}
    ]
    return render_template('index.html', regions=regions)    return render_template('index.html', regions=regions)

@routes_bp.route('/about')oute('/about')
def about():
    return render_template('about.html')    return render_template('about.html')

@routes_bp.route('/docs')route('/docs')
def docs():
    return render_template('docs.html')    return render_template('docs.html')

@routes_bp.route('/contact')te('/contact')
def contact():
    return render_template('contact.html')    return render_template('contact.html')

@routes_bp.route('/deploy')ute('/deploy')
def deploy():
    return render_template('deploy.html')    return render_template('deploy.html')

@routes_bp.route('/terms')oute('/terms')
def terms():
    return render_template('terms.html')    return render_template('terms.html')

@routes_bp.route('/execute', methods=['POST'])e('/execute', methods=['POST'])
@login_required
def execute_action():ute_action():
    try:
        action = request.form.get('action')
        config = request.form.get('config')st.form.get('config')
        if not config:
            config = load_default_config(action)
        app.logger.info(f'Action: {action} executed with config: {config}')onfig: {config}')
        emit_status('processing', f'Starting {action}...')..')
        result = handle_decision_point(action, config)t(action, config)
        if 'error' in result.lower():
            emit_status('error', result)mit_status('error', result)
        else:
            emit_status('success', result)
        return jsonify({'result': result})esult': result})
    except Exception as e:
        app.logger.error(f'Error in execute_action: {str(e)}\n{traceback.format_exc()}')execute_action: {str(e)}\n{traceback.format_exc()}')
        emit_status('error', str(e))
        return jsonify({'error': str(e)}), 500        return jsonify({'error': str(e)}), 500

@routes_bp.route('/validate_config', methods=['POST'])e('/validate_config', methods=['POST'])
@login_required
def validate_config():
    config = request.json
    app.logger.info(f'Config validation requested: {config}')onfig}')
    config_data, error = validate_config_data(config)ta, error = validate_config_data(config)
    if error:
        app.logger.error(f'Config validation error: {error}')or}')
        return jsonify({'valid': False, 'error': error})lse, 'error': error})
    return jsonify({'valid': True})    return jsonify({'valid': True})

@routes_bp.route('/chat', methods=['POST'])e('/chat', methods=['POST'])
@login_requiredired
def chat():
    message = request.json.get('message')
    app.logger.info(f'Chat message received: {message}')
    response = 'This is a placeholder response from the LLM.'onse from the LLM.'
    return jsonify({'response': response})    return jsonify({'response': response})

@routes_bp.route('/predict', methods=['POST'])e('/predict', methods=['POST'])
@login_requiredd
def predict():
    config = request.form.get('config')
    app.logger.info(f'Prediction requested for config: {config}')onfig: {config}')
    config_data, error = validate_config(config)ta, error = validate_config(config)
    if error:
        app.logger.error(f'Prediction error: {error}')ror: {error}')
        return jsonify({'error': error})sonify({'error': error})
    features = [
        config_data.get('vm_name', ''),
        config_data.get('admin_username', ''),
        config_data.get('resource_group', ''),, ''),
        config_data.get('location', ''),''),
        config_data.get('image', '')   config_data.get('image', '')
    ]
    prediction = model.predict([features])
    app.logger.info(f'Prediction result: {prediction[0]}')ion[0]}')
    return jsonify({'prediction': prediction[0]})    return jsonify({'prediction': prediction[0]})

@routes_bp.route('/create_network', methods=['POST'])e('/create_network', methods=['POST'])
@login_required
def create_network_route():):
    config = request.json
    app.logger.info(f'Network creation requested: {config}')ion requested: {config}')
    result = create_network(config)
    return jsonify({'result': result})    return jsonify({'result': result})

@routes_bp.route('/create_storage_account', methods=['POST'])e('/create_storage_account', methods=['POST'])
@login_required
def create_storage_account_route():t_route():
    config = request.json
    app.logger.info(f'Storage account creation requested: {config}')ion requested: {config}')
    result = create_storage_account(config)nfig)
    return jsonify({'result': result})    return jsonify({'result': result})

@routes_bp.route('/create_resource_group', methods=['POST'])e('/create_resource_group', methods=['POST'])
@login_required
def create_resource_group_route():_route():
    config = request.json
    app.logger.info(f'Resource group creation requested: {config}')logger.info(f'Resource group creation requested: {config}')
    try:
        resource_group_params = {'location': config['location']}
        resource_client.resource_groups.create_or_update(config['name'], resource_group_params)resource_group_params)
        return jsonify({'result': 'Resource group created successfully'})esult': 'Resource group created successfully'})
    except Exception as e:
        app.logger.error(f'Error creating resource group: {str(e)}')urce group: {str(e)}')
        return jsonify({'error': str(e)}), 500        return jsonify({'error': str(e)}), 500

@routes_bp.route('/deploy_vm', methods=['POST'])e('/deploy_vm', methods=['POST'])
@login_required
def deploy_vm_route():
    config = request.json
    app.logger.info(f'VM deployment requested: {config}')logger.info(f'VM deployment requested: {config}')
    try:
        return jsonify({'result': 'VM deployed successfully'})esult': 'VM deployed successfully'})
    except Exception as e:
        app.logger.error(f'Error deploying VM: {str(e)}') {str(e)}')
        return jsonify({'error': str(e)}), 500        return jsonify({'error': str(e)}), 500

@routes_bp.route('/setup_monitoring', methods=['POST'])e('/setup_monitoring', methods=['POST'])
@login_required
def setup_monitoring_route():e():
    config = request.json
    app.logger.info(f'Monitoring setup requested: {config}')
    result = setup_monitoring_and_alerts(config['resource_group'], config['vm_name'])ts(config['resource_group'], config['vm_name'])
    return jsonify({'result': result})    return jsonify({'result': result})

@routes_bp.route('/predict_optimal_config', methods=['POST'])e('/predict_optimal_config', methods=['POST'])
@login_required
def predict_optimal_config_route():g_route():
    config = request.json
    app.logger.info(f'Optimal config prediction requested: {config}')nfo(f'Optimal config prediction requested: {config}')
    features = [
        config.get('vm_name', ''),
        config.get('admin_username', ''),
        config.get('resource_group', ''),, ''),
        config.get('location', ''),''),
        config.get('image', '')   config.get('image', '')
    ]
    prediction = predict_optimal_config(features)redict_optimal_config(features)
    if prediction:
        return jsonify({'prediction': prediction})eturn jsonify({'prediction': prediction})
    else:
        return jsonify({'error': 'Prediction failed'}), 500        return jsonify({'error': 'Prediction failed'}), 500

@routes_bp.route('/docs/introduction')introduction')
def docs_introduction():
    return render_template('docs/introduction.md')    return render_template('docs/introduction.md')

@routes_bp.route('/docs/setup')'/docs/setup')
def docs_setup():
    return render_template('docs/setup.md')    return render_template('docs/setup.md')

@routes_bp.route('/docs/usage')'/docs/usage')
def docs_usage():
    return render_template('docs/usage.md')    return render_template('docs/usage.md')

@routes_bp.route('/docs/api_reference')pi_reference')
def docs_api_reference():
    return render_template('docs/api_reference.md')    return render_template('docs/api_reference.md')

@routes_bp.route('/deployer', methods=['GET'])oyer', methods=['GET'])
def deployer_landing():
    realtime_data = get_realtime_data()
    return render_template('deployer-landing.html', realtimeData=realtime_data)    return render_template('deployer-landing.html', realtimeData=realtime_data)

@routes_bp.route('/2fa', methods=['POST'])', methods=['POST'])
def two_factor_auth():
    code = request.form['code']
    if validate_2fa_code(code):
        session['authenticated'] = True
        return redirect(url_for('routes.deployer_interface'))   return jsonify({'error': 'No 2FA code provided'}), 400
    else:
        return 'Invalid 2FA code', 401        if validate_2fa_code(code):

@routes_bp.route('/deploy', methods=['GET'])y({'message': 'Authentication successful'}), 200
def deployer_interface():
    if not session.get('authenticated'):401
        return redirect(url_for('routes.deployer_landing'))
    initialize_azure_integration()
    return render_template('deployer-full.html')        return jsonify({'error': 'Authentication failed'}), 500

# Helper function to simulate fetching real-time datay', methods=['GET'])
def get_realtime_data():_interface():
    return {
        'deployments': 5,  # Example metricloyer_landing'))
        'uptime': '99.9%'  # Example metricnitialize_azure_integration()
    }    return render_template('deployer-full.html')

# Function for validating the 2FA code using TOTP
SECRET_KEY = 'base32secret3232'  # This should be stored securelydef get_realtime_data():

def validate_2fa_code(code):ple metric
    totp = pyotp.TOTP(SECRET_KEY) Example metric
    return totp.verify(code)    }


# Get secret key from environment variable
SECRET_KEY = os.getenv('TOTP_SECRET_KEY', 'base32secret3232')

# Function for validating the 2FA code using TOTP
def validate_2fa_code(code):
    try:
        totp = pyotp.TOTP(SECRET_KEY)
        return totp.verify(code, valid_window=1)  # Allow 30s window
    except Exception:
        app.logger.error('TOTP validation error')
        return False
