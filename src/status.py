from datetime import datetime

# Shared in-memory status object
watcher_status = {
    "started_at": datetime.now().isoformat(),
    "last_check_at": "Never",
    "last_successful_check_at": "Never",
    "watcher_running": False,
    "successful_checks": 0,
    "failed_checks": 0,
    "last_change_at": "Never"
}
