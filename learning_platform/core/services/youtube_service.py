from decouple import config
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import httplib2
from datetime import datetime, timedelta
import isodate

YOUTUBE_API_KEY = config('YOUTUBE_API_KEY')

def get_youtube_videos(topic):
    current_year = datetime.now().year
    published_after = f'{current_year}-01-01T00:00:00Z'  # Start of the current year in ISO 8601 format

    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY, http=httplib2.Http(timeout=30))

        # Fetching relevant videos for the topic
        request = youtube.search().list(
            q=topic,
            part='snippet',
            maxResults=5,  # Fetch more results to have a buffer
            order='relevance',  # Prioritize relevance
            videoDuration='long',  # Use 'long' for videos longer than 20 minutes
            type='video',
            publishedAfter=published_after,
            relevanceLanguage="en"  # Enforce English-language videos
        )
        response = request.execute(num_retries=3)
        print(f"Initial search response items: {len(response['items'])}")

        videos = []
        for item in response['items']:
            video_id = item['id']['videoId']
            # Fetch video details including duration and statistics
            video_details = youtube.videos().list(part='contentDetails,statistics', id=video_id).execute()
            duration = isodate.parse_duration(video_details['items'][0]['contentDetails']['duration'])
            
            # Check if statistics are available; otherwise, default to 0 for likes
            likes = int(video_details['items'][0]['statistics'].get('likeCount', 0)) if 'statistics' in video_details['items'][0] else 0

            # Filter for videos between 1 and 1.5 hours
            if timedelta(hours=1) <= duration < timedelta(hours=1, minutes=30):
                video_data = {
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'videoId': video_id,
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'duration': str(duration),
                    'likes': likes
                }
                videos.append(video_data)

        # Fallback: if no videos found between 1-1.5 hours, accept any video between 1.5-2 hours
        if not videos:
            for item in response['items']:
                video_id = item['id']['videoId']
                video_details = youtube.videos().list(part='contentDetails,statistics', id=video_id).execute()
                duration = isodate.parse_duration(video_details['items'][0]['contentDetails']['duration'])
                likes = int(video_details['items'][0]['statistics'].get('likeCount', 0)) if 'statistics' in video_details['items'][0] else 0

                if timedelta(hours=1, minutes=30) <= duration <= timedelta(hours=2):
                    video_data = {
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'videoId': video_id,
                        'url': f'https://www.youtube.com/watch?v={video_id}',
                        'duration': str(duration),
                        'likes': likes
                    }
                    videos.append(video_data)
                    break  # Only add one fallback video

        # Sort videos by likes if multiple matches found
        videos.sort(key=lambda x: x['likes'], reverse=True)
        return videos

    except TimeoutError:
        print("The request timed out.")
    except HttpError as err:
        print(f"An error occurred: {err}")
    return []

# Test the function
if __name__ == "__main__":
    try:
        # Test with a sample topic
        topic = "learn css"
        results = get_youtube_videos(topic)

        # Print results in a readable format
        print(f"\nSearch results for '{topic}':\n")
        for video in results:
            print("Title:", video['title'])
            print("Description:", video['description'])
            print("URL:", video['url'])
            print("Duration:", video['duration'])
            print("Likes:", video['likes'])
            print("-" * 50)
            
    except Exception as e:
        print("An error occurred:", str(e))
