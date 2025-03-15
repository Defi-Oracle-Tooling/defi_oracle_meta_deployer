import os
import unittest
from app import app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Azure Automation Orchestration Tool', response.data)

    def test_login(self):
        username = os.getenv('TEST_USERNAME', 'admin')
        password = os.getenv('TEST_PASSWORD', 'password')
        response = self.app.post('/login', data=dict(username=username, password=password), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Azure Automation Orchestration Tool', response.data)

    def test_protected(self):
        username = os.getenv('TEST_USERNAME', 'admin')
        password = os.getenv('TEST_PASSWORD', 'password')
        self.app.post('/login', data=dict(username=username, password=password), follow_redirects=True)
        response = self.app.get('/protected')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logged in as:', response.data)

if __name__ == '__main__':
    unittest.main()