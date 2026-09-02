import base64
import requests
from typing import Optional
from .config import (
    SPOTIFY_CLIENT_ID, 
    SPOTIFY_CLIENT_SECRET, 
    SPOTIFY_PLAYLIST_ID, 
    REQUEST_TIMEOUT_SECONDS
)

class SpotifyAuthError(Exception):
    pass

class SpotifyRequestError(Exception):
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after

_cached_token = None

def _get_access_token() -> str:
    """
    Fetch an access token using the Client Credentials flow.
    Caches token in memory.
    """
    global _cached_token
    if _cached_token:
        return _cached_token
        
    url = "https://accounts.spotify.com/api/token"
    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_base64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }

    try:
        response = requests.post(url, headers=headers, data=data, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        token_data = response.json()
        _cached_token = token_data.get("access_token")
        return _cached_token
    except requests.exceptions.RequestException as e:
        raise SpotifyAuthError(f"Failed to authenticate with Spotify: {e}")

def force_refresh_token():
    global _cached_token
    _cached_token = None

def fetch_playlist_description(is_retry=False) -> Optional[str]:
    """
    Fetch the playlist description using the Spotify Web API.
    Handles HTTP status codes as requested.
    Returns the description as a string, or None if it's explicitly null.
    """
    token = _get_access_token()
    
    url = f"https://api.spotify.com/v1/playlists/{SPOTIFY_PLAYLIST_ID}?fields=description"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.exceptions.Timeout:
        raise SpotifyRequestError("Spotify request timed out.")
    except requests.exceptions.RequestException as e:
        raise SpotifyRequestError(f"Spotify request failed (network error): {e}")
        
    if response.status_code == 401:
        if not is_retry:
            force_refresh_token()
            return fetch_playlist_description(is_retry=True)
        else:
            raise SpotifyRequestError("Authentication error (401). Retried and failed.")

    if response.status_code == 403:
        raise SpotifyRequestError("Spotify denied access (403).")

    if response.status_code == 404:
        raise SpotifyRequestError("Playlist not found (404).")

    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 5))
        raise SpotifyRequestError("Rate limited (429).", retry_after=retry_after)

    if response.status_code >= 500:
        raise SpotifyRequestError(f"Spotify server error ({response.status_code}).")
    
    try:
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SpotifyRequestError(f"Spotify request failed ({response.status_code}).")

    try:
        data = response.json()
    except ValueError:
        raise SpotifyRequestError("Invalid JSON in Spotify response")

    if "description" not in data:
        raise SpotifyRequestError("Missing 'description' field in response")

    return data.get("description")
