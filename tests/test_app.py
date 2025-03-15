import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
import unittest

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to DeFi Oracle Meta Deployer', response.data)

    def test_login(self):
        username = os.getenv('TEST_USERNAME', 'admin')
        password = os.getenv('TEST_PASSWORD', 'password')
        response = self.app.post('/login', data=dict(username=username, password=password), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to DeFi Oracle Meta Deployer', response.data)

    def test_protected(self):
        username = os.getenv('TEST_USERNAME', 'admin')
        password = os.getenv('TEST_PASSWORD', 'password')
        self.app.post('/login', data=dict(username=username, password=password), follow_redirects=True)
        response = self.app.get('/protected')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logged in as:', response.data)

    def test_deployer_landing(self):
        response = self.app.get('/deployer')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Deployer Landing Page', response.data)

    def test_2fa_authentication(self):
        response = self.app.post('/2fa', data=dict(code='expected_code'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Deployer Interface', response.data)

    def test_deployer_interface(self):
        self.app.post('/2fa', data=dict(code='expected_code'), follow_redirects=True)
        response = self.app.get('/deploy')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Deployer Interface', response.data)

if __name__ == '__main__':
    unittest.main()