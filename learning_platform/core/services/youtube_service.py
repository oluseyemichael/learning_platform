from decouple import config
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import httplib2
from datetime import datetime, timedelta
import isodate
import logging
import re
from difflib import SequenceMatcher

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

YOUTUBE_API_KEY = config('YOUTUBE_API_KEY')

def calculate_text_similarity(a, b):
    """
    Calculate similarity between two strings using SequenceMatcher.
    
    Args:
        a (str): First string
        b (str): Second string
    
    Returns:
        float: Similarity score between 0 and 1
    """
    # Convert to lowercase and remove special characters
    a_clean = re.sub(r'[^\w\s]', '', a.lower())
    b_clean = re.sub(r'[^\w\s]', '', b.lower())
    
    return SequenceMatcher(None, a_clean, b_clean).ratio()

def generate_topic_specific_queries(topic):
    """
    Generate highly specific search queries for the given topic.
    
    Args:
        topic (str): Original search topic
    
    Returns:
        list: List of precise search query variations
    """
    # Remove common filler words and extra spaces
    topic_clean = re.sub(r'\s+', ' ', topic.strip())
    
    # Generate precise queries
    precise_queries = [
        f"full {topic_clean} tutorial",
        f"complete {topic_clean} explained",
        f"beginner to advanced {topic_clean}",
        f"{topic_clean} in-depth course",
        topic_clean  # Include the original topic
    ]
    
    return precise_queries

def get_youtube_videos(topic, max_results=20, similarity_threshold=0.5):
    """
    Enhanced YouTube video search with strict topic relevance filtering.
    
    Args:
        topic (str): Search topic
        max_results (int, optional): Maximum number of results to fetch. Defaults to 20.
        similarity_threshold (float, optional): Minimum similarity score for topic matching. Defaults to 0.5.
    
    Returns:
        list: Filtered and ranked video results
    """
    current_year = datetime.now().year
    published_after = f'{current_year - 2}-01-01T00:00:00Z'  # Last 2 years

    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY, http=httplib2.Http(timeout=30))
        all_videos = []

        # Extensive language filtering
        language_filters = {
            'language': 'en',  # English language content
            'regions': ['US', 'GB', 'CA', 'AU']  # English-speaking regions
        }

        # Try multiple highly specific queries
        for query in generate_topic_specific_queries(topic):
            try:
                request = youtube.search().list(
                    q=query,
                    part='snippet',
                    maxResults=20,  # Increased to capture more potential matches
                    order='relevance',
                    videoDuration='long',  # 'long' for videos > 20 minutes
                    type='video',
                    publishedAfter=published_after,
                    relevanceLanguage=language_filters['language'],
                    regionCode=language_filters['regions'][0]  # Primary region
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

                        # Extract video details
                        duration_str = details.get('contentDetails', {}).get('duration')
                        duration = isodate.parse_duration(duration_str) if duration_str else None

                        # Skip videos with undefined duration
                        if not duration:
                            continue

                        # Title and description for topic similarity check
                        title = item['snippet']['title']
                        description = item['snippet']['description']

                        # Compute topic similarity
                        title_similarity = calculate_text_similarity(topic, title)
                        desc_similarity = calculate_text_similarity(topic, description)
                        
                        # Strict topic relevance filtering
                        if (title_similarity < similarity_threshold and 
                            desc_similarity < similarity_threshold):
                            continue

                        # Enhanced video information
                        video_info = {
                            'title': title,
                            'description': description,
                            'videoId': video_id,
                            'url': f'https://www.youtube.com/watch?v={video_id}',
                            'duration': duration,
                            'likes': int(details.get('statistics', {}).get('likeCount', 0)),
                            'views': int(details.get('statistics', {}).get('viewCount', 0)),
                            'channel_title': item['snippet']['channelTitle'],
                            'published_date': item['snippet']['publishedAt'],
                            'title_similarity': title_similarity,
                            'desc_similarity': desc_similarity
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
                # Language and region check (optional additional filter)
                and any(region in video['channel_title'] for region in ['US', 'UK', 'Canada', 'Australia'])
            )
        ]

        # Sophisticated ranking function
        def ranking_score(video):
            # Combine multiple factors
            view_score = min(video['views'] / 10000, 10)  # Cap at 10
            like_score = min(video['likes'] / 1000, 5)  # Cap at 5
            
            # Heavily weight topic similarity
            similarity_score = (video['title_similarity'] * 10) + (video['desc_similarity'] * 5)
            
            # Recency bonus
            published_date = datetime.fromisoformat(video['published_date'].replace('Z', '+00:00'))
            days_since_publish = (datetime.now(published_date.tzinfo) - published_date).days
            recency_score = max(10 - (days_since_publish / 365), 0)
            
            return view_score + like_score + similarity_score + recency_score

        # Sort and return top results
        ranked_videos = sorted(filtered_videos, key=ranking_score, reverse=True)
        
        logger.info(f"Fetched {len(ranked_videos)} videos for topic: {topic}")
        
        # Annotate results with similarity scores for debugging
        for video in ranked_videos[:5]:
            logger.info(f"Video: {video['title']}")
            logger.info(f"Title Similarity: {video['title_similarity']:.2f}")
            logger.info(f"Description Similarity: {video['desc_similarity']:.2f}")
        
        return ranked_videos[:5]  # Return top 5 videos

    except Exception as err:
        logger.error(f"Unexpected error in video search: {err}")
        return []

if __name__ == "__main__":
    # Example usage with precise topics
    topics = [
        "Introduction to data science"
    ]
    
    for topic in topics:
        print(f"\nSearch results for '{topic}':\n")
        results = get_youtube_videos(topic, similarity_threshold=0.6)
        
        for video in results:
            print("Title:", video['title'])
            print("Channel:", video['channel_title'])
            print("Views:", video['views'])
            print("Title Similarity:", video['title_similarity'])
            print("Description Similarity:", video['desc_similarity'])
            print("URL:", video['url'])
            print("Duration:", video['duration'])
            print("-" * 50)