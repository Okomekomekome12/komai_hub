import asyncio
from pornhub_api import Client, DownloadConfigHLS

async def main():
    client = Client()
    video_object = await client.get_video("https://jp.pornhub.com/view_video.php?viewkey=68f9c080f17c9")
    await video_object.load_fields('m3u8_base_url')
    print(video_object.m3u8_base_url)
    print(video_object.title)
    #config = DownloadConfigHLS(quality="best", path="./")
    #await video_object.download(config)

if __name__ == "__main__":
    asyncio.run(main())