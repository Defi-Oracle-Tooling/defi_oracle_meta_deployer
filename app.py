from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from flask import Flask, request, jsonify, render_template, redirect, url_for
import subprocess
import requests
import json
import logging
from sklearn.ensemble import RandomForestClassifier
import joblib
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from logging.handlers import RotatingFileHandler
from flask_healthz import healthz
from prometheus_client import Counter, generate_latest, Histogram, CONTENT_TYPE_LATEST
from flask_socketio import SocketIO, emit
from pythonjsonlogger import jsonlogger
import traceback
import time
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Add Prometheus metrics
REQUESTS = Counter('web_requests_total', 'Total web requests', ['endpoint'])
LATENCY = Histogram('web_request_latency_seconds', 'Request latency in seconds', ['endpoint'])

# Register health check blueprint
app.register_blueprint(healthz, url_prefix="/health")

# Health check functions
def liveness():
    pass  # Basic check - if this runs, app is alive

def readiness():
    try:
        # Check if ML model is loaded
        if not hasattr(app, 'model'):
            return False
        # Add any other readiness checks (database, external services, etc)
        return True
    except Exception:
        return False

app.config.update(
    HEALTHZ = {
        "live": liveness,
        "ready": readiness,
    }
)

# Set the secret key for session management
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':  # Replace with proper authentication
            user = User(id=1)
            login_user(user)
            return redirect(url_for('index'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/protected')
@login_required
def protected():
    return 'Logged in as: ' + current_user.id

# Enhanced logging configuration
logging.basicConfig(level=logging.DEBUG)
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Add a console handler for logging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
app.logger.addHandler(console_handler)

# Enhance logging with JSON formatter
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
app.logger.addHandler(logHandler)

# Load pre-trained machine learning model
model = joblib.load('ml_model.pkl')

@app.route("/", methods=["GET"])
def index():
    app.logger.info('Index page accessed')
    regions = [
        {"value": "eastus", "name": "East US"},
        {"value": "westus", "name": "West US"},
        {"value": "centralus", "name": "Central US"},
        {"value": "northcentralus", "name": "North Central US"},
        {"value": "southcentralus", "name": "South Central US"}
    ]
    return render_template("index.html", regions=regions)

@app.route("/execute", methods=["POST"])
@login_required
def execute_action():
    try:
        action = request.form.get("action")
        config = request.form.get("config")
        app.logger.info(f'Action: {action} executed with config: {config}')
        
        emit_status('processing', f'Starting {action}...')
        
        if action == "create_rg":
            result = create_resource_group(config)
            emit_status('success', 'Resource group created successfully')
        elif action == "deploy_vm":
            result = deploy_vm(config)
            emit_status('success', 'VM deployed successfully')
        elif action == "rest_deploy":
            result = deploy_via_rest_api(config)
            emit_status('success', 'REST deployment completed')
        else:
            emit_status('error', 'Unknown action selected')
            result = "Unknown action selected."
            
        return jsonify({'result': result})
    except Exception as e:
        app.logger.error(f'Error in execute_action: {str(e)}\n{traceback.format_exc()}')
        emit_status('error', str(e))
        return jsonify({'error': str(e)}), 500

@app.route("/validate_config", methods=["POST"])
@login_required
def validate_config():
    config = request.json
    app.logger.info(f'Config validation requested: {config}')
    config_data, error = validate_config_data(config)
    if error:
        app.logger.error(f'Config validation error: {error}')
        return jsonify({"valid": False, "error": error})
    return jsonify({"valid": True})

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    message = request.json.get('message')
    app.logger.info(f'Chat message received: {message}')
    # Here you would integrate with an LLM to get a response
    response = "This is a placeholder response from the LLM."
    return jsonify({"response": response})

@app.route("/predict", methods=["POST"])
@login_required
def predict():
    config = request.form.get("config")
    app.logger.info(f'Prediction requested for config: {config}')
    config_data, error = validate_config(config)
    if error:
        app.logger.error(f'Prediction error: {error}')
        return jsonify({"error": error})
    # Extract features from the configuration data
    features = [
        config_data.get("vm_name", ""),
        config_data.get("admin_username", ""),
        config_data.get("resource_group", ""),
        config_data.get("location", ""),
        config_data.get("image", ""),
    ]
    # Predict using the pre-trained model
    prediction = model.predict([features])
    app.logger.info(f'Prediction result: {prediction[0]}')
    return jsonify({"prediction": prediction[0]})

# Enhanced validation function

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


def run_command(cmd):
    try:
        logging.info("Executing command: %s", " ".join(cmd))
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
        return output
    except subprocess.CalledProcessError as e:
        logging.error("Command failed: %s", e.output)
        return f"Error: {e.output}"


def create_resource_group(config):
    config_data, error = validate_config(config)
    if error:
        return error
    cmd = ["az", "group", "create", "--name", config_data.get("name", "BesuResourceGroup"), "--location", config_data.get("location", "eastus")]
    return run_command(cmd)


def deploy_vm(config):
    config_data, error = validate_config(config)
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


def deploy_via_rest_api(config):
    config_data, error = validate_config(config)
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


def setup_monitoring_and_alerts(resource_group, vm_name):
    try:
        log_analytics_workspace = run_command([
            "az", "monitor", "log-analytics", "workspace", "create",
            "--resource-group", resource_group,
            "--workspace-name", f"{vm_name}-log-analytics"
        ])
        logging.info("Log Analytics workspace created: %s", log_analytics_workspace)
        enable_monitoring = run_command([
            "az", "monitor", "diagnostic-settings", "create",
            "--resource-group", resource_group,
            "--workspace", f"{vm_name}-log-analytics",
            "--name", f"{vm_name}-monitoring",
            "--vm", vm_name,
            "--metrics", "AllMetrics",
            "--logs", "AllLogs"
        ])
        logging.info("Monitoring enabled for VM: %s", enable_monitoring)
        create_alert = run_command([
            "az", "monitor", "metrics", "alert", "create",
            "--resource-group", resource_group,
            "--name", f"{vm_name}-cpu-alert",
            "--scopes", f"/subscriptions/{os.getenv('AZURE_SUBSCRIPTION_ID')}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}",
            "--condition", "avg Percentage CPU > 80",
            "--description", "Alert when CPU usage is over 80%",
            "--action", "email@example.com"
        ])
        logging.info("Alert rule created: %s", create_alert)
        return "Monitoring and alerts setup successfully."
    except Exception as e:
        logging.error("Failed to setup monitoring and alerts: %s", str(e))
        return f"Exception occurred: {str(e)}"

def emit_status(status, message):
    """Emit status updates to connected clients"""
    socketio.emit('status_update', {'status': status, 'message': message})
    app.logger.info(f'Status update: {status} - {message}')

@app.errorhandler(Exception)
def handle_error(error):
    app.logger.error(f'Unhandled error: {str(error)}\n{traceback.format_exc()}')
    emit_status('error', str(error))
    return jsonify({'error': str(error)}), 500

# Custom error handlers
@app.errorhandler(404)
def page_not_found(e):
    app.logger.error(f'Page not found: {request.url}')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f'Server error: {e}, URL: {request.url}')
    return render_template('500.html'), 500

# Health check endpoint for Docker
@app.route('/health')
def health_check():
    REQUESTS.labels(endpoint='/health').inc()
    return jsonify({"status": "healthy"}), 200

# Metrics endpoint for monitoring
@app.route('/metrics')
def metrics():
    REQUESTS.labels(endpoint='/metrics').inc()
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    if request.path != '/metrics':
        latency = time.time() - request.start_time
        REQUESTS.labels(endpoint=request.path).inc()
        LATENCY.labels(endpoint=request.path).observe(latency)
    return response

def check_system_status():
    """Periodic system status check"""
    try:
        # Add your system checks here
        app.logger.info("System status check completed")
        emit_status_update('ok', 'System running normally')
    except Exception as e:
        app.logger.error(f"System check failed: {str(e)}")
        emit_status_update('error', f'System check failed: {str(e)}')

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_system_status, trigger="interval", minutes=5)
scheduler.start()

if __name__ == "__main__":
    socketio.run(app, debug=os.getenv('FLASK_ENV') == 'development', host="0.0.0.0", port=5000)
