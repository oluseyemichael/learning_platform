from decouple import config
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import httplib2
from datetime import datetime, timedelta
import isodate
import logging
import re

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

YOUTUBE_API_KEY = config('YOUTUBE_API_KEY')

def clean_title(title):
    """
    Clean and normalize video titles to improve matching and filtering.
    
    Args:
        title (str): Original video title
    
    Returns:
        str: Cleaned and normalized title
    """
    # Remove special characters and convert to lowercase
    cleaned = re.sub(r'[^\w\s]', '', title.lower())
    
    # Remove common filler words and variations
    filler_words = [
        'full', 'complete', 'ultimate', 'comprehensive', 
        'tutorial', 'guide', 'course', 'masterclass',
        '2024', '2023', 'new', 'latest'
    ]
    for word in filler_words:
        cleaned = cleaned.replace(word, '').strip()
    
    return cleaned

def generate_search_queries(topic):
    """
    Generate multiple search query variations to improve result diversity.
    
    Args:
        topic (str): Original search topic
    
    Returns:
        list: List of search query variations
    """
    base_queries = [
        f"{topic} tutorial",
        f"learn {topic}",
        f"{topic} explained",
        f"best {topic} course",
        f"comprehensive {topic} guide",
        f"{topic} for beginners",
        f"advanced {topic} techniques"
    ]
    return base_queries

def get_youtube_videos(topic, max_results=20):
    """
    Enhanced YouTube video search with multiple query strategies and advanced filtering.
    
    Args:
        topic (str): Search topic
        max_results (int, optional): Maximum number of results to fetch. Defaults to 20.
    
    Returns:
        list: Filtered and ranked video results
    """
    current_year = datetime.now().year
    published_after = f'{current_year - 2}-01-01T00:00:00Z'  # Last 2 years

    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY, http=httplib2.Http(timeout=30))
        all_videos = []

        # Try multiple query variations
        for query in generate_search_queries(topic):
            try:
                request = youtube.search().list(
                    q=query,
                    part='snippet',
                    maxResults=15,
                    order='viewCount',  # Prioritize popular videos
                    videoDuration='long',  # 'long' for videos > 20 minutes
                    type='video',
                    publishedAfter=published_after,
                    relevanceLanguage="en",
                    regionCode="US"
                )
                response = request.execute(num_retries=3)

                # Process each video
                for item in response.get('items', []):
                    try:
                        video_id = item['id']['videoId']
                        
                        # Fetch detailed video information
                        video_details = youtube.videos().list(
                            part='contentDetails,statistics,snippet', 
                            id=video_id
                        ).execute()
                        
                        details = video_details['items'][0]

                        # Extract video details with robust error handling
                        duration_str = details.get('contentDetails', {}).get('duration')
                        duration = isodate.parse_duration(duration_str) if duration_str else None

                        # Skip videos with undefined duration
                        if not duration:
                            continue

                        # Enhanced metrics and filtering
                        video_info = {
                            'title': item['snippet']['title'],
                            'clean_title': clean_title(item['snippet']['title']),
                            'description': item['snippet']['description'],
                            'videoId': video_id,
                            'url': f'https://www.youtube.com/watch?v={video_id}',
                            'duration': duration,
                            'likes': int(details.get('statistics', {}).get('likeCount', 0)),
                            'views': int(details.get('statistics', {}).get('viewCount', 0)),
                            'channel_title': item['snippet']['channelTitle'],
                            'published_date': item['snippet']['publishedAt']
                        }

                        all_videos.append(video_info)

                    except (KeyError, ValueError) as e:
                        logger.warning(f"Skipping video due to parsing error: {e}")

            except HttpError as e:
                logger.error(f"HTTP error in query '{query}': {e}")

        # Advanced filtering and ranking
        filtered_videos = [
            video for video in all_videos
            if (
                # Duration between 30 minutes and 2 hours
                timedelta(minutes=30) <= video['duration'] <= timedelta(hours=2)
                # Decent number of views
                and video['views'] > 5000
            )
        ]

        # Sophisticated ranking function
        def ranking_score(video):
            # Combine multiple factors: views, likes, recency, and title relevance
            view_score = min(video['views'] / 10000, 10)  # Cap at 10
            like_score = min(video['likes'] / 1000, 5)  # Cap at 5
            
            # Calculate title relevance
            title_words = video['clean_title'].split()
            topic_words = clean_title(topic).split()
            title_relevance = len(set(title_words) & set(topic_words)) / len(topic_words or [1])
            
            # Recency bonus
            published_date = datetime.fromisoformat(video['published_date'].replace('Z', '+00:00'))
            days_since_publish = (datetime.now(published_date.tzinfo) - published_date).days
            recency_score = max(10 - (days_since_publish / 365), 0)  # Bonus decays over years
            
            return view_score + like_score + (title_relevance * 5) + recency_score

        # Sort and return top results
        ranked_videos = sorted(filtered_videos, key=ranking_score, reverse=True)
        
        logger.info(f"Fetched {len(ranked_videos)} videos for topic: {topic}")
        return ranked_videos[:5]  # Return top 5 videos

    except Exception as err:
        logger.error(f"Unexpected error in video search: {err}")
        return []

if __name__ == "__main__":
    # Example usage
    topics = [
        "What is oop"
    ]
    
    for topic in topics:
        print(f"\nSearch results for '{topic}':\n")
        results = get_youtube_videos(topic)
        
        for video in results:
            print("Title:", video['title'])
            print("Channel:", video['channel_title'])
            print("Views:", video['views'])
            print("URL:", video['url'])
            print("Duration:", video['duration'])
            print("-" * 50)