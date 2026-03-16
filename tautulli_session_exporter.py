
import requests
from flask import Flask, Response
import os

TAUTULLI_URL = os.environ.get("TAUTULLI_URL", "http://localhost:8181")
TAUTULLI_API_KEY = os.environ.get("TAUTULLI_API_KEY")

app = Flask(__name__)

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
        user = s.get("user", "unknown")
        client = s.get("player", "unknown")
        decision = s.get("transcode_decision", "directplay")
        bitrate = s.get("bitrate", 0)
        resolution = s.get("video_resolution", "unknown")

        lines.append(
            f'plex_stream_active{{user="{user}",client="{client}",decision="{decision}",resolution="{resolution}"}} 1'
        )

        lines.append(
            f'plex_stream_bitrate{{user="{user}",resolution="{resolution}"}} {bitrate}'
        )

    return Response("\n".join(lines), mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9594)
