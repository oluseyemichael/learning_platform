from decouple import config
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import httplib2
from datetime import datetime, timedelta
import isodate
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

YOUTUBE_API_KEY = config('YOUTUBE_API_KEY')

def get_youtube_videos(topic):
    current_year = datetime.now().year
    published_after = f'{current_year - 2}-01-01T00:00:00Z'  # Last 2 years

    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY, http=httplib2.Http(timeout=30))

        # Construct specific query
        query = f'"{topic}" tutorial OR course OR guide'

        request = youtube.search().list(
            q=query,
            part='snippet',
            maxResults=15,
            order='relevance',
            videoDuration='long',
            type='video',
            publishedAfter=published_after,
            relevanceLanguage="en",
            regionCode="US"
        )
        response = request.execute(num_retries=3)

        videos = []
        for item in response.get('items', []):
            try:
                video_id = item['id']['videoId']
                video_details = youtube.videos().list(part='contentDetails,statistics', id=video_id).execute()
                details = video_details['items'][0]

                # Extract details
                duration_str = details.get('contentDetails', {}).get('duration')
                duration = isodate.parse_duration(duration_str) if duration_str else None

                title = item['snippet']['title']
                description = item['snippet']['description']
                likes = int(details.get('statistics', {}).get('likeCount', 0))
                views = int(details.get('statistics', {}).get('viewCount', 0))
                published_date = item['snippet']['publishedAt']

                # Check if topic is explicitly in title or description
                if topic.lower() in title.lower() or topic.lower() in description.lower():
                    videos.append({
                        'title': title,
                        'description': description,
                        'videoId': video_id,
                        'url': f'https://www.youtube.com/watch?v={video_id}',
                        'duration': duration,
                        'likes': likes,
                        'views': views,
                        'published_date': published_date,
                    })
            except KeyError as e:
                logger.error(f"Missing key in video details: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")

        # Filter by duration
        filtered_videos = [
            video for video in videos
            if timedelta(minutes=30) <= video['duration'] <= timedelta(hours=3)
        ]

        # Sort by likes and views
        filtered_videos.sort(key=lambda x: (x['likes'], x['views'], x['published_date']), reverse=True)

        logger.info(f"Fetched {len(filtered_videos)} videos for topic: {topic}")
        return filtered_videos[:3] if filtered_videos else videos[:3]

    except HttpError as err:
        logger.error(f"An error occurred with the YouTube API: {err}")
    except Exception as err:
        logger.error(f"An unexpected error occurred: {err}")

    return []


if __name__ == "__main__":
    topic = "Python programming"
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
