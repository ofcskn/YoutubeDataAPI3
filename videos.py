from googleapiclient.discovery import build
from dotenv import load_dotenv
import pandas as pd
import re
import os

# Load environment variables from .env file
load_dotenv()

# Get API_KEY and CHANNEL_ID from .env
API_KEY = os.getenv('YOUTUBE_API_KEY')
CHANNEL_ID = os.getenv('CHANNEL_ID')

# Initialize YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_channel_videos(channel_id):
    video_data = []
    next_page_token = None

    while True:
        # Get the playlist ID for uploaded videos
        channel_response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Fetch videos from the playlist
        playlist_response = youtube.playlistItems().list(
            part='snippet',
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in playlist_response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_data.append(get_video_details(video_id))

        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break

    return video_data

def get_video_details(video_id):
    video_response = youtube.videos().list(
        part='snippet,statistics',
        id=video_id
    ).execute()

    video = video_response['items'][0]
    snippet = video['snippet']
    stats = video['statistics']

    # Extract keywords from the description using regex (if any)
    description = snippet.get('description', '')
    description_keywords = re.findall(r"#\w+", description)
    
    # Get the tags (keywords) from the video
    tags = snippet.get('tags', [])
    
    # Get the category ID and resolve it to a category name
    category_id = snippet.get('categoryId', None)
    category_name = get_video_category_name(category_id) if category_id else "Unknown"

    return {
        'Video ID': video_id,
        'Title': snippet.get('title'),
        'Description': description,
        'Description Keywords': ', '.join(description_keywords),
        'Tags (Keywords)': ', '.join(tags),
        'Category': category_name,
        'View Count': stats.get('viewCount', 0),
        'Like Count': stats.get('likeCount', 0),
        'Comments Count': stats.get('commentCount', 0),
        'Publish Date': snippet.get('publishedAt'),
        'Thumbnail': snippet['thumbnails']['high']['url']
    }

def get_video_category_name(category_id):
    category_response = youtube.videoCategories().list(
        part='snippet',
        id=category_id
    ).execute()

    if category_response['items']:
        return category_response['items'][0]['snippet']['title']
    return "Unknown"

def save_to_csv(video_data, filename='data/channel_videos.csv'):
    df = pd.DataFrame(video_data)
    df.to_csv(filename, index=False, encoding='utf-8-sig')

if __name__ == '__main__':
    video_data = get_channel_videos(CHANNEL_ID)
    save_to_csv(video_data)
    print(f"Saved {len(video_data)} videos to data/channel_videos.csv")
