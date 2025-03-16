from typing import Dict, Any
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.monitor import MonitorManagementClient
import os
import logging
from functools import lru_cache

class ServiceContainer:
    """Dependency Injection Container for services"""
    
    def __init__(self):
        self._services = {}
        self._configs = {}
        self.logger = logging.getLogger(__name__)

    def register_service(self, name: str, service: Any) -> None:
        """Register a service in the container"""
        self._services[name] = service

    def get_service(self, name: str) -> Any:
        """Get a service from the container"""
        if name not in self._services:
            raise KeyError(f"Service {name} not registered")
        return self._services[name]

    def register_config(self, name: str, config: Dict[str, Any]) -> None:
        """Register configuration in the container"""
        self._configs[name] = config

    def get_config(self, name: str) -> Dict[str, Any]:
        """Get configuration from the container"""
        if name not in self._configs:
            raise KeyError(f"Configuration {name} not registered")
        return self._configs[name]

    @lru_cache(maxsize=None)
    def get_azure_credential(self) -> DefaultAzureCredential:
        """Get Azure credential (cached)"""
        try:
            return DefaultAzureCredential()
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure credential: {str(e)}")
            raise

    def initialize_azure_clients(self) -> None:
        """Initialize Azure service clients"""
        try:
            credential = self.get_azure_credential()
            subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
            
            if not subscription_id:
                raise ValueError("AZURE_SUBSCRIPTION_ID environment variable not set")
            
            # Initialize Azure clients
            self.register_service('resource_client', 
                ResourceManagementClient(credential, subscription_id))
            
            self.register_service('network_client',
                NetworkManagementClient(credential, subscription_id))
            
            self.register_service('storage_client',
                StorageManagementClient(credential, subscription_id))
            
            self.register_service('monitor_client',
                MonitorManagementClient(credential, subscription_id))
            
            self.logger.info("Azure clients initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure clients: {str(e)}")
            raise

    def load_config_from_env(self) -> None:
        """Load configuration from environment variables"""
        config = {
            'azure': {
                'subscription_id': os.getenv('AZURE_SUBSCRIPTION_ID'),
                'tenant_id': os.getenv('AZURE_TENANT_ID'),
                'client_id': os.getenv('AZURE_CLIENT_ID'),
                'client_secret': os.getenv('AZURE_CLIENT_SECRET')
            },
            'app': {
                'secret_key': os.getenv('SECRET_KEY'),
                'jwt_secret_key': os.getenv('JWT_SECRET_KEY'),
                'environment': os.getenv('FLASK_ENV', 'production'),
                'debug': os.getenv('FLASK_DEBUG', '0') == '1'
            },
            'security': {
                'allowed_origins': os.getenv('ALLOWED_ORIGINS', '').split(','),
                'rate_limit_requests': int(os.getenv('RATE_LIMIT_REQUESTS', '100')),
                'rate_limit_window': int(os.getenv('RATE_LIMIT_WINDOW', '3600'))
            },
            'monitoring': {
                'retention_days': int(os.getenv('LOG_RETENTION_DAYS', '30')),
                'alert_email': os.getenv('ALERT_EMAIL')
            }
        }
        
        self.register_config('app_config', config)
        self.logger.info("Configuration loaded from environment")

    def initialize(self) -> None:
        """Initialize all services and configurations"""
        try:
            self.load_config_from_env()
            self.initialize_azure_clients()
            self.logger.info("Service container initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize service container: {str(e)}")
            raise

# Create global container instance
container = ServiceContainer()