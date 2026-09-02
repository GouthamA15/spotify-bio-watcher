import time
import sys
from datetime import datetime
from .config import validate_config, POLL_INTERVAL_SECONDS
from .spotify import fetch_playlist_description, SpotifyAuthError, SpotifyRequestError

def get_current_time_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(message: str):
    print(f"[{get_current_time_str()}] {message}")

def run_watcher():
    validate_config()
    
    previous_description = None
    is_first_run = True
    
    while True:
        try:
            if not is_first_run:
                log("Checking playlist...")

            current_description = fetch_playlist_description()
            
            if is_first_run:
                previous_description = current_description
                log(f'Initial description: "{current_description}"')
                log(f"Watching for changes every {POLL_INTERVAL_SECONDS} seconds...")
                is_first_run = False
            else:
                if current_description == previous_description:
                    log("No change.")
                else:
                    print("\n==================================================")
                    print("CHANGE DETECTED")
                    print("==================================================\n")
                    print("Old:")
                    print(previous_description)
                    print("\nNew:")
                    print(current_description)
                    print(f"\nDetected:\n{get_current_time_str()}")
                    print("\n==================================================\n")
                    
                    previous_description = current_description
            
            time.sleep(POLL_INTERVAL_SECONDS)
            
        except SpotifyAuthError as e:
            log(f"ERROR: {e}")
            log("Please check your Spotify credentials. Retrying in 60 seconds...")
            time.sleep(60)
            
        except SpotifyRequestError as e:
            log(f"ERROR: {e}")
            if e.retry_after:
                log(f"Respecting rate limit. Waiting {e.retry_after} seconds...")
                time.sleep(e.retry_after)
            else:
                log("Keeping previous description and retrying later.")
                time.sleep(POLL_INTERVAL_SECONDS)
                
        except Exception as e:
            log(f"UNEXPECTED ERROR: {e}")
            time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    try:
        run_watcher()
    except KeyboardInterrupt:
        print("\nStopping Spotify Bio Watcher...")
        sys.exit(0)
