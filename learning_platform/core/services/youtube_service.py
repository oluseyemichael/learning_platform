from decouple import config
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import httplib2
from datetime import datetime, timedelta
import isodate

YOUTUBE_API_KEY = config('YOUTUBE_API_KEY')

def get_youtube_videos(topic):
    current_year = datetime.now().year
    published_after = f'{current_year - 2}-01-01T00:00:00Z'  # Last 2 years

    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY, http=httplib2.Http(timeout=30))

        # Construct improved query
        query = f"{topic} complete guide 2024 full tutorial"

        # Fetching relevant videos for the topic
        request = youtube.search().list(
            q=query,
            part='snippet',
            maxResults=15,  # Fetch a wider pool
            order='relevance',  # Prioritize relevance
            videoDuration='long',  # 'long' for videos > 20 minutes
            type='video',
            publishedAfter=published_after,
            relevanceLanguage="en"
        )
        response = request.execute(num_retries=3)

        videos = []
        for item in response.get('items', []):
            video_id = item['id']['videoId']
            video_details = youtube.videos().list(part='contentDetails,statistics', id=video_id).execute()
            details = video_details['items'][0]

            # Extract video details
            duration = isodate.parse_duration(details['contentDetails']['duration'])
            likes = int(details['statistics'].get('likeCount', 0))
            views = int(details['statistics'].get('viewCount', 0))
            published_date = item['snippet']['publishedAt']

            videos.append({
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'videoId': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'duration': duration,
                'likes': likes,
                'views': views,
                'published_date': published_date,
            })

        # Filter for comprehensive videos
        filtered_videos = [
            video for video in videos
            if timedelta(minutes=45) <= video['duration'] <= timedelta(hours=2)
        ]

        # Sort videos by likes, views, and recency
        filtered_videos.sort(key=lambda x: (x['likes'], x['views'], x['published_date']), reverse=True)

        return filtered_videos[:3]  # Return the top 3 videos

    except TimeoutError:
        print("The request timed out.")
    except HttpError as err:
        print(f"An error occurred: {err}")
    return []



if __name__ == "__main__":
    topic = "Git Fundamentals, Branching Strategies, and Collaboration"
    results = get_youtube_videos(topic)

    print(f"\nSearch results for '{topic}':\n")
    for video in results:
        print("Title:", video['title'])
        print("Description:", video['description'])
        print("URL:", video['url'])
        print("Duration:", video['duration'])
        print("Likes:", video['likes'])
        print("Views:", video['views'])
        print("-" * 50)
