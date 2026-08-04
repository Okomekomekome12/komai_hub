from flask import Flask, Response, request
from curl_cffi import requests as creq
from urllib.parse import quote

app = Flask(__name__)

HEADERS = {
    "Referer": "https://www.pornhub.com/",
    "Origin": "https://www.pornhub.com",
}

@app.route("/proxy")
def proxy():
    target_url = request.args.get("url")
    if not target_url:
        return "Missing 'url' parameter", 400

    r = creq.get(target_url, headers=HEADERS, impersonate="chrome124")
    content_type = r.headers.get("content-type", "application/vnd.apple.mpegurl")

    if "mpegurl" in content_type or target_url.endswith(".m3u8"):
        base = target_url.rsplit("/", 1)[0]
        lines = []
        for line in r.text.splitlines():
            if line and not line.startswith("#"):
                seg_url = line if line.startswith("http") else f"{base}/{line}"
                line = f"/proxy?url={quote(seg_url, safe='')}"  # ← ここを修正
            lines.append(line)
        return Response("\n".join(lines), content_type="application/vnd.apple.mpegurl")

    return Response(r.content, content_type=content_type)

if __name__ == "__main__":
    app.run(port=5000, debug=True)