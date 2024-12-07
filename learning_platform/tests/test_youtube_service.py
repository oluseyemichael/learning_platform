import unittest
from unittest.mock import patch, MagicMock
from datetime import timedelta
from core.services.youtube_service import get_youtube_videos


class TestYouTubeService(unittest.TestCase):

    @patch("core.services.youtube_service.build")
    def test_get_youtube_videos_success(self, mock_build):
        # Mock YouTube API client
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube

        # Mock API responses
        mock_youtube.search().list().execute.return_value = {
            "items": [
                {
                    "id": {"videoId": "test_video_id_1"},
                    "snippet": {
                        "title": "Test Video 1",
                        "description": "Description of Test Video 1",
                        "publishedAt": "2023-01-01T00:00:00Z"
                    }
                }
            ]
        }
        mock_youtube.videos().list().execute.return_value = {
            "items": [
                {
                    "contentDetails": {"duration": "PT1H30M"},  # 1.5 hours
                    "statistics": {"likeCount": "100", "viewCount": "5000"}
                }
            ]
        }

        # Call the function
        videos = get_youtube_videos("test topic")

        # Assertions
        self.assertEqual(len(videos), 1)
        self.assertEqual(videos[0]["videoId"], "test_video_id_1")
        self.assertEqual(videos[0]["likes"], 100)
        self.assertEqual(videos[0]["views"], 5000)
        self.assertGreaterEqual(videos[0]["duration"], timedelta(minutes=45))
        self.assertLessEqual(videos[0]["duration"], timedelta(hours=2))

    @patch("core.services.youtube_service.build")
    def test_get_youtube_videos_no_results(self, mock_build):
        # Mock YouTube API client
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube

        # Mock API responses with no results
        mock_youtube.search().list().execute.return_value = {"items": []}

        # Call the function
        videos = get_youtube_videos("test topic")

        # Assertions
        self.assertEqual(videos, [])


if __name__ == "__main__":
    unittest.main()
