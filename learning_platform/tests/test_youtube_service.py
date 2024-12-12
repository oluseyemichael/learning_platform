import unittest
from unittest.mock import patch, MagicMock
from core.services.youtube_service import get_youtube_videos

class TestYouTubeService(unittest.TestCase):

    @patch('core.services.youtube_service.build')
    @patch('core.services.youtube_service.calculate_text_similarity')
    def test_get_youtube_videos_success(self, mock_similarity, mock_build):
        """Test fetching YouTube videos successfully."""
        # Setup mock similarity to always return high values
        mock_similarity.return_value = 0.8

        # Mock YouTube API
        mock_youtube = MagicMock()
        mock_search = mock_youtube.search.return_value.list.return_value
        mock_videos = mock_youtube.videos.return_value.list.return_value

        # Mocked API search response
        mock_search.execute.return_value = {
            'items': [
                {'id': {'videoId': 'video1'}},
                {'id': {'videoId': 'video2'}}
            ]
        }

        # Mocked API video details response
        mock_videos.execute.return_value = {
            'items': [
                {
                    'contentDetails': {'duration': 'PT1H30M'},
                    'snippet': {
                        'title': 'Object Oriented Programming Explained',
                        'description': 'Deep dive into Object Oriented Programming concepts',
                        'channelTitle': 'Tech Tutorials',
                        'publishedAt': '2023-01-01T00:00:00Z',
                    },
                    'statistics': {'viewCount': '1000'}
                },
                {
                    'contentDetails': {'duration': 'PT1H45M'},
                    'snippet': {
                        'title': 'Advanced OOP Techniques',
                        'description': 'Advanced Object Oriented Programming strategies',
                        'channelTitle': 'Code Masters',
                        'publishedAt': '2023-01-02T00:00:00Z',
                    },
                    'statistics': {'viewCount': '2000'}
                },
            ]
        }

        mock_build.return_value = mock_youtube

        # Call the function
        topic = "Object Oriented Programming"
        videos = get_youtube_videos(topic, max_results=2)

        # Debug print
        print("Returned videos:", videos)

        # Assert basic expectations
        self.assertIsInstance(videos, list)
        self.assertTrue(len(videos) > 0)

        # Print out details for investigation
        for video in videos:
            print(f"Title: {video.get('title')}")
            print(f"Views: {video.get('views')}")
            print(f"Title Similarity: {video.get('title_similarity')}")
            print("---")

    @patch('core.services.youtube_service.build')
    def test_get_youtube_videos_no_results(self, mock_build):
        """Test fetching YouTube videos with no results."""
        # Mock YouTube API response with no items
        mock_youtube = MagicMock()
        mock_youtube.search.return_value.list.return_value.execute.return_value = {'items': []}
        mock_build.return_value = mock_youtube

        # Call the function
        topic = "Nonexistent Topic"
        videos = get_youtube_videos(topic)

        # Assert no results
        self.assertEqual(len(videos), 0)

    @patch('core.services.youtube_service.build')
    def test_get_youtube_videos_error_handling(self, mock_build):
        """Test error handling in fetching YouTube videos."""
        # Mock YouTube API to raise an exception
        mock_build.side_effect = Exception("API error")

        # Call the function
        topic = "Error Topic"
        videos = get_youtube_videos(topic)

        # Assert empty result due to error
        self.assertEqual(len(videos), 0)

if __name__ == '__main__':
    unittest.main()