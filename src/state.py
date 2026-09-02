import json
import os
import tempfile
from datetime import datetime, timezone

STATE_FILE = os.path.join("data", "state.json")

def load_state(expected_playlist_id: str):
    """
    Loads state from state.json.
    Returns None if missing, corrupted, or if the playlist ID doesn't match.
    """
    if not os.path.exists(STATE_FILE):
        return None
        
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
            
        if not isinstance(state, dict):
            print("[STATE] WARNING: state.json is invalid (not a JSON object).")
            return None
            
        if state.get("playlist_id") != expected_playlist_id:
            print(f"[STATE] WARNING: state.json belongs to another playlist. Expected {expected_playlist_id}.")
            return None
            
        return state
    except (json.JSONDecodeError, IOError) as e:
        print(f"[STATE] WARNING: state.json is invalid or unreadable: {e}")
        return None

def save_state(playlist_id: str, description: str):
    """
    Saves the description and timestamp atomically to state.json.
    """
    state = {
        "playlist_id": playlist_id,
        "last_description": description,
        "last_checked": datetime.now(timezone.utc).isoformat()
    }
    
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    
    try:
        fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(STATE_FILE), text=True)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)
        
        os.replace(temp_path, STATE_FILE)
    except IOError as e:
        print(f"[STATE] ERROR: Failed to write state.json: {e}")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
