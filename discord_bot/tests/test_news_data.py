import pytest
from unittest.mock import patch
from discord_bot.news_data import summarize_text

def test_summarize_text_empty_and_short():
    assert summarize_text(None) is None
    assert summarize_text("") == ""
    assert summarize_text("Too short") == "Too short"

def test_summarize_text_happy_path():
    long_text = (
        "Artificial intelligence is transforming the world. "
        "Many companies are investing heavily in AI technologies. "
        "The impact on the job market is still being studied. "
        "Some believe AI will create new opportunities for everyone. "
        "Others worry about potential displacement of workers in certain sectors. "
        "Only time will tell the true extent of these changes."
    )
    # Ensure > 100 characters
    assert len(long_text) > 100

    # Request a 2 sentence summary
    result = summarize_text(long_text, sentences_count=2)

    # Verify it returns bullet points
    lines = result.split("\n")
    assert len(lines) == 2
    assert all(line.startswith("• ") for line in lines)

    # Length of summary should be less than original text
    assert len(result) < len(long_text)

def test_summarize_text_exception():
    long_text = "A" * 250
    with patch("discord_bot.news_data.PlaintextParser.from_string", side_effect=Exception("Mock Error")):
        result = summarize_text(long_text)
        assert result == f"• {'A' * 200}..."
