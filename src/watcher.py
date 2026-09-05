import time
import sys
import zoneinfo
import json
import os
from datetime import datetime
from .config import validate_config, POLL_INTERVAL_SECONDS, SPOTIFY_PLAYLIST_ID
from .spotify import fetch_playlist_description, SpotifyAuthError, SpotifyRequestError
from .state import load_state, save_state
from .notifier import send_notification, send_error_notification
from .status import watcher_status

def get_full_time_str() -> str:
    return datetime.now(zoneinfo.ZoneInfo('Asia/Kolkata')).strftime("%Y-%m-%d %I:%M:%S %p IST")

def log(message: str):
    print(f"[{get_full_time_str()}] {message}")

def run_watcher():
    validate_config()
    
    watcher_status["watcher_running"] = True
    state = load_state(SPOTIFY_PLAYLIST_ID)
    
    if state is None:
        log("No previous state found. Creating a fresh baseline from Spotify.")
        is_first_run = True
        previous_description = None
    else:
        previous_description = state.get("last_description")
        is_first_run = False
        log("Watching for changes every 60 seconds...")

    while True:
        try:
            if not is_first_run:
                log("Checking playlist...")

            watcher_status["last_check_at"] = get_full_time_str()
            current_description = fetch_playlist_description()
            
            watcher_status["last_successful_check_at"] = get_full_time_str()
            watcher_status["successful_checks"] += 1
            watcher_status["last_spotify_error"] = "None"
            watcher_status["spotify_error_notified"] = False
            
            if current_description is None:
                log("WARNING: Spotify returned no description (null).")
                log("Keeping previous description.")
                time.sleep(POLL_INTERVAL_SECONDS)
                continue
                
            if is_first_run:
                previous_description = current_description
                log(f'Initial description: "{current_description}"')
                log("Baseline saved.")
                log(f"Watching for changes every {POLL_INTERVAL_SECONDS} seconds...")
                save_state(SPOTIFY_PLAYLIST_ID, current_description)
                is_first_run = False
            else:
                if current_description == previous_description:
                    log("No change.")
                    save_state(SPOTIFY_PLAYLIST_ID, current_description)
                else:
                    detection_time = get_full_time_str()
                    watcher_status["last_change_at"] = detection_time
                    
                    print("\n==================================================")
                    print("CHANGE DETECTED")
                    print("==================================================\n")
                    print("Old:")
                    print(previous_description)
                    print("\nNew:")
                    print(current_description)
                    print(f"\nDetected:\n{detection_time}")
                    print("\n==================================================\n")
                    
                    log("Sending notification...")
                    send_notification(previous_description, current_description, detection_time)
                    
                    previous_description = current_description
                    save_state(SPOTIFY_PLAYLIST_ID, current_description)
            
            time.sleep(POLL_INTERVAL_SECONDS)
            
        except SpotifyAuthError as e:
            watcher_status["failed_checks"] += 1
            log(f"ERROR: {e}")
            log("Please check your Spotify credentials. Retrying in 60 seconds...")
            time.sleep(60)
            
        except SpotifyRequestError as e:
            watcher_status["failed_checks"] += 1
            watcher_status["last_spotify_error"] = str(e)
            watcher_status["last_spotify_error_time"] = get_full_time_str()
            log(f"ERROR: {e}")
            
            if not watcher_status.get("spotify_error_notified", False):
                log("Sending error notification to ntfy...")
                send_error_notification(str(e), get_full_time_str())
                watcher_status["spotify_error_notified"] = True

            if e.retry_after:
                log(f"Respecting rate limit. Waiting {e.retry_after} seconds...")
                watcher_status["last_notification_error"] = f"Spotify Penalty: {e.retry_after}s"
                time.sleep(e.retry_after)
                watcher_status["last_notification_error"] = "None"
            else:
                log("Keeping previous state.")
                time.sleep(POLL_INTERVAL_SECONDS)
                
        except Exception as e:
            watcher_status["failed_checks"] += 1
            watcher_status["last_spotify_error"] = f"Unexpected: {e}"
            watcher_status["last_spotify_error_time"] = get_full_time_str()
            log(f"UNEXPECTED ERROR: {e}")
            
            if not watcher_status.get("spotify_error_notified", False):
                log("Sending error notification to ntfy...")
                send_error_notification(f"Unexpected: {e}", get_full_time_str())
                watcher_status["spotify_error_notified"] = True

            time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    try:
        run_watcher()
    except KeyboardInterrupt:
        print(f"\n[{get_full_time_str()}] Stopping Spotify Bio Watcher...")
        sys.exit(0)
