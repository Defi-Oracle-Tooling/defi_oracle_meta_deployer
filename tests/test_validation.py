import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class ValidationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.maxDiff = None

    # Simple Mode Validation Tests
    def test_simple_mode_resource_group_validation(self):
        """Test resource group name validation rules"""
        test_cases = [
            ('valid-name-123', True),
            ('a' * 65, False),  # Too long
            ('ab', False),      # Too short
            ('invalid@name', False),  # Invalid characters
            ('VALID_NAME_123', True),
            ('valid-name_123', True),
            ('123-start-with-number', True),
            ('', False),        # Empty string
            (' space-name', False),  # Starts with space
            ('valid-name ', False),  # Ends with space
        ]

        for name, should_be_valid in test_cases:
            response = self.app.post('/api/validate/simple', json={
                'resourceGroup': name,
                'location': 'eastus',
                'nodeType': 'validator',
                'vmSize': 'Standard_D2s_v3'
            })
            data = response.get_json()
            self.assertEqual(
                data['valid'], 
                should_be_valid, 
                f"Resource group name '{name}' validation failed"
            )

    def test_simple_mode_location_validation(self):
        """Test location validation rules"""
        test_cases = [
            ('eastus', True),
            ('westus', True),
            ('northeurope', True),
            ('invalid-location', False),
            ('', False),
            ('EASTUS', False),  # Case sensitive
            ('east-us', False),  # Invalid format
        ]

        for location, should_be_valid in test_cases:
            response = self.app.post('/api/validate/simple', json={
                'resourceGroup': 'test-group',
                'location': location,
                'nodeType': 'validator',
                'vmSize': 'Standard_D2s_v3'
            })
            data = response.get_json()
            self.assertEqual(
                data['valid'], 
                should_be_valid, 
                f"Location '{location}' validation failed"
            )

    def test_simple_mode_node_type_validation(self):
        """Test node type validation rules"""
        test_cases = [
            ('validator', True),
            ('observer', True),
            ('bootnode', True),
            ('invalid-type', False),
            ('', False),
            ('VALIDATOR', False),  # Case sensitive
            ('light-node', False),  # Invalid type
        ]

        for node_type, should_be_valid in test_cases:
            response = self.app.post('/api/validate/simple', json={
                'resourceGroup': 'test-group',
                'location': 'eastus',
                'nodeType': node_type,
                'vmSize': 'Standard_D2s_v3'
            })
            data = response.get_json()
            self.assertEqual(
                data['valid'], 
                should_be_valid, 
                f"Node type '{node_type}' validation failed"
            )

    def test_simple_mode_vm_size_validation(self):
        """Test VM size validation rules"""
        test_cases = [
            ('Standard_D2s_v3', True),
            ('Standard_D4s_v3', True),
            ('Standard_D8s_v3', True),
            ('invalid-size', False),
            ('', False),
            ('standard_d2s_v3', False),  # Case sensitive
            ('Standard_D16s_v3', False),  # Not in allowed list
        ]

        for vm_size, should_be_valid in test_cases:
            response = self.app.post('/api/validate/simple', json={
                'resourceGroup': 'test-group',
                'location': 'eastus',
                'nodeType': 'validator',
                'vmSize': vm_size
            })
            data = response.get_json()
            self.assertEqual(
                data['valid'], 
                should_be_valid, 
                f"VM size '{vm_size}' validation failed"
            )

    # Expert Mode Validation Tests
    def test_expert_mode_network_validation(self):
        """Test network configuration validation"""
        test_cases = [
            # Valid cases
            ({
                'vnetName': 'valid-network',
                'subnetPrefix': '10.0.0.0/24'
            }, True),
            # Invalid vnet name
            ({
                'vnetName': 'invalid@network',
                'subnetPrefix': '10.0.0.0/24'
            }, False),
            # Invalid subnet prefix
            ({
                'vnetName': 'valid-network',
                'subnetPrefix': '10.0.0.0'
            }, False),
            # Missing vnet name
            ({
                'subnetPrefix': '10.0.0.0/24'
            }, False),
            # Invalid subnet range
            ({
                'vnetName': 'valid-network',
                'subnetPrefix': '256.0.0.0/24'
            }, False),
            # Invalid subnet mask
            ({
                'vnetName': 'valid-network',
                'subnetPrefix': '10.0.0.0/33'
            }, False)
        ]

        for network_config, should_be_valid in test_cases:
            response = self.app.post('/api/validate/expert', json={
                'network': network_config,
                'nodes': {
                    'count': 3,
                    'consensusProtocol': 'ibft2'
                }
            })
            data = response.get_json()
            self.assertEqual(
                data['valid'], 
                should_be_valid, 
                f"Network config {network_config} validation failed"
            )

    def test_expert_mode_node_configuration(self):
        """Test node configuration validation"""
        test_cases = [
            # Valid cases
            ({
                'count': 3,
                'consensusProtocol': 'ibft2'
            }, True),
            # Invalid node count
            ({
                'count': 0,
                'consensusProtocol': 'ibft2'
            }, False),
            # Invalid consensus protocol
            ({
                'count': 3,
                'consensusProtocol': 'invalid'
            }, False),
            # Missing count
            ({
                'consensusProtocol': 'ibft2'
            }, False),
            # Too many nodes
            ({
                'count': 11,
                'consensusProtocol': 'ibft2'
            }, False),
            # Invalid count type
            ({
                'count': 'three',
                'consensusProtocol': 'ibft2'
            }, False)
        ]

        for node_config, should_be_valid in test_cases:
            response = self.app.post('/api/validate/expert', json={
                'network': {
                    'vnetName': 'test-network',
                    'subnetPrefix': '10.0.0.0/24'
                },
                'nodes': node_config
            })
            data = response.get_json()
            self.assertEqual(
                data['valid'], 
                should_be_valid, 
                f"Node config {node_config} validation failed"
            )

    def test_expert_mode_monitoring_validation(self):
        """Test monitoring configuration validation"""
        test_cases = [
            # Valid cases
            ({
                'enabled': True,
                'retention': 30,
                'alertEmail': 'test@example.com'
            }, True),
            # Invalid retention period
            ({
                'enabled': True,
                'retention': 0,
                'alertEmail': 'test@example.com'
            }, False),
            # Invalid email
            ({
                'enabled': True,
                'retention': 30,
                'alertEmail': 'invalid-email'
            }, False),
            # Missing email when enabled
            ({
                'enabled': True,
                'retention': 30
            }, False),
            # Valid when disabled (no other fields required)
            ({
                'enabled': False
            }, True),
            # Retention too high
            ({
                'enabled': True,
                'retention': 91,
                'alertEmail': 'test@example.com'
            }, False)
        ]

        for monitoring_config, should_be_valid in test_cases:
            response = self.app.post('/api/validate/expert', json={
                'network': {
                    'vnetName': 'test-network',
                    'subnetPrefix': '10.0.0.0/24'
                },
                'nodes': {
                    'count': 3,
                    'consensusProtocol': 'ibft2'
                },
                'monitoring': monitoring_config
            })
            data = response.get_json()
            self.assertEqual(
                data['valid'], 
                should_be_valid, 
                f"Monitoring config {monitoring_config} validation failed"
            )

    def test_complete_expert_mode_validation(self):
        """Test complete expert mode configuration validation"""
        valid_config = {
            'mode': 'expert',
            'network': {
                'vnetName': 'test-network',
                'subnetPrefix': '10.0.0.0/24'
            },
            'nodes': {
                'count': 3,
                'consensusProtocol': 'ibft2'
            },
            'monitoring': {
                'enabled': True,
                'retention': 30,
                'alertEmail': 'test@example.com'
            }
        }

        response = self.app.post('/api/validate/expert', json=valid_config)
        data = response.get_json()
        self.assertTrue(data['valid'], "Valid complete configuration failed validation")

        # Test with missing required sections
        required_sections = ['network', 'nodes']
        for section in required_sections:
            invalid_config = valid_config.copy()
            del invalid_config[section]
            response = self.app.post('/api/validate/expert', json=invalid_config)
            data = response.get_json()
            self.assertFalse(
                data['valid'], 
                f"Configuration missing {section} should be invalid"
            )

    def test_validation_error_messages(self):
        """Test that validation error messages are clear and helpful"""
        test_cases = [
            # Resource group name too short
            ({
                'mode': 'simple',
                'resourceGroup': 'ab',
                'location': 'eastus',
                'nodeType': 'validator',
                'vmSize': 'Standard_D2s_v3'
            }, 'Resource group name must be 3-64 characters'),
            # Invalid location
            ({
                'mode': 'simple',
                'resourceGroup': 'test-group',
                'location': 'invalid',
                'nodeType': 'validator',
                'vmSize': 'Standard_D2s_v3'
            }, 'Invalid location'),
            # Invalid subnet prefix
            ({
                'mode': 'expert',
                'network': {
                    'vnetName': 'test-network',
                    'subnetPrefix': 'invalid'
                },
                'nodes': {
                    'count': 3,
                    'consensusProtocol': 'ibft2'
                }
            }, 'Invalid subnet prefix')
        ]

        for config, expected_error in test_cases:
            endpoint = '/api/validate/simple' if config['mode'] == 'simple' else '/api/validate/expert'
            response = self.app.post(endpoint, json=config)
            data = response.get_json()
            self.assertIn(
                expected_error,
                str(data.get('errors', [])),
                f"Expected error message not found for config: {config}"
            )

    def test_concurrent_validation_requests(self):
        """Test handling of concurrent validation requests"""
        import concurrent.futures
        import json

        def make_request():
            return self.app.post('/api/validate/simple', json={
                'resourceGroup': 'test-group',
                'location': 'eastus',
                'nodeType': 'validator',
                'vmSize': 'Standard_D2s_v3'
            })

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]

        for response in responses:
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['valid'])

if __name__ == '__main__':
    unittest.main()