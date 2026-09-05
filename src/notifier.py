import requests
import zoneinfo
from typing import Optional
from .config import NTFY_TOPIC, NTFY_SERVER_URL, REQUEST_TIMEOUT_SECONDS, NTFY_ACCESS_TOKEN
from .status import watcher_status
from datetime import datetime

def get_ist_time_str() -> str:
    return datetime.now(zoneinfo.ZoneInfo('Asia/Kolkata')).strftime("%Y-%m-%d %I:%M:%S %p IST")

def _do_ntfy_post(message: str, headers: dict):
    """Helper to perform the HTTP POST to ntfy and track status"""
    attempt_time = get_ist_time_str()
    watcher_status["last_notification_attempt"] = attempt_time

    if not NTFY_TOPIC:
        print("[NOTIFIER] WARNING: NTFY_TOPIC is not configured.")
        watcher_status["notification_failure_count"] += 1
        watcher_status["last_notification_error"] = "NTFY_TOPIC missing"
        return

    safe_topic = NTFY_TOPIC.strip().strip("\"'")
    safe_url = NTFY_SERVER_URL.strip().strip("\"'")
    url = f"{safe_url}/{safe_topic}"

    if NTFY_ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {NTFY_ACCESS_TOKEN.strip()}"

    try:
        response = requests.post(
            url, 
            data=message.encode('utf-8'), 
            headers=headers, 
            timeout=REQUEST_TIMEOUT_SECONDS
        )
        if 200 <= response.status_code < 300:
            print("[NOTIFIER] Notification sent successfully.")
            watcher_status["notification_success_count"] += 1
            watcher_status["last_notification_success"] = attempt_time
            watcher_status["last_notification_error"] = "None"
        else:
            err_text = response.text[:100]
            print(f"[NOTIFIER] ERROR: Notification failure ({response.status_code}). Response: {err_text}")
            watcher_status["notification_failure_count"] += 1
            watcher_status["last_notification_error"] = f"HTTP {response.status_code}: {err_text}"
    except Exception as e:
        print(f"[NOTIFIER] ERROR: Failed to send notification: {e}")
        watcher_status["notification_failure_count"] += 1
        watcher_status["last_notification_error"] = f"Error: {e}"

def send_notification(old_description: Optional[str], new_description: Optional[str], detected_at: str):
    """
    Sends a push notification to ntfy.sh with the old and new playlist description.
    """
    old_text = old_description if old_description else "[empty]"
    new_text = new_description if new_description else "[empty]"
    
    message = (
        "Playlist description changed.\n\n"
        f"Old:\n{old_text}\n\n"
        f"New:\n{new_text}\n\n"
        f"Detected:\n{detected_at}"
    )
    
    headers = {
        "Title": "Spotify Playlist Changed",
        "Priority": "high",
        "Tags": "musical_note"
    }
    _do_ntfy_post(message, headers)

def send_error_notification(error_message: str, detected_at: str):
    """
    Sends a push notification to ntfy.sh when the Spotify API crashes or is banned.
    """
    message = (
        "Spotify Watcher Error!\n\n"
        f"Error:\n{error_message}\n\n"
        f"Detected:\n{detected_at}"
    )
    
    headers = {
        "Title": "Spotify Watcher Down",
        "Priority": "urgent",
        "Tags": "warning"
    }
    _do_ntfy_post(message, headers)
