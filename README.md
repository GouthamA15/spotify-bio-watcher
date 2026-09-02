# Spotify Bio Watcher

A simple Python command-line application that monitors the description (bio) of a specific Spotify playlist. It polls the Spotify Web API every 60 seconds and notifies you via console and push notifications if the description has changed.

**Currently in Phase 3:** Added push notifications to your mobile phone via [ntfy.sh](https://ntfy.sh).

## Requirements

- Python 3.11+ (or 3.10+)
- Windows PowerShell (or any standard terminal)
- **Ntfy app** (available on iOS and Android)

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
   - Note down the `Client ID` and `Client Secret`.

2. **Set up Ntfy**:
   - Download the **ntfy** app on your phone.
   - Subscribe to a new topic.
   - **Important:** Use a random and unpredictable topic name (e.g., `playlist-watch-84hf9qj`). Do not use common names like `spotify`, as public ntfy topics can be viewed by anyone who guesses the name.

3. **Configure Environment Variables**:
   - Rename `.env.example` to `.env`.
   - Open `.env` and fill in your actual credentials and your chosen secret topic:
     ```env
     SPOTIFY_CLIENT_ID=your_client_id
     SPOTIFY_CLIENT_SECRET=your_client_secret
     SPOTIFY_PLAYLIST_ID=6jiNsQnLOGTHZYw3dTd2nc
     
     NTFY_SERVER_URL=https://ntfy.sh
     NTFY_TOPIC=your_private_random_topic
     ```

   > **Warning**: Never commit your `.env` file to version control.

## Running the Watcher

Once your environment is activated and `.env` is configured, start the watcher:

```powershell
python -m src.watcher
```

## Running Tests

You can verify the watcher's logic and notification functionality using pytest:

```powershell
python -m pytest
```

## Behavior & Error Handling

- **Persistent State:** It stores the last valid state in `data/state.json`. On start, it resumes exactly where it left off.
- **Null Descriptions:** If Spotify returns `null`, the watcher ignores it and retains the previous valid description. However, if Spotify returns an explicit empty string `""`, it registers as a change and you are notified.
- **Notification Failure:** If the watcher fails to send a push notification (due to a network error or ntfy server downtime), it will simply log the error and **keep running**. The state will still be updated, so it won't repeatedly spam notifications every 60 seconds if ntfy goes down.
- **Spotify API Errors:** Tokens are refreshed automatically on `401`. Rate limits (`429`) correctly trigger a pause, and `5xx` errors keep the application alive to retry later.
