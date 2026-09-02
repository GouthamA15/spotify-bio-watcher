import unittest
from unittest.mock import patch, MagicMock
import sys
import io

from src.watcher import run_watcher
from src.spotify import SpotifyRequestError, SpotifyAuthError

class TestWatcher(unittest.TestCase):
    @patch('src.watcher.validate_config')
    @patch('src.watcher.fetch_playlist_description')
    @patch('src.watcher.time.sleep')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_watcher_flow(self, mock_stdout, mock_sleep, mock_fetch, mock_validate):
        # We want the loop to run a few times and then raise KeyboardInterrupt to exit
        
        # Responses for fetch_playlist_description:
        # 1. "AAA" (Initial)
        # 2. "AAA" (No change)
        # 3. "BBB" (Change detected)
        # 4. KeyboardInterrupt (Exit)
        
        mock_fetch.side_effect = [
            "AAA",
            "AAA",
            "BBB",
            KeyboardInterrupt()
        ]
        
        try:
            run_watcher()
        except KeyboardInterrupt:
            pass
            
        output = mock_stdout.getvalue()
        
        # TEST 4: First successful value becomes the baseline.
        self.assertIn('Initial description: "AAA"', output)
        
        # TEST 5: Same value does NOT produce CHANGE DETECTED.
        self.assertIn('No change.', output)
        
        # TEST 6: Changed value produces CHANGE DETECTED.
        self.assertIn('CHANGE DETECTED', output)
        self.assertIn('Old:\nAAA', output)
        self.assertIn('New:\nBBB', output)

    @patch('src.watcher.validate_config')
    @patch('src.watcher.fetch_playlist_description')
    @patch('src.watcher.time.sleep')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_watcher_error_recovery(self, mock_stdout, mock_sleep, mock_fetch, mock_validate):
        # Responses:
        # 1. "AAA" (Initial)
        # 2. SpotifyRequestError (Network failure)
        # 3. "BBB" (Recovers and gets new description)
        # 4. KeyboardInterrupt
        
        mock_fetch.side_effect = [
            "AAA",
            SpotifyRequestError("Temporary network error"),
            "BBB",
            KeyboardInterrupt()
        ]
        
        try:
            run_watcher()
        except KeyboardInterrupt:
            pass
            
        output = mock_stdout.getvalue()
        
        self.assertIn('Initial description: "AAA"', output)
        self.assertIn('ERROR: Temporary network error', output)
        self.assertIn('Keeping previous description and retrying later.', output)
        self.assertIn('CHANGE DETECTED', output)
        self.assertIn('New:\nBBB', output)

if __name__ == '__main__':
    unittest.main()
