from pornhub_api import Client
from flask import Flask, send_from_directory, request, Response
import asyncio, os, requests, time

app    = Flask(__name__)
client = Client()
loop   = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

HEADERS = {
    "Referer":    "https://www.pornhub.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
}

def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"]  = "*"
    resp.headers["Access-Control-Expose-Headers"] = "Content-Length, Content-Range"
    return resp

async def get_m3u8(url):
    v = await client.get_video(url)
    await v.load_fields("m3u8_base_url")
    lines = [l for l in v.m3u8_base_url.strip().splitlines() if l and not l.startswith("#")]
    return lines[-1]

def proxy_m3u8(url):
    r    = requests.get(url, headers=HEADERS, timeout=15)
    base = url.rsplit("/", 1)[0]
    out  = []
    for line in r.text.splitlines():
        if line and not line.startswith("#"):
            seg = line if line.startswith("http") else f"{base}/{line}"
            line = f"/ts?url={requests.utils.quote(seg, safe='')}"
        out.append(line)
    return "\n".join(out)

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/videos")
def api():
    url = request.args.get("url", "")
    if not url:
        return "missing url", 400
    try:
        m3u8 = loop.run_until_complete(get_m3u8(url))
        return add_cors(Response(f"/m3u8?url={requests.utils.quote(m3u8, safe='')}"))
    except Exception as e:
        return str(e), 500

@app.route("/m3u8")
def m3u8():
    url = request.args.get("url", "")
    try:
        resp = Response(proxy_m3u8(url), content_type="application/vnd.apple.mpegurl")
        return add_cors(resp)
    except Exception as e:
        return str(e), 500

@app.route("/ts")
def ts():
    url = request.args.get("url", "")
    if url.endswith(".m3u8"):
        return m3u8()
    try:
        r    = requests.get(url, headers={**HEADERS, "Range": request.headers.get("Range", "")}, stream=True, timeout=30)
        ct   = "video/mp4" if url.endswith((".m4s", ".mp4")) else "video/MP2T"
        resp = Response(r.iter_content(128 * 1024), status=r.status_code, content_type=ct)
        resp.headers["Accept-Ranges"] = "bytes"
        for h in ("Content-Range", "Content-Length"):
            if h in r.headers:
                resp.headers[h] = r.headers[h]
        return add_cors(resp)
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), threaded=True)