import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from news_data import summarize_text

class TestNewsData(unittest.TestCase):
    def test_summarize_text_short(self):
        short_text = "This is a short text that is less than 100 characters long."
        self.assertTrue(len(short_text) < 100)
        result = summarize_text(short_text)
        self.assertEqual(result, short_text)

    def test_summarize_text_empty(self):
        result = summarize_text("")
        self.assertEqual(result, "")

    def test_summarize_text_none(self):
        result = summarize_text(None)
        self.assertEqual(result, None)

if __name__ == '__main__':
    unittest.main()
