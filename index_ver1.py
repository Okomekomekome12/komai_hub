import asyncio
from pornhub_api import Client
from flask import Flask, send_from_directory
import os

app = Flask(__name__)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/player.html")
def player():
    return send_from_directory(".", "player.html")

async def _fetch_top_link(video_id):
    client = Client()
    video_object = await client.get_video(video_id)
    await video_object.load_fields("m3u8_base_url")
    print(video_object.title)
    lines = video_object.m3u8_base_url.strip().splitlines()
    return lines[2]

@app.route("/api/videos/<path:video_id>")
def main(video_id):
    top_link = loop.run_until_complete(_fetch_top_link(video_id))
    return f"{top_link}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)