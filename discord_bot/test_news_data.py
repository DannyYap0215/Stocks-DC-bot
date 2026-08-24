import unittest
from unittest.mock import patch
from news_data import format_major_news

class TestFormatMajorNews(unittest.TestCase):
    def test_empty_or_none(self):
        """Test with empty list or None."""
        self.assertEqual(format_major_news([]), "")
        self.assertEqual(format_major_news(None), "")

    @patch('news_data.summarize_text')
    @patch('news_data.clean_html')
    def test_single_item_with_summary(self, mock_clean_html, mock_summarize_text):
        """Test with a normal news item that gets summarized."""
        mock_clean_html.return_value = "Clean summary"
        mock_summarize_text.return_value = "• Summarized text"

        news_items = [{
            'title': "Big Event",
            'summary': "<p>Raw summary</p>",
            'link': "http://example.com/news1"
        }]

        result = format_major_news(news_items)

        expected = (
            "🚨 **[MAJOR MARKET ALERT]** 🚨\n\n"
            "🔥 **Big Event**\n"
            "*• Summarized text*\n"
            "[Source](http://example.com/news1)\n\n"
        )
        self.assertEqual(result, expected)
        mock_clean_html.assert_called_once_with("<p>Raw summary</p>")
        mock_summarize_text.assert_called_once_with("Clean summary", 2)

    @patch('news_data.summarize_text')
    @patch('news_data.clean_html')
    def test_single_item_without_summary(self, mock_clean_html, mock_summarize_text):
        """Test with a news item that has no summary key."""
        mock_clean_html.return_value = ""
        mock_summarize_text.return_value = ""

        news_items = [{
            'title': "Another Event",
            'link': "http://example.com/news2"
        }]

        result = format_major_news(news_items)

        expected = (
            "🚨 **[MAJOR MARKET ALERT]** 🚨\n\n"
            "🔥 **Another Event**\n"
            "[Source](http://example.com/news2)\n\n"
        )
        self.assertEqual(result, expected)
        mock_clean_html.assert_called_once_with("")
        mock_summarize_text.assert_called_once_with("", 2)

    @patch('news_data.summarize_text')
    @patch('news_data.clean_html')
    def test_empty_bullet_summary(self, mock_clean_html, mock_summarize_text):
        """Test behavior when summarizer returns an empty bullet point."""
        mock_clean_html.return_value = "Some text"
        mock_summarize_text.return_value = "• "

        news_items = [{
            'title': "Empty Bullet Event",
            'summary': "Some text",
            'link': "http://example.com/news3"
        }]

        result = format_major_news(news_items)

        expected = (
            "🚨 **[MAJOR MARKET ALERT]** 🚨\n\n"
            "🔥 **Empty Bullet Event**\n"
            "[Source](http://example.com/news3)\n\n"
        )
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
