import sys
import os
import unittest

# Ensure the 'src' directory is in the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from app import app

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_home_page(self):
        """Verify the index page renders the dashboard correctly."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Flask App', response.data)
        self.assertIn(b'19191', response.data)

    def test_health_check(self):
        """Verify the health check endpoint returns active status and proper details."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'UP')
        self.assertEqual(data['details']['port'], 19191)

    def test_api_status(self):
        """Verify the API status returns system details and uptime."""
        response = self.client.get('/api/status')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'online')
        self.assertEqual(data['port'], 19191)
        self.assertEqual(data['framework'], 'Flask')

    def test_cinnamon_endpoint(self):
        """Verify cinnamon roll endpoint GET and POST work correctly."""
        # 1. Test GET
        response = self.client.get('/api/cinnamon')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('cinnamon_roll_code', data)
        self.assertIn('cinnamon_roll_name', data)

        # 2. Test POST
        post_data = {
            "cinnamon_roll_code": "TEST-CODE-123",
            "cinnamon_roll_name": "測試用起司肉桂捲"
        }
        post_response = self.client.post('/api/cinnamon', json=post_data)
        self.assertEqual(post_response.status_code, 200)
        
        # Verify changes saved
        get_response = self.client.get('/api/cinnamon')
        get_data = get_response.get_json()
        self.assertEqual(get_data['cinnamon_roll_code'], "TEST-CODE-123")
        self.assertEqual(get_data['cinnamon_roll_name'], "測試用起司肉桂捲")

    def test_company_endpoint(self):
        """Verify afternoon company endpoint GET and POST work correctly."""
        # 1. Test GET
        response = self.client.get('/api/company')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('afternoon_company', data)
        self.assertIn('afternoon_company_location', data)

        # 2. Test POST
        post_data = {
            "afternoon_company": "測試下午公司股份有限公司",
            "afternoon_company_location": "測試地點科學園區"
        }
        post_response = self.client.post('/api/company', json=post_data)
        self.assertEqual(post_response.status_code, 200)
        
        # Verify changes saved
        get_response = self.client.get('/api/company')
        get_data = get_response.get_json()
        self.assertEqual(get_data['afternoon_company'], "測試下午公司股份有限公司")
        self.assertEqual(get_data['afternoon_company_location'], "測試地點科學園區")

if __name__ == '__main__':
    unittest.main()
