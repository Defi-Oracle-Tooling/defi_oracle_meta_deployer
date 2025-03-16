from flask import Flask
from dependency_container import container
from logging_config import configure_logging
from auth import auth_bp, login_manager
from routes import routes_bp
from flask_cors import CORS
from flask_healthz import healthz
from flask_socketio import SocketIO
from prometheus_client import Counter, Histogram, CONTENT_TYPE_LATEST
import json
import logging.config
from datetime import datetime
import os

def create_app():
    """Application factory with proper initialization"""
    app = Flask(__name__)
    
    # Load configuration
    container.initialize()
    app_config = container.get_config('app_config')
    
    # Configure app
    app.config.update({
        'SECRET_KEY': app_config['app']['secret_key'],
        'JWT_SECRET_KEY': app_config['app']['jwt_secret_key'],
        'DEBUG': app_config['app']['debug']
    })
    
    # Initialize logging
    log_handlers = configure_logging(app)
    
    # Configure CORS
    CORS(app, resources={
        r"/*": {
            "origins": app_config['security']['allowed_origins'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Range", "X-Content-Range"],
            "supports_credentials": True,
            "max_age": 600
        }
    })
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)
    app.register_blueprint(healthz, url_prefix="/health")
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    
    # Add Prometheus metrics
    REQUESTS = Counter('web_requests_total', 'Total web requests', ['endpoint'])
    LATENCY = Histogram('web_request_latency_seconds', 'Request latency', ['endpoint'])
    
    # Health check functions
    def liveness():
        pass
    
    def readiness():
        try:
            # Check Azure clients
            container.get_service('resource_client')
            return True
        except Exception:
            app.logger.error("Readiness check failed - Azure clients not initialized")
            return False
    
    app.config.update(
        HEALTHZ = {
            "live": liveness,
            "ready": readiness,
        }
    )
    
    @app.before_request
    def before_request():
        request.start_time = datetime.utcnow()
    
    @app.after_request
    def after_request(response):
        try:
            # Add security headers
            response.headers.update({
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'SAMEORIGIN',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'",
                'Referrer-Policy': 'strict-origin-when-cross-origin'
            })
            
            # Update metrics
            if hasattr(request, 'start_time'):
                latency = (datetime.utcnow() - request.start_time).total_seconds()
                LATENCY.labels(endpoint=request.path).observe(latency)
            REQUESTS.labels(endpoint=request.path).inc()
            
        except Exception as e:
            app.logger.error(f"Error in after_request: {str(e)}")
            
        return response
    
    @app.errorhandler(Exception)
    def handle_error(error):
        app.logger.error(f"Unhandled error: {str(error)}", exc_info=True)
        return json.dumps({
            'error': str(error),
            'type': error.__class__.__name__
        }), 500
    
    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
