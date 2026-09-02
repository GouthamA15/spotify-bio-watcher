# Spotify Bio Watcher

A simple Python command-line application that monitors the description (bio) of a specific Spotify playlist. It polls the Spotify Web API every 60 seconds and notifies you in the console if the description has changed.

## Requirements

- Python 3.11+ (or 3.10+)
- Windows PowerShell (or any standard terminal)

## Setup

1. **Clone or download this repository** to your local machine.

2. **Create a virtual environment**:
   ```powershell
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

## Configuration

1. **Create Spotify Developer Credentials**:
   - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
   - Log in and create a new App.
   - Note down the `Client ID` and `Client Secret` from your App's settings.

2. **Configure Environment Variables**:
   - Rename `.env.example` to `.env` (or copy it):
     ```powershell
     cp .env.example .env
     ```
   - Open `.env` and fill in your actual `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`.
   - The `SPOTIFY_PLAYLIST_ID` is pre-configured to `6jiNsQnLOGTHZYw3dTd2nc`.

   > **Warning**: Never commit your `.env` file to version control. It is listed in `.gitignore` by default to prevent accidental sharing of your secrets.

## Running the Watcher

Once your environment is activated and `.env` is configured, start the watcher:

```powershell
python -m src.watcher
```

## Expected Output

On startup, it fetches the baseline description:
```text
[2026-09-02 20:00:00] Initial description: "Some description here"
[2026-09-02 20:00:00] Watching for changes every 60 seconds...
```

Every 60 seconds, it checks for changes:
```text
[2026-09-02 20:01:00] Checking playlist...
[2026-09-02 20:01:00] No change.
```

If a change is detected:
```text
[2026-09-02 20:02:00] Checking playlist...

==================================================
CHANGE DETECTED
==================================================

Old:
Some description here

New:
New description!

Detected:
2026-09-02 20:02:00

==================================================
```

Press `Ctrl+C` to gracefully shut down the watcher.

## Limitations (Phase 1)
- Currently polls every 60 seconds.
- State is kept in memory. When the application restarts, it will fetch the current description as the new baseline (it won't remember the previous description from a previous run).
- Only outputs changes to the console (no push notifications, emails, or webhooks yet).
- Only supports monitoring one specific playlist.
