import unittest, json
from api import create_api

class ApiHealthRequests(unittest.TestCase):

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_api("testing")
        self.client = self.app.test_client
        # binds the app to the current context
        ctx = self.app.app_context()
        ctx.push()

    def test_api_response(self):
        """Test API up and running (GET request)"""
        res = self.client().get('/api')
        self.assertEqual(res.status_code, 200)
        self.assertEqual({'status':'ok'}, json.loads(res.data))

suite = unittest.TestLoader().loadTestsFromTestCase(ApiHealthRequests)
unittest.TextTestRunner(verbosity=2).run(suite)
