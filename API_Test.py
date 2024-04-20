import unittest
from app import app

class testAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_low_stock_levels(self):
        response = self.app.get("api/low_stock_levels")
        self.assertEqual(response.status._code, 200)

if  __name__ == "__main__":
    unittest.main()