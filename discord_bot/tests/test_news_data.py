import pytest
from news_data import clean_html

def test_clean_html_none():
    assert clean_html(None) == ""

def test_clean_html_empty_string():
    assert clean_html("") == ""

def test_clean_html_valid_html():
    html_input = "<html><body><h1>Hello, World!</h1><p>This is a <b>test</b>.</p></body></html>"
    expected_output = "Hello, World!This is a test."
    assert clean_html(html_input) == expected_output

def test_clean_html_no_tags():
    text_input = "Just plain text without tags."
    assert clean_html(text_input) == text_input
