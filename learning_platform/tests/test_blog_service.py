import unittest
from unittest.mock import patch
from core.services.blog_service import get_blog_posts


class TestBlogService(unittest.TestCase):

    @patch("core.services.blog_service.requests.get")
    def test_get_blog_posts_success(self, mock_get):
        # Mock response from SerpAPI
        mock_response = {
            "organic_results": [
                {"title": "Learn Python Tutorial", "link": "https://example.com/learn-python"},
                {"title": "Python Course", "link": "https://example.com/python-course"}
            ]
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.status_code = 200

        # Call the function
        result = get_blog_posts("Python")

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "Learn Python Tutorial")
        self.assertEqual(result["url"], "https://example.com/learn-python")

    @patch("core.services.blog_service.requests.get")
    def test_get_blog_posts_no_results(self, mock_get):
        # Mock response with no organic results
        mock_response = {"organic_results": []}
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.status_code = 200

        # Call the function
        result = get_blog_posts("Python")

        # Assertions
        self.assertIsNone(result)

    @patch("core.services.blog_service.requests.get")
    def test_get_blog_posts_api_error(self, mock_get):
        # Mock an HTTP error
        mock_get.side_effect = Exception("API error")

        # Call the function
        result = get_blog_posts("Python")

        # Assertions
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
