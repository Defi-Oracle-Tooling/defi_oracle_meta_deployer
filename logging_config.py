import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger

# Enhanced logging configuration
logging.basicConfig(level=logging.DEBUG)
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add a console handler for logging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# Enhance logging with JSON formatter
logHandler = logging.StreamHandler()
json_formatter = jsonlogger.JsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
logHandler.setFormatter(json_formatter)

# Function to configure logging
def configure_logging(app):
    app.logger.addHandler(handler)
    app.logger.addHandler(console_handler)
    app.logger.addHandler(logHandler)
