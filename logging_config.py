import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
import os
from datetime import datetime

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.utcnow().isoformat()
        if not log_record.get('level'):
            log_record['level'] = record.levelname
        if not log_record.get('module'):
            log_record['module'] = record.module
        if not log_record.get('function'):
            log_record['function'] = record.funcName
        if not log_record.get('line'):
            log_record['line'] = record.lineno

def configure_logging(app):
    """Configure comprehensive logging with structured output and rotation"""
    
    # Ensure log directory exists
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure JSON formatter
    json_formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(module)s %(function)s %(line)s %(message)s'
    )

    # Main application log handler with rotation
    main_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    main_handler.setFormatter(json_formatter)
    main_handler.setLevel(logging.INFO)

    # Error log handler with rotation
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    error_handler.setFormatter(json_formatter)
    error_handler.setLevel(logging.ERROR)

    # Access log handler with rotation
    access_handler = RotatingFileHandler(
        os.path.join(log_dir, 'access.log'),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    access_handler.setFormatter(json_formatter)
    access_handler.setLevel(logging.INFO)

    # Security log handler with rotation
    security_handler = RotatingFileHandler(
        os.path.join(log_dir, 'security.log'),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    security_handler.setFormatter(json_formatter)
    security_handler.setLevel(logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(main_handler)
    root_logger.addHandler(error_handler)

    # Configure Flask logger
    app.logger.setLevel(logging.INFO)
    for handler in app.logger.handlers:
        app.logger.removeHandler(handler)
    app.logger.addHandler(main_handler)
    app.logger.addHandler(error_handler)

    # Configure Werkzeug access logger
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    logging.getLogger('werkzeug').addHandler(access_handler)

    # Configure security logger
    security_logger = logging.getLogger('security')
    security_logger.setLevel(logging.INFO)
    security_logger.addHandler(security_handler)

    # Log startup message
    app.logger.info('Application logging configured')
    security_logger.info('Security logging configured')

    @app.before_request
    def log_request_info():
        """Log detailed request information"""
        security_logger.info('Request received', extra={
            'method': app.request.method,
            'url': app.request.url,
            'headers': dict(app.request.headers),
            'source_ip': app.request.remote_addr,
            'user_agent': app.request.user_agent.string,
            'user_id': getattr(app.current_user, 'id', None)
        })

    @app.after_request
    def log_response_info(response):
        """Log response information"""
        security_logger.info('Response sent', extra={
            'status_code': response.status_code,
            'headers': dict(response.headers)
        })
        return response

    return {
        'main_handler': main_handler,
        'error_handler': error_handler,
        'access_handler': access_handler,
        'security_handler': security_handler
    }
