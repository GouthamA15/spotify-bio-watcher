import unittest
from unittest.mock import patch
import io
import sys

from src.watcher import run_watcher
from src.spotify import SpotifyRequestError, SpotifyAuthError

class TestWatcher(unittest.TestCase):
    
    @patch('src.watcher.validate_config')
    @patch('src.watcher.load_state')
    @patch('src.watcher.save_state')
    @patch('src.watcher.fetch_playlist_description')
    @patch('src.watcher.time.sleep')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_first_run_creates_baseline(self, mock_stdout, mock_sleep, mock_fetch, mock_save, mock_load, mock_validate):
        mock_load.return_value = None
        mock_fetch.side_effect = ["AAA", KeyboardInterrupt()]
        
        try:
            run_watcher()
        except KeyboardInterrupt:
            pass
            
        output = mock_stdout.getvalue()
        self.assertIn('No previous state found', output)
        self.assertIn('Initial description: "AAA"', output)
        self.assertNotIn('CHANGE DETECTED', output)
        mock_save.assert_called_once_with('6jiNsQnLOGTHZYw3dTd2nc', "AAA")

    @patch('src.watcher.validate_config')
    @patch('src.watcher.load_state')
    @patch('src.watcher.save_state')
    @patch('src.watcher.fetch_playlist_description')
    @patch('src.watcher.time.sleep')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_existing_state_loaded(self, mock_stdout, mock_sleep, mock_fetch, mock_save, mock_load, mock_validate):
        mock_load.return_value = {"playlist_id": "6jiNsQnLOGTHZYw3dTd2nc", "last_description": "AAA", "last_checked": "2026-09-02T12:00:00Z"}
        mock_fetch.side_effect = ["AAA", KeyboardInterrupt()]
        
        try:
            run_watcher()
        except KeyboardInterrupt:
            pass
            
        output = mock_stdout.getvalue()
        self.assertNotIn('No previous state found', output)
        self.assertIn('No change.', output)
        self.assertNotIn('CHANGE DETECTED', output)

    @patch('src.watcher.validate_config')
    @patch('src.watcher.load_state')
    @patch('src.watcher.save_state')
    @patch('src.watcher.fetch_playlist_description')
    @patch('src.watcher.time.sleep')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_description_changed(self, mock_stdout, mock_sleep, mock_fetch, mock_save, mock_load, mock_validate):
        mock_load.return_value = {"playlist_id": "6jiNsQnLOGTHZYw3dTd2nc", "last_description": "AAA", "last_checked": "2026-09-02T12:00:00Z"}
        mock_fetch.side_effect = ["BBB", KeyboardInterrupt()]
        
        try:
            run_watcher()
        except KeyboardInterrupt:
            pass
            
        output = mock_stdout.getvalue()
        self.assertIn('CHANGE DETECTED', output)
        self.assertIn('Old:\nAAA', output)
        self.assertIn('New:\nBBB', output)

    @patch('src.watcher.validate_config')
    @patch('src.watcher.load_state')
    @patch('src.watcher.save_state')
    @patch('src.watcher.fetch_playlist_description')
    @patch('src.watcher.time.sleep')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_empty_string_is_change(self, mock_stdout, mock_sleep, mock_fetch, mock_save, mock_load, mock_validate):
        mock_load.return_value = {"playlist_id": "6jiNsQnLOGTHZYw3dTd2nc", "last_description": "AAA", "last_checked": "2026-09-02T12:00:00Z"}
        mock_fetch.side_effect = ["", KeyboardInterrupt()]
        
        try:
            run_watcher()
        except KeyboardInterrupt:
            pass
            
        output = mock_stdout.getvalue()
        self.assertIn('CHANGE DETECTED', output)

    @patch('src.watcher.validate_config')
    @patch('src.watcher.load_state')
    @patch('src.watcher.save_state')
    @patch('src.watcher.fetch_playlist_description')
    @patch('src.watcher.time.sleep')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_null_description_preserves_state(self, mock_stdout, mock_sleep, mock_fetch, mock_save, mock_load, mock_validate):
        mock_load.return_value = {"playlist_id": "6jiNsQnLOGTHZYw3dTd2nc", "last_description": "AAA", "last_checked": "2026-09-02T12:00:00Z"}
        mock_fetch.side_effect = [None, KeyboardInterrupt()]
        
        try:
            run_watcher()
        except KeyboardInterrupt:
            pass
            
        output = mock_stdout.getvalue()
        self.assertIn('Spotify returned no description (null)', output)
        self.assertIn('Keeping previous description.', output)
        mock_save.assert_not_called()

    @patch('src.watcher.validate_config')
    @patch('src.watcher.load_state')
    @patch('src.watcher.save_state')
    @patch('src.watcher.fetch_playlist_description')
    @patch('src.watcher.time.sleep')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_api_failure_preserves_state(self, mock_stdout, mock_sleep, mock_fetch, mock_save, mock_load, mock_validate):
        mock_load.return_value = {"playlist_id": "6jiNsQnLOGTHZYw3dTd2nc", "last_description": "AAA", "last_checked": "2026-09-02T12:00:00Z"}
        mock_fetch.side_effect = [SpotifyRequestError("Spotify server error (500)"), KeyboardInterrupt()]
        
        try:
            run_watcher()
        except KeyboardInterrupt:
            pass
            
        output = mock_stdout.getvalue()
        self.assertIn('Spotify server error (500)', output)
        self.assertIn('Keeping previous state.', output)
        mock_save.assert_not_called()

if __name__ == '__main__':
    unittest.main()
