import openai
import os
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

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
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return ""

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
        print(f"Error fetching video description: {e}")
        return ""

def generate_quiz_from_text(content, num_questions=5):
    """
    Generate multiple-choice quiz questions from content using OpenAI API.
    """
    try:
        prompt = (
            f"Create {num_questions} multiple-choice quiz questions from the following content. "
            "Each question should include one correct answer and three incorrect answers:\n\n"
            f"{content}"
        )

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=800,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error generating quiz: {e}")
        return None
    
def generate_default_quiz(topic):
    """
    Generate a default quiz based on the module topic using OpenAI's Chat API.
    """
    try:
        # Define the prompt for quiz generation
        messages = [
            {"role": "system", "content": "You are an educational assistant creating quizzes for learning modules."},
            {
                "role": "user",
                "content": (
                    f"Generate a simple quiz with 3 questions about the topic: {topic}. "
                    "For each question, provide 4 multiple-choice answers and mark one as correct. "
                    "Format the output as follows:\n\n"
                    "Question 1:\nAnswer A\nAnswer B Correct:\nAnswer C\nAnswer D\n\n"
                    "Question 2:\n..."
                ),
            },
        ]

        # Call OpenAI's Chat API
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use GPT-4 or GPT-3.5, depending on your subscription
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print(f"Error generating default quiz: {e}")
        return None