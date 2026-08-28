from pornhub_api import Client, DownloadConfigHLS
from flask import Flask, send_from_directory, request
import asyncio
import os
import re
import subprocess
import time

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, "Videos")

app = Flask(__name__)
client = Client()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def safe_filename(title):
    return re.sub(r"""[\\/:*?"<>|']""", "_", title)

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/video/<path:filename>")
def serve_video(filename):
    return send_from_directory(VIDEO_DIR, filename, conditional=True)

"""
async def DL_videos(video_id):
    video_object = await client.get_video(video_id)
    title = safe_filename(video_object.title)

    tmp   = os.path.join(VIDEO_DIR, "_tmp.mp4")
    final = os.path.join(VIDEO_DIR, f"{title}.mp4")

    for f in [tmp, final]:
        if os.path.exists(f): os.remove(f)

    os.makedirs(VIDEO_DIR, exist_ok=True)
    config = DownloadConfigHLS(quality="360p", path=VIDEO_DIR)
    await video_object.download(config)

    raw = max(
        [os.path.join(VIDEO_DIR, f) for f in os.listdir(VIDEO_DIR) if f.endswith(".mp4")],
        key=os.path.getctime
    )

    subprocess.run(["ffmpeg", "-i", raw, "-c", "copy", "-movflags", "+faststart", "-y", tmp], check=True)

    # Windowsのファイルロック対策
    time.sleep(0.5)
    try:
        os.remove(raw)
    except PermissionError:
        pass

    os.replace(tmp, final)
    return title"""


async def DL_videos(video_id):
    video_object = await client.get_video(video_id)
    title = safe_filename(video_object.title)
    tmp   = os.path.join(VIDEO_DIR, "_tmp.mp4")
    final = os.path.join(VIDEO_DIR, f"{title}.mp4")

    for f in [tmp, final]:
        if os.path.exists(f): os.remove(f)

    os.makedirs(VIDEO_DIR, exist_ok=True)
    config = DownloadConfigHLS(quality="360p", path=VIDEO_DIR)
    await video_object.download(config)

    raw = max(
        [os.path.join(VIDEO_DIR, f) for f in os.listdir(VIDEO_DIR) if f.endswith(".mp4")],
        key=os.path.getctime
    )

    subprocess.run(["ffmpeg", "-i", raw, "-c", "copy", "-movflags", "+faststart", "-y", tmp], check=True)
    os.remove(raw)
    os.replace(tmp, final)
    return title

@app.route("/api/videos")
def main():
    video_id = request.args.get("url", "")
    if not video_id:
        return "missing url", 400
    try:
        video_title = loop.run_until_complete(DL_videos(video_id))
        return video_title
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)