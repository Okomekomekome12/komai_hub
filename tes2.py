import asyncio
from pornhub_api import Client, DownloadConfigHLS
from flask import Flask , send_from_directory 
from urllib.parse import unquote

app = Flask(__name__)

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/player.html")
def player():
    return send_from_directory(".", "player.html")


@app.route("/api/videos/<path:video_id>")
async def main(video_id):
    client = Client()
    #video_object = await client.get_video("https://jp.pornhub.com/view_video.php?viewkey=68f9c080f17c9")
    video_object = await client.get_video(video_id)
    await video_object.load_fields("m3u8_base_url")
    print(video_object.title)
    #print(video_object.m3u8_base_url)
    lines = video_object.m3u8_base_url.strip().splitlines()
    top_link = lines[2]
    print(top_link)
    return f"{top_link}"
if __name__ == "__main__":
    app.run(debug=True)
    asyncio.run(main("https://jp.pornhub.com/view_video.php?viewkey=68f9c080f17c9"))