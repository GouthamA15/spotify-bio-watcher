from datetime import datetime
import zoneinfo

def get_ist_time_str() -> str:
    return datetime.now(zoneinfo.ZoneInfo('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S IST")

# Shared in-memory status object
watcher_status = {
    "started_at": get_ist_time_str(),
    "last_check_at": "Never",
    "last_successful_check_at": "Never",
    "watcher_running": False,
    "successful_checks": 0,
    "failed_checks": 0,
    "last_change_at": "Never",
    "last_notification_attempt": "Never",
    "last_notification_success": "Never",
    "notification_success_count": 0,
    "notification_failure_count": 0,
    "last_notification_error": "None"
}
