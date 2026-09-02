import time
import sys
from datetime import datetime
from .config import validate_config, POLL_INTERVAL_SECONDS, SPOTIFY_PLAYLIST_ID
from .spotify import fetch_playlist_description, SpotifyAuthError, SpotifyRequestError
from .state import load_state, save_state
from .notifier import send_notification
from .status import watcher_status

def get_full_time_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
            log(f"ERROR: {e}")
            if e.retry_after:
                log(f"Respecting rate limit. Waiting {e.retry_after} seconds...")
                time.sleep(e.retry_after)
            else:
                log("Keeping previous state.")
                time.sleep(POLL_INTERVAL_SECONDS)
                
        except Exception as e:
            watcher_status["failed_checks"] += 1
            log(f"UNEXPECTED ERROR: {e}")
            time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    try:
        run_watcher()
    except KeyboardInterrupt:
        print(f"\n[{get_full_time_str()}] Stopping Spotify Bio Watcher...")
        sys.exit(0)
