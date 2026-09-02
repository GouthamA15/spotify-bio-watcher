import unittest
from unittest.mock import patch, MagicMock
import io
import sys
import requests

from src.notifier import send_notification

class TestNotifier(unittest.TestCase):
    
    @patch('src.notifier.NTFY_TOPIC', 'test_topic')
    @patch('src.notifier.requests.post')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_successful_notification(self, mock_stdout, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        send_notification("AAA", "BBB", "2026-09-02 12:45:36")
        
        mock_post.assert_called_once()
        output = mock_stdout.getvalue()
        self.assertIn("Notification sent successfully", output)

    @patch('src.notifier.NTFY_TOPIC', 'test_topic')
    @patch('src.notifier.requests.post')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_ntfy_400_response(self, mock_stdout, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        send_notification("AAA", "BBB", "2026-09-02 12:45:36")
        
        output = mock_stdout.getvalue()
        self.assertIn("Notification configuration or request may be invalid", output)
        self.assertIn("Watcher will continue", output)

    @patch('src.notifier.NTFY_TOPIC', 'test_topic')
    @patch('src.notifier.requests.post')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_ntfy_500_response(self, mock_stdout, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        send_notification("AAA", "BBB", "2026-09-02 12:45:36")
        
        output = mock_stdout.getvalue()
        self.assertIn("Temporary notification failure", output)
        self.assertIn("Watcher will continue", output)

    @patch('src.notifier.NTFY_TOPIC', 'test_topic')
    @patch('src.notifier.requests.post')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_network_timeout(self, mock_stdout, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout()
        
        send_notification("AAA", "BBB", "2026-09-02 12:45:36")
        
        output = mock_stdout.getvalue()
        self.assertIn("Notification request timed out", output)
        self.assertIn("Watcher will continue", output)

    @patch('src.notifier.NTFY_TOPIC', '')
    @patch('src.notifier.requests.post')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_missing_topic(self, mock_stdout, mock_post):
        send_notification("AAA", "BBB", "2026-09-02 12:45:36")
        
        mock_post.assert_not_called()
        output = mock_stdout.getvalue()
        self.assertIn("NTFY_TOPIC is not configured", output)

    @patch('src.notifier.NTFY_TOPIC', 'test_topic')
    @patch('src.notifier.requests.post')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_notification_message_content(self, mock_stdout, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        send_notification("AAA", "BBB", "2026-09-02 12:45:36")
        
        args, kwargs = mock_post.call_args
        data = kwargs.get('data').decode('utf-8')
        
        self.assertIn("Old:\nAAA", data)
        self.assertIn("New:\nBBB", data)
        self.assertIn("2026-09-02 12:45:36", data)

    @patch('src.notifier.NTFY_TOPIC', 'test_topic')
    @patch('src.notifier.requests.post')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_empty_description_content(self, mock_stdout, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        send_notification("AAA", "", "2026-09-02 12:45:36")
        
        args, kwargs = mock_post.call_args
        data = kwargs.get('data').decode('utf-8')
        
        self.assertIn("Old:\nAAA", data)
        self.assertIn("New:\n[empty]", data)

if __name__ == '__main__':
    unittest.main()
