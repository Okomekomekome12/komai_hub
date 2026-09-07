from pornhub_api import Client
from flask import Flask, send_from_directory, request, Response
import asyncio, os, requests

app    = Flask(__name__)
client = Client()
loop   = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

HEADERS = {
    "Referer":    "https://www.pornhub.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
}

async def get_m3u8(video_id):
    video_object = await client.get_video(video_id)
    await video_object.load_fields("m3u8_base_url")
    lines = [l for l in video_object.m3u8_base_url.strip().splitlines() if l and not l.startswith("#")]
    return lines[1]  # 240p

def fetch_m3u8(url):
    r    = requests.get(url, headers=HEADERS, timeout=15)
    base = url.rsplit("/", 1)[0]
    lines = []
    for line in r.text.splitlines():
        if line and not line.startswith("#"):
            if not line.startswith("http"):
                line = f"{base}/{line}"
            line = f"/ts?url={requests.utils.quote(line, safe='')}"
        lines.append(line)
    return Response("\n".join(lines), content_type="application/vnd.apple.mpegurl")

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/videos")
def start():
    video_id = request.args.get("url", "")
    if not video_id:
        return "missing url", 400
    try:
        m3u8_url = loop.run_until_complete(get_m3u8(video_id))
        return f"/m3u8?url={requests.utils.quote(m3u8_url, safe='')}"
    except Exception as e:
        return str(e), 500

@app.route("/m3u8")
def m3u8():
    return fetch_m3u8(request.args.get("url", ""))

@app.route("/ts")
def ts():
    url = request.args.get("url", "")
    if url.split("?")[0].endswith(".m3u8"):
        return fetch_m3u8(url)
    r = requests.get(url, headers=HEADERS, stream=True, timeout=30)
    return Response(r.iter_content(chunk_size=1024*128), content_type="video/MP2T")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)