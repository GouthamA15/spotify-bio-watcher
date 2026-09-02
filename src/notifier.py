import requests
from typing import Optional
from .config import NTFY_TOPIC, NTFY_SERVER_URL, REQUEST_TIMEOUT_SECONDS

def send_notification(old_description: Optional[str], new_description: Optional[str], detected_at: str):
    """
    Sends a push notification to ntfy.sh with the old and new playlist description.
    """
    if not NTFY_TOPIC:
        print("[NOTIFIER] WARNING: NTFY_TOPIC is not configured.")
        print("[NOTIFIER] Change detected but notification was not sent.")
        return

    old_text = old_description if old_description else "[empty]"
    new_text = new_description if new_description else "[empty]"
    
    message = (
        "Playlist description changed.\n\n"
        f"Old:\n{old_text}\n\n"
        f"New:\n{new_text}\n\n"
        f"Detected:\n{detected_at}"
    )

    url = f"{NTFY_SERVER_URL}/{NTFY_TOPIC}"
    
    headers = {
        "Title": "Spotify Playlist Changed",
        "Priority": "high",
        "Tags": "musical_note"
    }
    
    try:
        response = requests.post(
            url, 
            data=message.encode('utf-8'), 
            headers=headers, 
            timeout=REQUEST_TIMEOUT_SECONDS
        )
        if 200 <= response.status_code < 300:
            print("[NOTIFIER] Notification sent successfully.")
        elif 400 <= response.status_code < 500:
            print(f"[NOTIFIER] ERROR: Notification configuration or request may be invalid ({response.status_code}).")
            print("[NOTIFIER] Watcher will continue.")
        elif response.status_code >= 500:
            print(f"[NOTIFIER] ERROR: Temporary notification failure ({response.status_code}).")
            print("[NOTIFIER] Watcher will continue.")
    except requests.exceptions.Timeout:
        print("[NOTIFIER] ERROR: Notification request timed out.")
        print("[NOTIFIER] Watcher will continue.")
    except requests.exceptions.RequestException:
        print("[NOTIFIER] ERROR: Failed to send notification (Network Error).")
        print("[NOTIFIER] Watcher will continue.")
