import os
import sys
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_PLAYLIST_ID = os.getenv("SPOTIFY_PLAYLIST_ID")
POLL_INTERVAL_SECONDS = 60
REQUEST_TIMEOUT_SECONDS = 10

def validate_config():
    missing = []
    if not SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_ID == "your_client_id":
        missing.append("SPOTIFY_CLIENT_ID")
    if not SPOTIFY_CLIENT_SECRET or SPOTIFY_CLIENT_SECRET == "your_client_secret":
        missing.append("SPOTIFY_CLIENT_SECRET")
    if not SPOTIFY_PLAYLIST_ID:
        missing.append("SPOTIFY_PLAYLIST_ID")
    
    if missing:
        print(f"ERROR: Missing or invalid configuration for: {', '.join(missing)}")
        print("Please check your .env file.")
        sys.exit(1)
