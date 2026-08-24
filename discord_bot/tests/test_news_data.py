import unittest
from news_data import clean_html

class TestCleanHtml(unittest.TestCase):
    def test_clean_html_basic(self):
        """Test removing basic HTML tags."""
        html = "<p>Hello, World!</p>"
        expected = "Hello, World!"
        self.assertEqual(clean_html(html), expected)

    def test_clean_html_nested(self):
        """Test removing nested HTML tags and attributes."""
        html = '<div><h1>Title</h1><p class="content">Some <b>bold</b> text.</p></div>'
        expected = "TitleSome bold text."
        self.assertEqual(clean_html(html), expected)

    def test_clean_html_no_tags(self):
        """Test with string containing no HTML tags."""
        text = "Just a normal string without tags."
        expected = "Just a normal string without tags."
        self.assertEqual(clean_html(text), expected)

    def test_clean_html_empty_string(self):
        """Test with an empty string."""
        html = ""
        expected = ""
        self.assertEqual(clean_html(html), expected)

    def test_clean_html_none(self):
        """Test with None input."""
        html = None
        expected = ""
        self.assertEqual(clean_html(html), expected)

    def test_clean_html_entities(self):
        """Test decoding HTML entities."""
        html = "AT&amp;T and Johnson &amp; Johnson"
        expected = "AT&T and Johnson & Johnson"
        self.assertEqual(clean_html(html), expected)

if __name__ == '__main__':
    unittest.main()
