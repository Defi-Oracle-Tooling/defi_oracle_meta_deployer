import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class ComprehensiveTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # Authentication & Security Tests
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.app.post('/login', data=dict(
            username='wrong',
            password='wrong'
        ), follow_redirects=True)
        self.assertIn(b'Invalid credentials', response.data)

    def test_login_sql_injection_attempt(self):
        """Test login security against SQL injection"""
        response = self.app.post('/login', data=dict(
            username="' OR '1'='1",
            password="' OR '1'='1"
        ), follow_redirects=True)
        self.assertIn(b'Invalid credentials', response.data)

    def test_2fa_invalid_code(self):
        """Test 2FA with invalid code"""
        response = self.app.post('/2fa', data=dict(
            code='invalid_code'
        ), follow_redirects=True)
        self.assertIn(b'Invalid 2FA code', response.data)

    def test_session_timeout(self):
        """Test session timeout functionality"""
        with self.app as client:
            client.post('/login', data=dict(
                username='admin',
                password='password'
            ))
            # Simulate session timeout
            with client.session_transaction() as sess:
                sess.clear()
            response = client.get('/protected')
            self.assertEqual(response.status_code, 302)  # Should redirect to login

    # Resource Management Tests
    @patch('azure_operations.create_resource_group')
    def test_create_resource_group(self, mock_create):
        """Test resource group creation"""
        mock_create.return_value = {'status': 'success'}
        response = self.app.post('/api/create-resource-group', json={
            'name': 'test-group',
            'location': 'eastus'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.get_json()['status'])

    @patch('azure_operations.deploy_vm')
    def test_deploy_vm_with_valid_config(self, mock_deploy):
        """Test VM deployment with valid configuration"""
        mock_deploy.return_value = {'status': 'success'}
        response = self.app.post('/api/deploy-vm', json={
            'vm_name': 'test-vm',
            'resource_group': 'test-group',
            'location': 'eastus',
            'vm_size': 'Standard_DS1_v2'
        })
        self.assertEqual(response.status_code, 200)

    @patch('azure_operations.deploy_vm')
    def test_deploy_vm_with_invalid_config(self, mock_deploy):
        """Test VM deployment with invalid configuration"""
        mock_deploy.side_effect = ValueError("Invalid VM size")
        response = self.app.post('/api/deploy-vm', json={
            'vm_name': 'test-vm',
            'resource_group': 'test-group',
            'location': 'eastus',
            'vm_size': 'invalid_size'
        })
        self.assertEqual(response.status_code, 400)

    # API Tests
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'healthy')

    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        response = self.app.get('/metrics')
        self.assertEqual(response.status_code, 200)
        self.assertIn('web_requests_total', response.data.decode())

    # Error Handling Tests
    def test_404_handling(self):
        """Test 404 error handling"""
        response = self.app.get('/nonexistent-page')
        self.assertEqual(response.status_code, 404)

    def test_500_handling(self):
        """Test 500 error handling"""
        with patch('app.health_check', side_effect=Exception('Internal error')):
            response = self.app.get('/health')
            self.assertEqual(response.status_code, 500)

    # ML Model Tests
    @patch('ml_model.predict_optimal_config')
    def test_ml_prediction(self, mock_predict):
        """Test ML model prediction endpoint"""
        mock_predict.return_value = {'vm_size': 'Standard_DS2_v2'}
        response = self.app.post('/api/predict-config', json={
            'workload_type': 'high-compute',
            'budget': 1000,
            'region': 'eastus'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('vm_size', response.get_json())

    # WebSocket Tests
    def test_status_updates(self):
        """Test WebSocket status updates"""
        with patch('flask_socketio.SocketIO.emit') as mock_emit:
            from app import emit_status
            emit_status('ok', 'Test message')
            mock_emit.assert_called_with('status_update', {
                'status': 'ok',
                'message': 'Test message'
            })

if __name__ == '__main__':
    unittest.main()