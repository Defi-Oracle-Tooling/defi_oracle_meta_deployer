from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
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
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.storage import StorageManagementClient
from auth import auth_bp, login_manager
from logging_config import configure_logging
from azure_operations import create_resource_group, deploy_vm, deploy_via_rest_api, create_network, create_storage_account, setup_monitoring_and_alerts, initialize_azure_integration
from ml_model import model, predict_optimal_config
from routes import routes_bp

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(routes_bp)

# Initialize Flask-Login
login_manager.init_app(app)

# Configure logging
configure_logging(app)

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

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

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

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
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

def emit_status(status, message):
    """Emit status updates to connected clients"""
    socketio.emit('status_update', {'status': status, 'message': message})
    app.logger.info(f'Status update: {status} - {message}')

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_system_status, trigger="interval", minutes=5)
scheduler.start()

if __name__ == "__main__":
    socketio.run(app, debug=os.getenv('FLASK_ENV') == 'development', host="0.0.0.0", port=5000)
