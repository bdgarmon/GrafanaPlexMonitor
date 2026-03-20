import requests
from flask import Flask, Response
import os

TAUTULLI_URL = os.environ.get("TAUTULLI_URL", "http://localhost:8181")
TAUTULLI_API_KEY = os.environ.get("TAUTULLI_API_KEY")

app = Flask(__name__)

def clean(val):
    return str(val).replace('"', '').replace('\n', ' ').strip()

def get_activity():
    url = f"{TAUTULLI_URL}/api/v2"
    params = {
        "apikey": TAUTULLI_API_KEY,
        "cmd": "get_activity"
    }
    r = requests.get(url, params=params, timeout=5)
    return r.json()

@app.route("/metrics")
def metrics():
    data = get_activity()
    lines = []

    sessions = data.get("response", {}).get("data", {}).get("sessions", [])
    lines.append(f"plex_stream_sessions {len(sessions)}")

    for s in sessions:
        user = clean(s.get("user", "unknown"))
        client = clean(s.get("player", "unknown"))
        decision = clean(s.get("transcode_decision", "directplay"))
        bitrate = s.get("bitrate", 0)
        resolution = clean(s.get("video_resolution", "unknown"))
        media_type = clean(s.get("media_type", "unknown"))

        # Build a better title (handles TV vs Movies)
        if media_type == "episode":
            show = clean(s.get("grandparent_title", ""))
            episode = clean(s.get("title", ""))
            title = f"{show} - {episode}".strip(" -")
        else:
            title = clean(s.get("full_title") or s.get("title") or "unknown")

        # Active stream metric (unchanged)
        lines.append(
            f'plex_stream_active{{user="{user}",client="{client}",decision="{decision}",resolution="{resolution}"}} 1'
        )

        # Enhanced bitrate metric (NEW LABELS ADDED)
        lines.append(
            f'plex_stream_bitrate{{user="{user}",title="{title}",media_type="{media_type}",resolution="{resolution}",decision="{decision}"}} {bitrate}'
        )

    return Response("\n".join(lines), mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9594)
