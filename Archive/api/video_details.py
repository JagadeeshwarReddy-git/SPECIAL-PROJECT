from googleapiclient.discovery import build
from config import YOUTUBE_API_KEY

youtube = build(
    "youtube",
    "v3",
    developerKey=YOUTUBE_API_KEY
)

def get_video_details(video_id):

    request = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    )

    response = request.execute()

    if not response["items"]:
        return None

    item = response["items"][0]

    return {
        "title": item["snippet"]["title"],
        "channel": item["snippet"]["channelTitle"],
        "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
        "description": item["snippet"]["description"],
        "published": item["snippet"]["publishedAt"],
        "views": item["statistics"].get("viewCount", 0),
        "likes": item["statistics"].get("likeCount", 0),
        "comments": item["statistics"].get("commentCount", 0)
    }