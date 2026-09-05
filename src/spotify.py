import base64
import requests
import time
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

class ClientPool:
    def __init__(self, client_ids_str: str, client_secrets_str: str):
        self.clients = []
        ids = [i.strip() for i in (client_ids_str or "").split(",") if i.strip()]
        secrets = [s.strip() for s in (client_secrets_str or "").split(",") if s.strip()]
        
        for cid, csec in zip(ids, secrets):
            self.clients.append({
                "id": cid,
                "secret": csec,
                "token": None,
                "penalty_until": 0
            })
        self.current_idx = 0

    def get_active_client(self):
        now = time.time()
        for i in range(len(self.clients)):
            idx = (self.current_idx + i) % len(self.clients)
            if self.clients[idx]["penalty_until"] <= now:
                self.current_idx = idx
                return self.clients[idx]
        return None

    def penalize_current(self, retry_after: int):
        self.clients[self.current_idx]["penalty_until"] = time.time() + retry_after
        self.clients[self.current_idx]["token"] = None

    def force_refresh_current(self):
        self.clients[self.current_idx]["token"] = None

pool = None

def init_pool():
    global pool
    if pool is None:
        pool = ClientPool(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)

def _get_access_token(client) -> str:
    if client["token"]:
        return client["token"]
        
    url = "https://accounts.spotify.com/api/token"
    auth_string = f"{client['id']}:{client['secret']}"
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
        client["token"] = token_data.get("access_token")
        return client["token"]
    except requests.exceptions.RequestException as e:
        raise SpotifyAuthError(f"Failed to authenticate with Spotify: {e}")

def force_refresh_token():
    init_pool()
    pool.force_refresh_current()

def fetch_playlist_description(is_retry=False) -> Optional[str]:
    init_pool()
    client = pool.get_active_client()
    
    if not client:
        now = time.time()
        min_penalty = min(c["penalty_until"] for c in pool.clients) - now
        raise SpotifyRequestError(f"All {len(pool.clients)} Spotify Client IDs are rate-limited.", retry_after=int(min_penalty) + 1)

    token = _get_access_token(client)
    
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
            pool.force_refresh_current()
            return fetch_playlist_description(is_retry=True)
        else:
            raise SpotifyRequestError("Authentication error (401). Retried and failed.")

    if response.status_code == 403:
        raise SpotifyRequestError("Spotify denied access (403).")

    if response.status_code == 404:
        raise SpotifyRequestError("Playlist not found (404).")

    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 5))
        pool.penalize_current(retry_after)
        print(f"[SPOTIFY] Client ID ending in ...{client['id'][-5:]} rate-limited. Rotating to next ID.")
        
        # We can safely retry once immediately with the next client
        if not is_retry:
            return fetch_playlist_description(is_retry=True)
        else:
            raise SpotifyRequestError("Rate limited (429) across multiple clients.")

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
