import os
import sys
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_PLAYLIST_ID = os.getenv("SPOTIFY_PLAYLIST_ID")
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", 60))
REQUEST_TIMEOUT_SECONDS = 10

NTFY_TOPIC = os.getenv("NTFY_TOPIC")
NTFY_SERVER_URL = os.getenv("NTFY_SERVER_URL", "https://ntfy.sh").rstrip("/")
NTFY_ACCESS_TOKEN = os.getenv("NTFY_ACCESS_TOKEN")

def validate_config():
    missing = []
    if not SPOTIFY_CLIENT_ID or "your_client_id" in SPOTIFY_CLIENT_ID:
        missing.append("SPOTIFY_CLIENT_ID")
    if not SPOTIFY_CLIENT_SECRET or "your_client_secret" in SPOTIFY_CLIENT_SECRET:
        missing.append("SPOTIFY_CLIENT_SECRET")
    if not SPOTIFY_PLAYLIST_ID:
        missing.append("SPOTIFY_PLAYLIST_ID")
    
    if missing:
        print(f"ERROR: Missing or invalid configuration for: {', '.join(missing)}")
        print("Please check your .env file.")
        sys.exit(1)
