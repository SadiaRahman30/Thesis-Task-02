import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import unittest

try:
    from app import app
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


class TestApp(unittest.TestCase):
    def setUp(self):
        if HAS_FLASK:
            self.client = app.test_client()

    def test_home(self):
        if not HAS_FLASK:
            self.skipTest("Flask not installed")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_health(self):
        if not HAS_FLASK:
            self.skipTest("Flask not installed")
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "healthy")

    def test_predict(self):
        if not HAS_FLASK:
            self.skipTest("Flask not installed")
        payload = {"features": [5.1, 3.5, 1.4, 0.2]}
        response = self.client.post(
            "/predict",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("prediction", data)


if __name__ == "__main__":
    unittest.main()
