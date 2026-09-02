# Spotify Bio Watcher

A simple Python command-line application that monitors the description (bio) of a specific Spotify playlist. It polls the Spotify Web API every 60 seconds and notifies you via console and push notifications if the description has changed.

**Currently in Phase 4:** The application now features a minimal HTTP web server (FastAPI) allowing it to be deployed as a **Web Service on Render**. The internal Spotify watcher runs transparently in the background while the web server fulfills Render's port requirement.

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
   - **Important:** Use a random and unpredictable topic name.

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

## Running Locally

Once your environment is activated and `.env` is configured, start the application:

```powershell
python -m src.app
```
*Note: You can still run `python -m src.watcher` if you only want the watcher without the web server, but `src.app` is the recommended entry point to run both.*

Once running, you can access the minimal status pages:
- **Root Status Page**: `http://127.0.0.1:8000/`
- **Health Check**: `http://127.0.0.1:8000/health`
- **JSON Status**: `http://127.0.0.1:8000/status`

## Render Deployment

This application is ready to be deployed as a **Render Web Service** (Free tier compatible).

1. Connect your repository to Render.
2. Select **Web Service**.
3. Set the **Build Command**:
   ```bash
   pip install -r requirements.txt
   ```
4. Set the **Start Command**:
   ```bash
   python -m src.app
   ```
5. Add your Environment Variables in the Render dashboard (`SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_PLAYLIST_ID`, `NTFY_TOPIC`). Render will automatically provide the `PORT` variable.

Render will start the Web Service, detect the open port via the FastAPI server, and immediately begin running the Spotify Watcher loop in the background!

## Running Tests

You can verify the watcher's logic and the web server using pytest:

```powershell
python -m pytest
```
