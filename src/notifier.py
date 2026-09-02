import requests
import zoneinfo
from typing import Optional
from .config import NTFY_TOPIC, NTFY_SERVER_URL, REQUEST_TIMEOUT_SECONDS, NTFY_ACCESS_TOKEN
from .status import watcher_status
from datetime import datetime

def send_notification(old_description: Optional[str], new_description: Optional[str], detected_at: str):
    """
    Sends a push notification to ntfy.sh with the old and new playlist description.
    """
    attempt_time = datetime.now(zoneinfo.ZoneInfo('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S IST")
    watcher_status["last_notification_attempt"] = attempt_time

    if not NTFY_TOPIC:
        print("[NOTIFIER] WARNING: NTFY_TOPIC is not configured.")
        print("[NOTIFIER] Change detected but notification was not sent.")
        watcher_status["notification_failure_count"] += 1
        watcher_status["last_notification_error"] = "NTFY_TOPIC missing"
        return

    # Render env vars often have accidental whitespace/quotes
    safe_topic = NTFY_TOPIC.strip().strip("\"'")
    if safe_topic != NTFY_TOPIC:
        print("[NOTIFIER] WARNING: NTFY_TOPIC contained whitespace or quotes and was cleaned.")

    safe_url = NTFY_SERVER_URL.strip().strip("\"'")

    old_text = old_description if old_description else "[empty]"
    new_text = new_description if new_description else "[empty]"
    
    message = (
        "Playlist description changed.\n\n"
        f"Old:\n{old_text}\n\n"
        f"New:\n{new_text}\n\n"
        f"Detected:\n{detected_at}"
    )

    url = f"{safe_url}/{safe_topic}"
    
    print(f"[NOTIFIER] NTFY server configured: {safe_url}")
    print(f"[NOTIFIER] NTFY topic configured: True")
    
    # Ensure headers are safe ASCII strings, avoiding weird render encoding issues
    headers = {
        "Title": "Spotify Playlist Changed",
        "Priority": "high",
        "Tags": "musical_note"
    }

    if NTFY_ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {NTFY_ACCESS_TOKEN.strip()}"
        print("[NOTIFIER] Using authenticated request via NTFY_ACCESS_TOKEN.")

    
    try:
        print("[NOTIFIER] NTFY request starting...")
        response = requests.post(
            url, 
            data=message.encode('utf-8'), 
            headers=headers, 
            timeout=REQUEST_TIMEOUT_SECONDS
        )
        print(f"[NOTIFIER] NTFY response status: {response.status_code}")
        
        if 200 <= response.status_code < 300:
            print("[NOTIFIER] Notification sent successfully.")
            watcher_status["notification_success_count"] += 1
            watcher_status["last_notification_success"] = attempt_time
            watcher_status["last_notification_error"] = "None"
        elif 400 <= response.status_code < 500:
            err_text = response.text[:100]
            print(f"[NOTIFIER] ERROR: Notification configuration or request may be invalid ({response.status_code}). Response: {err_text}")
            print("[NOTIFIER] Watcher will continue.")
            watcher_status["notification_failure_count"] += 1
            watcher_status["last_notification_error"] = f"HTTP {response.status_code}: {err_text}"
        elif response.status_code >= 500:
            print(f"[NOTIFIER] ERROR: Temporary notification failure ({response.status_code}).")
            print("[NOTIFIER] Watcher will continue.")
            watcher_status["notification_failure_count"] += 1
            watcher_status["last_notification_error"] = f"HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        print("[NOTIFIER] ERROR: Notification request timed out.")
        print("[NOTIFIER] Watcher will continue.")
        watcher_status["notification_failure_count"] += 1
        watcher_status["last_notification_error"] = "Timeout"
    except requests.exceptions.RequestException as e:
        print(f"[NOTIFIER] ERROR: Failed to send notification (Network Error): {e}")
        print("[NOTIFIER] Watcher will continue.")
        watcher_status["notification_failure_count"] += 1
        watcher_status["last_notification_error"] = f"Network Error: {e}"
    except Exception as e:
        print(f"[NOTIFIER] UNEXPECTED ERROR: {e}")
        watcher_status["notification_failure_count"] += 1
        watcher_status["last_notification_error"] = f"Unexpected: {e}"
