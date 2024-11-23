import openai
import os
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Load API keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def fetch_video_transcript(video_url):
    """
    Fetch transcript of a YouTube video.
    """
    try:
        video_id = video_url.split("v=")[-1]

        # Fetch transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([t['text'] for t in transcript])
        return transcript_text
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        print(f"Transcript not available for video {video_url}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error fetching transcript for video {video_url}: {e}")
        return None

def fetch_video_description(video_url):
    """
    Fetch description of a YouTube video.
    """
    try:
        video_id = video_url.split("v=")[-1]
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request = youtube.videos().list(part='snippet', id=video_id)
        response = request.execute()
        return response['items'][0]['snippet']['description']
    except Exception as e:
        print(f"Error fetching video description for {video_url}: {e}")
        return None

def generate_quiz_with_chat_api(content, num_questions=5):
    """
    Generate multiple-choice quiz questions from content using OpenAI's Chat API.
    """
    try:
        messages = [
            {"role": "system", "content": "You are an educational assistant that generates quizzes from text."},
            {"role": "user", "content": (
                f"Create {num_questions} multiple-choice quiz questions from the following content. "
                "Each question should include one correct answer and three incorrect answers. "
                "Output in the format:\n"
                "Question 1:\nAnswer A\nAnswer B Correct:\nAnswer C\nAnswer D\n\n"
                "Content:\n"
                f"{content}"
            )}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=800,
            temperature=0.7,
        )
        return response.choices[0].message['content'].strip()
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return None
    except Exception as e:
        print(f"Error generating quiz: {e}")
        return None

def generate_default_quiz(topic):
    """
    Generate a default quiz based on the module topic using OpenAI's Chat API.
    """
    try:
        messages = [
            {"role": "system", "content": "You are an educational assistant that generates quizzes for learning modules."},
            {"role": "user", "content": (
                f"Generate a simple quiz with 3 questions about the topic: {topic}. "
                "For each question, provide 4 multiple-choice answers and mark one as correct. "
                "Format the output as follows:\n"
                "Question 1:\nAnswer A\nAnswer B Correct:\nAnswer C\nAnswer D\n\n"
                "Question 2:\n..."
            )}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message['content'].strip()
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return None
    except Exception as e:
        print(f"Error generating default quiz: {e}")
        return None

def generate_quiz_from_module(module):
    """
    Generate a quiz for the given module using its YouTube video.
    """
    try:
        # Step 1: Try fetching the transcript
        transcript = fetch_video_transcript(module.video_link)
        if transcript:
            print("Using transcript for quiz generation.")
            return generate_quiz_with_chat_api(transcript)

        # Step 2: Try fetching the description
        description = fetch_video_description(module.video_link)
        if description:
            print("Using video description for quiz generation.")
            return generate_quiz_with_chat_api(description)

        # Step 3: Log fallback if both transcript and description are unavailable
        print(f"No content available for video: {module.video_link}")
        return None  # No content available, return None or raise an exception
    except Exception as e:
        print(f"Error generating quiz for module {module.id}: {e}")
        return None
