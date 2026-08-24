from pornhub_api import Client ,  DownloadConfigHLS
from flask import Flask, send_from_directory , request
import asyncio
import os
import re
import subprocess

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, "Videos")
app = Flask(__name__)
client = Client()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def safe_filename(title):
    return re.sub(r'[\\/:*?"<>|]', "_", title)

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

async def DL_videos(video_id):
    video_object = await client.get_video(video_id)
    title = safe_filename(video_object.title)
    config = DownloadConfigHLS(quality="360p", path="./Videos")
    await video_object.download(config)

    raw  = os.path.join(BASE_DIR, "Videos", f"{title}.mp4")
    out  = os.path.join(BASE_DIR, "Videos", f"{title}_web.mp4")

    # ブラウザ再生できる形式に変換
    subprocess.run([
        "ffmpeg", "-i", raw,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-movflags", "+faststart",
        "-y", out
    ], check=True)
    os.remove(raw)
    os.rename(out, raw)

    return title


@app.route("/api/video")
def serve_video():
    filename = request.args.get("f", "")
    if not filename:
        return "missing filename", 400
    return send_from_directory(VIDEO_DIR, filename, conditional=True)

@app.route("/api/videos")
def main():
    video_id = request.args.get("url", "")
    if not video_id:
        return "missing url", 400
    video_title = loop.run_until_complete(DL_videos(video_id))
    return f"{video_title}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)