from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
import pandas as pd

# Define the required scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Authenticate and create the API client
def authenticate_youtube():
    flow = InstalledAppFlow.from_client_secrets_file(
    "data/client_secrets.json", SCOPES)

    credentials = flow.run_local_server(port=8080)  # Use a fixed port

    # Load existing credentials from file if available
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
    # Authenticate if credentials are not available or expired
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "data/client_secrets.json", SCOPES)
            print(credentials)
        # Save the credentials for future use
        print(credentials)
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)
    return build("youtube", "v3", credentials=credentials)

# Get subscribers
def get_subscribers(youtube):
    nextPageToken = None
    data = []
    while True:
        request = youtube.subscriptions().list(
            part="snippet",
            mine=True,
            maxResults=50,  # Maximum number of results per page
            pageToken=nextPageToken  # Add pageToken if it's not the first page
        )
        response = request.execute()
        subscribers = response.get("items", [])

        
        for subscriber in subscribers:
            subscriber_info = {
                "Title": subscriber["snippet"]["title"],
                "Description": subscriber["snippet"]["description"],
                "Channel ID": subscriber["snippet"]["channelId"],
                "Channel ID": subscriber["snippet"]["resourceId"],
                "Published At": subscriber["snippet"]["publishedAt"]
            }
            
            # Append to list
            data.append(subscriber_info)

        # Check if there are more pages, if yes, move to the next page
        nextPageToken = response.get("nextPageToken")
        if not nextPageToken:
            break
    # Save to Excel
    save_data(data, "data/liked_videos.xlsx")
    return subscribers

# Get liked videos
def get_liked_videos(youtube):
    data = []
    nextPageToken = None
    while True:
        request = youtube.videos().list(
            part="snippet,contentDetails",
            myRating="like",
            maxResults=50,
            pageToken=nextPageToken
        )
        response = request.execute()
        liked_videos = response.get("items", [])

        for video in liked_videos:
            info = {
                "Id": video["id"],
                "Title": video["snippet"]["title"],
                "Description": video["snippet"]["description"],
                "Channel ID": video["snippet"]["channelId"],
                "Published At": video["snippet"]["publishedAt"],
                "Thumnails": video["snippet"]["thumbnails"],
                "Duration": video["contentDetails"]["duration"],
            }
            
            # Append to list
            data.append(info)

        # Check if there are more pages, if yes, move to the next page
        nextPageToken = response.get("nextPageToken")
        if not nextPageToken:
            break
        
    save_data(data, "data/liked_videos.xlsx")
    return data

# Get playlists
def get_playlists(youtube):
    data = []
    nextPageToken = None
    while True:
        request = youtube.playlists().list(
            part="snippet,contentDetails",
            mine=True,
            maxResults=50,
            pageToken=nextPageToken
        )
        response = request.execute()
        playlists = response.get("items", [])

        for item in playlists:
            info = {
                "Id": item["id"],
                "Title": item["snippet"]["title"],
                "Description": item["snippet"]["description"],
                "Published At": item["snippet"]["publishedAt"],
                "Thumnails": item["snippet"]["thumbnails"],
                "Content Details": item["contentDetails"],	
                "Content Item Count": item["contentDetails"]["itemCount"],	
            }
        
            # Append to list
            data.append(info)

        # Check if there are more pages, if yes, move to the next page
        nextPageToken = response.get("nextPageToken")
        if not nextPageToken:
            break
    save_data(data, "data/playlists.xlsx")
    return playlists

def save_data(data, filename):
    """Save the data in Excel, CSV, and TXT formats."""
    df = pd.DataFrame(data)

    # Save as Excel
    excel_filename = f"{filename}.xlsx"
    df.to_excel(excel_filename, index=False)
    print(f"Saved {filename} to {excel_filename}")

    # Save as CSV
    csv_filename = f"{filename}.csv"
    df.to_csv(csv_filename, index=False)
    print(f"Saved {filename} to {csv_filename}")

    # Save as TXT (tab-delimited)
    txt_filename = f"{filename}.txt"
    df.to_csv(txt_filename, sep="\t", index=False)
    print(f"Saved {filename} to {txt_filename}")

# Main script
if __name__ == "__main__":
    # Authenticate Youtube OAuth, Youtube Data API v3
    youtube = authenticate_youtube()
    subscribers = get_subscribers(youtube)
    liked = get_liked_videos(youtube)
    playlists = get_playlists(youtube)

