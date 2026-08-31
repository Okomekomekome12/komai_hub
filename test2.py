from pornhub_api import Client, DownloadConfigHLS
import asyncio
client = Client()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
async def video_search(query):
    async for result in client.search_videos(
        query=query,
        sort_by="mr",        
        duration_min="10",   
        pages=2):
        if result.data:
            video = result.data
            print(video.title)
            print(video.key)
loop.run_until_complete(video_search("keyword"))