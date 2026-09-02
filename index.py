from pornhub_api import Client
from flask import Flask, send_from_directory, request, Response
import asyncio, os, re, requests

app    = Flask(__name__)
client = Client()
loop   = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

async def get_m3u8(video_id):
    video_object = await client.get_video(video_id)
    await video_object.load_fields("m3u8_base_url")
    lines = video_object.m3u8_base_url.strip().splitlines()
    return lines[2]

@app.route("/api/videos")
def start():
    video_id = request.args.get("url", "")
    if not video_id:
        return "missing url", 400
    try:
        m3u8_url = loop.run_until_complete(get_m3u8(video_id))
        return m3u8_url
    except Exception as e:
        return str(e), 500
@app.route("/proxy")
def proxy():
    video_url = request.args.get("video_url", "")
    if not video_url:
        return "missing video_url", 400

    m3u8_url = loop.run_until_complete(get_m3u8(video_url))
    return rewrite_m3u8(m3u8_url)

@app.route("/ts")
def ts():
    url = request.args.get("url", "")
    if not url:
        return "missing url", 400

    headers = {
        "Referer":    "https://www.pornhub.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Origin":     "https://www.pornhub.com",
    }

    r = requests.get(url, headers=headers, stream=True, timeout=10)
    content_type = r.headers.get("Content-Type", "")
    if "mpegurl" in content_type or url.split("?")[0].endswith(".m3u8"):
        return rewrite_m3u8(url)

    return Response(r.iter_content(chunk_size=1024*64), content_type="video/MP2T")

def rewrite_m3u8(m3u8_url):
    headers = {
        "Referer":    "https://www.pornhub.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Origin":     "https://www.pornhub.com",
    }
    r = requests.get(m3u8_url, headers=headers, timeout=10)
    base = m3u8_url.rsplit("/", 1)[0]

    lines = []
    for line in r.text.splitlines():
        if line and not line.startswith("#"):
            ts_url = line if line.startswith("http") else f"{base}/{line}"
            line = f"/ts?url={requests.utils.quote(ts_url, safe='')}"
        lines.append(line)

    return Response("\n".join(lines), content_type="application/vnd.apple.mpegurl")
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)