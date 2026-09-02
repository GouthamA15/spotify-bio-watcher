import os
import json
import tempfile
import unittest
from unittest.mock import patch

from src.state import load_state, save_state

class TestState(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for state.json
        self.test_dir = tempfile.TemporaryDirectory()
        self.state_file = os.path.join(self.test_dir.name, "state.json")
        
        # Patch the STATE_FILE constant in state.py
        self.patcher = patch('src.state.STATE_FILE', self.state_file)
        self.patcher.start()
        
    def tearDown(self):
        self.patcher.stop()
        self.test_dir.cleanup()
        
    def test_missing_state(self):
        self.assertIsNone(load_state("playlist123"))
        
    def test_save_and_load_state(self):
        save_state("playlist123", "Hello World")
        
        state = load_state("playlist123")
        self.assertIsNotNone(state)
        self.assertEqual(state["playlist_id"], "playlist123")
        self.assertEqual(state["last_description"], "Hello World")
        self.assertIn("last_checked", state)
        
    def test_wrong_playlist_id(self):
        save_state("playlist123", "Hello World")
        # Trying to load with a different playlist ID should return None
        self.assertIsNone(load_state("other_playlist"))
        
    def test_corrupted_state(self):
        # Write corrupted JSON
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, "w") as f:
            f.write("{ invalid json")
            
        self.assertIsNone(load_state("playlist123"))

if __name__ == '__main__':
    unittest.main()
