import asyncio
from xvideos_api import Client, DownloadConfigHLS

async def main():
    # Initialize a Client object
    client = Client()
    
    # Fetch a video
    video_object = await client.get_video("https://www.xvideos.com/video.ooeaoup938e/_")
    
    # Information from Video objects
    print(video_object.title)
    print(video_object.content_url)

    # Download the video
    config = DownloadConfigHLS(quality="best", path="./") # More options in the documentation
    await video_object.download(config)

if __name__ == "__main__":
    asyncio.run(main())