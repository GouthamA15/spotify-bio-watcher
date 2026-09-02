import os
import sys
import threading
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

from .watcher import run_watcher, get_full_time_str
from .status import watcher_status
from .config import POLL_INTERVAL_SECONDS, SPOTIFY_PLAYLIST_ID, NTFY_TOPIC

app = FastAPI()

watcher_thread = threading.Thread(target=run_watcher, daemon=True)

@app.on_event("startup")
def startup_event():
    watcher_thread.start()

@app.get("/", response_class=HTMLResponse)
def read_root():
    is_running = "Running" if watcher_status["watcher_running"] else "Stopped"
    ntfy_status = "Configured" if NTFY_TOPIC else "Not configured"
    
    html_content = f"""
    <html>
        <head>
            <title>Spotify Bio Watcher</title>
            <style>
                body {{ font-family: sans-serif; padding: 2rem; line-height: 1.6; max-width: 600px; margin: 0 auto; }}
                h1 {{ color: #1DB954; }}
                .status {{ background: #f4f4f4; padding: 1rem; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>Spotify Bio Watcher</h1>
            
            <div class="status">
                <p><strong>Status:</strong> {is_running}</p>
                <p><strong>Playlist:</strong> Configured ({SPOTIFY_PLAYLIST_ID})</p>
                <p><strong>Polling interval:</strong> {POLL_INTERVAL_SECONDS} seconds</p>
                
                <hr>
                
                <p><strong>Started at:</strong> {watcher_status["started_at"]}</p>
                <p><strong>Last check:</strong> {watcher_status["last_check_at"]}</p>
                <p><strong>Last successful check:</strong> {watcher_status["last_successful_check_at"]}</p>
                <p><strong>Successful checks:</strong> {watcher_status["successful_checks"]}</p>
                <p><strong>Failed checks:</strong> {watcher_status["failed_checks"]}</p>
                <p><strong>Last change detected:</strong> {watcher_status["last_change_at"]}</p>
                
                <hr>
                
                <p><strong>Notification service:</strong> {ntfy_status}</p>
                <p><strong>Last notification attempt:</strong> {watcher_status["last_notification_attempt"]}</p>
                <p><strong>Last notification success:</strong> {watcher_status["last_notification_success"]}</p>
                <p><strong>Notification success count:</strong> {watcher_status["notification_success_count"]}</p>
                <p><strong>Notification failure count:</strong> {watcher_status["notification_failure_count"]}</p>
                <p><strong>Last notification error:</strong> {watcher_status["last_notification_error"]}</p>
            </div>
        </body>
    </html>
    """
    return html_content

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/status")
def status_check():
    return {
        "status": "running" if watcher_status["watcher_running"] else "stopped",
        "watcher": "running" if watcher_status["watcher_running"] else "stopped",
        "last_check": watcher_status["last_check_at"],
        "last_successful_check": watcher_status["last_successful_check_at"],
        "successful_checks": watcher_status["successful_checks"],
        "failed_checks": watcher_status["failed_checks"],
        "last_change": watcher_status["last_change_at"],
        "last_notification_attempt": watcher_status["last_notification_attempt"],
        "last_notification_success": watcher_status["last_notification_success"],
        "notification_success_count": watcher_status["notification_success_count"],
        "notification_failure_count": watcher_status["notification_failure_count"],
        "last_notification_error": watcher_status["last_notification_error"]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
    except KeyboardInterrupt:
        print(f"\n[{get_full_time_str()}] Stopping Web Service...")
        sys.exit(0)
