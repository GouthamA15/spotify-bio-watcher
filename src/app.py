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
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; padding: 2rem; line-height: 1.6; max-width: 650px; margin: 0 auto; color: #333; }}
                h1 {{ color: #1DB954; display: flex; align-items: center; gap: 10px; }}
                .status-card {{ background: #f9f9f9; padding: 1.5rem; border-radius: 8px; border: 1px solid #e1e1e1; margin-bottom: 1.5rem; }}
                .status-card h3 {{ margin-top: 0; color: #555; border-bottom: 1px solid #ddd; padding-bottom: 0.5rem; }}
                .data-row {{ display: flex; justify-content: space-between; margin-bottom: 0.5rem; border-bottom: 1px dashed #eee; padding-bottom: 0.25rem; }}
                .data-row:last-child {{ border-bottom: none; }}
                .error-alert {{ background: #fff3f3; color: #d32f2f; padding: 1rem; border-left: 5px solid #d32f2f; border-radius: 4px; margin-top: 1rem; font-weight: 500; }}
            </style>
        </head>
        <body>
            <h1>Spotify Bio Watcher</h1>
            
            <div class="status-card">
                <h3>System Info</h3>
                <div class="data-row"><span>Status:</span> <strong>{is_running}</strong></div>
                <div class="data-row"><span>Playlist:</span> <strong>{SPOTIFY_PLAYLIST_ID}</strong></div>
                <div class="data-row"><span>Polling interval:</span> <strong>{POLL_INTERVAL_SECONDS} seconds</strong></div>
                <div class="data-row"><span>Started at:</span> <strong>{watcher_status["started_at"]}</strong></div>
            </div>

            <div class="status-card">
                <h3>Spotify Polling</h3>
                <div class="data-row"><span>Last check:</span> <strong>{watcher_status["last_check_at"]}</strong></div>
                <div class="data-row"><span>Last successful check:</span> <strong>{watcher_status["last_successful_check_at"]}</strong></div>
                <div class="data-row"><span>Successful checks:</span> <strong>{watcher_status["successful_checks"]}</strong></div>
                <div class="data-row"><span>Failed checks:</span> <strong>{watcher_status["failed_checks"]}</strong></div>
                <div class="data-row"><span>Last bio change:</span> <strong>{watcher_status["last_change_at"]}</strong></div>
                
                {f'<div class="error-alert">⚠️ Spotify API Error: {watcher_status["last_spotify_error"]}<br><small>Detected at: {watcher_status["last_spotify_error_time"]}</small></div>' if watcher_status["last_spotify_error"] != "None" else ""}
            </div>
            
            <div class="status-card">
                <h3>Notifications (NTFY)</h3>
                <div class="data-row"><span>Service:</span> <strong>{ntfy_status}</strong></div>
                <div class="data-row"><span>Last attempt:</span> <strong>{watcher_status["last_notification_attempt"]}</strong></div>
                <div class="data-row"><span>Last success:</span> <strong>{watcher_status["last_notification_success"]}</strong></div>
                <div class="data-row"><span>Success count:</span> <strong>{watcher_status["notification_success_count"]}</strong></div>
                <div class="data-row"><span>Failure count:</span> <strong>{watcher_status["notification_failure_count"]}</strong></div>
                
                {f'<div class="error-alert">⚠️ Notification Error: {watcher_status["last_notification_error"]}</div>' if watcher_status["last_notification_error"] != "None" else ""}
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
        "last_spotify_error": watcher_status["last_spotify_error"],
        "last_spotify_error_time": watcher_status["last_spotify_error_time"],
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
