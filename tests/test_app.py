import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
import os

with patch("src.app.threading.Thread"):
    from src.app import app
    from src.status import watcher_status

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
        watcher_status["watcher_running"] = True
        watcher_status["last_check_at"] = "Never"
        watcher_status["last_successful_check_at"] = "Never"
        watcher_status["successful_checks"] = 0
        watcher_status["failed_checks"] = 0
        watcher_status["last_change_at"] = "Never"

    def test_read_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Spotify Bio Watcher", response.text)
        self.assertIn("Status:</strong> Running", response.text)
        self.assertNotIn("your_client_secret", response.text)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_status_check(self):
        response = self.client.get("/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "running")
        self.assertEqual(data["watcher"], "running")
        self.assertEqual(data["successful_checks"], 0)
        self.assertEqual(data["failed_checks"], 0)

if __name__ == '__main__':
    unittest.main()
