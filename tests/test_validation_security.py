import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class ValidationSecurityTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.maxDiff = None

    def test_input_sanitization(self):
        """Test that inputs are properly sanitized"""
        test_cases = [
            # XSS attempts
            ({
                'resourceGroup': '<script>alert("xss")</script>',
                'location': 'eastus',
                'nodeType': 'validator',
                'vmSize': 'Standard_D2s_v3'
            }, False),
            # SQL injection attempts
            ({
                'resourceGroup': "my-group'; DROP TABLE users;--",
                'location': 'eastus',
                'nodeType': 'validator',
                'vmSize': 'Standard_D2s_v3'
            }, False),
            # Command injection attempts
            ({
                'resourceGroup': 'valid-group && rm -rf /',
                'location': 'eastus',
                'nodeType': 'validator',
                'vmSize': 'Standard_D2s_v3'
            }, False),
            # Unicode normalization attacks
            ({
                'resourceGroup': 'valid\u0307-group',
                'location': 'eastus',
                'nodeType': 'validator',
                'vmSize': 'Standard_D2s_v3'
            }, False)
        ]

        for config, should_be_valid in test_cases:
            response = self.app.post('/api/validate/simple', json=config)
            data = response.get_json()
            self.assertEqual(data['valid'], should_be_valid)

    def test_large_input_handling(self):
        """Test handling of unusually large inputs"""
        large_input = 'a' * 1024 * 1024  # 1MB of data
        response = self.app.post('/api/validate/simple', json={
            'resourceGroup': large_input,
            'location': 'eastus',
            'nodeType': 'validator',
            'vmSize': 'Standard_D2s_v3'
        })
        self.assertEqual(response.status_code, 400)

    def test_malformed_json(self):
        """Test handling of malformed JSON input"""
        test_cases = [
            ('{"incomplete": "json"', 400),
            ('not json at all', 400),
            ('[]', 400),  # Valid JSON but wrong type
            ('null', 400),
            ('{"resourceGroup": null}', 400)
        ]

        for payload, expected_status in test_cases:
            response = self.app.post(
                '/api/validate/simple',
                data=payload,
                content_type='application/json'
            )
            self.assertEqual(response.status_code, expected_status)

    def test_expert_mode_security_validation(self):
        """Test security-related validation in expert mode"""
        test_cases = [
            # CIDR range too broad
            ({
                'network': {
                    'vnetName': 'test-network',
                    'subnetPrefix': '0.0.0.0/0'
                }
            }, False),
            # Potential internal network access
            ({
                'network': {
                    'vnetName': 'test-network',
                    'subnetPrefix': '192.168.0.0/16'
                }
            }, False),
            # Overlapping with Azure internal ranges
            ({
                'network': {
                    'vnetName': 'test-network',
                    'subnetPrefix': '169.254.0.0/16'
                }
            }, False)
        ]

        for config, should_be_valid in test_cases:
            config.update({
                'nodes': {
                    'count': 3,
                    'consensusProtocol': 'ibft2'
                }
            })
            response = self.app.post('/api/validate/expert', json=config)
            data = response.get_json()
            self.assertEqual(data['valid'], should_be_valid)

    def test_monitoring_email_validation(self):
        """Test thorough email validation for monitoring configuration"""
        test_cases = [
            # Valid cases
            'test@example.com',
            'test.name@example.co.uk',
            'test+label@example.com',
            # Invalid cases
            '@example.com',
            'test@',
            'test@.com',
            'test@example.',
            'test@example..com',
            ' test@example.com',
            'test@example.com ',
            'test@@example.com',
            'test@example@com',
            # Length limits
            'a@b.c',  # Too short
            ('a' * 65 + '@example.com'),  # Local part too long
            ('test@' + 'a' * 255 + '.com'),  # Domain too long
        ]

        base_config = {
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
                'retention': 30
            }
        }

        for email in test_cases:
            config = json.loads(json.dumps(base_config))
            config['monitoring']['alertEmail'] = email
            response = self.app.post('/api/validate/expert', json=config)
            data = response.get_json()
            should_be_valid = '@' in email and '.' in email.split('@')[1] and len(email) > 5
            self.assertEqual(
                data['valid'],
                should_be_valid,
                f"Email validation failed for: {email}"
            )

    def test_consensus_protocol_compatibility(self):
        """Test consensus protocol compatibility with node configurations"""
        test_cases = [
            # Valid combinations
            ({
                'count': 4,
                'consensusProtocol': 'ibft2'
            }, True),
            ({
                'count': 1,
                'consensusProtocol': 'clique'
            }, True),
            # Invalid combinations
            ({
                'count': 1,
                'consensusProtocol': 'ibft2'  # IBFT2 requires at least 4 nodes
            }, False),
            ({
                'count': 2,
                'consensusProtocol': 'qbft'  # QBFT requires at least 4 nodes
            }, False)
        ]

        base_config = {
            'network': {
                'vnetName': 'test-network',
                'subnetPrefix': '10.0.0.0/24'
            }
        }

        for node_config, should_be_valid in test_cases:
            config = json.loads(json.dumps(base_config))
            config['nodes'] = node_config
            response = self.app.post('/api/validate/expert', json=config)
            data = response.get_json()
            self.assertEqual(
                data['valid'],
                should_be_valid,
                f"Consensus protocol validation failed for: {node_config}"
            )

    def test_rate_limiting(self):
        """Test rate limiting on validation endpoints"""
        # Make 100 requests in quick succession
        responses = []
        for _ in range(100):
            response = self.app.post('/api/validate/simple', json={
                'resourceGroup': 'test-group',
                'location': 'eastus',
                'nodeType': 'validator',
                'vmSize': 'Standard_D2s_v3'
            })
            responses.append(response.status_code)

        # Should see some 429 (Too Many Requests) responses
        self.assertTrue(
            429 in responses,
            "Rate limiting not properly enforced"
        )

if __name__ == '__main__':
    unittest.main()