import feedparser
import datetime
import time
import re
from bs4 import BeautifulSoup
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# List of RSS feeds for financial news
NEWS_FEEDS = [
    "https://finance.yahoo.com/news/rssindex",
    "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664", # CNBC Finance
    "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml", # WSJ Business
]

# Keywords that indicate a major event
MAJOR_NEWS_KEYWORDS = [
    "war", "conflict", "crash", "fed rate", "emergency",
    "plunge", "collapse", "crisis", "attack", "bankrupt",
    "scandal", "hacked", "breach"
]

# Keep track of seen news to avoid duplicate alerts
seen_news_links = set()

def fetch_latest_news():
    """Fetches the latest news from RSS feeds."""
    all_news = []

    for feed_url in NEWS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:15]:  # Look at the 15 most recent entries
                # Make sure we don't process very old news
                all_news.append({
                    'title': entry.title,
                    'link': entry.link,
                    'summary': entry.get('summary', ''),
                    'published': entry.get('published', '')
                })
        except Exception as e:
            print(f"Error fetching feed {feed_url}: {e}")

    return all_news

def check_for_major_news():
    """Checks recent news for major event keywords."""
    global seen_news_links

    latest_news = fetch_latest_news()
    major_news_alerts = []

    for item in latest_news:
        if item['link'] in seen_news_links:
            continue

        title_lower = item['title'].lower()
        summary_lower = item['summary'].lower()

        # Check if any major keyword is in the title or summary using whole word matching
        is_major = False
        for keyword in MAJOR_NEWS_KEYWORDS:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, title_lower) or re.search(pattern, summary_lower):
                is_major = True
                break

        if is_major:
            major_news_alerts.append(item)
            seen_news_links.add(item['link'])

    # Clean up seen links if it gets too large to prevent memory issues
    if len(seen_news_links) > 1000:
        seen_news_links.clear() # simpler safe approach for a set

    return major_news_alerts

def clean_html(raw_html):
    """Removes HTML tags from a string."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text()

def summarize_text(text, sentences_count=3):
    """Summarizes text using Sumy LSA Summarizer and formats as bullet points."""
    if not text or len(text) < 100:
        return text
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary = summarizer(parser.document, sentences_count)

        # Format as strict bullet points for an executive summary feel
        bullets = [f"• {str(sentence)}" for sentence in summary]
        return "\n".join(bullets)
    except Exception as e:
        print(f"Summarization error: {e}")
        return f"• {text[:200]}..."

def get_daily_news_summary():
    """Gets a summary of recent general news, formatted cleanly."""
    latest_news = fetch_latest_news()
    if not latest_news:
        return "Could not fetch news at this time."

    summary = "🗞️ **[Market News · Daily Highlights]**\n\n"
    # Take the top 3 recent news articles and format them well
    for i, item in enumerate(latest_news[:3]):
        clean_desc = clean_html(item.get('summary', ''))
        short_summary = summarize_text(clean_desc, 3)

        summary += f"📈 **{item['title']}**\n"
        if short_summary and short_summary != "• ":
            summary += f"*{short_summary}*\n"
        summary += f"[Read more]({item['link']})\n\n"

    return summary

def format_major_news(news_items):
    """Formats major news alerts."""
    if not news_items:
        return ""

    result = "🚨 **[MAJOR MARKET ALERT]** 🚨\n\n"
    for item in news_items:
        clean_desc = clean_html(item.get('summary', ''))
        short_summary = summarize_text(clean_desc, 2) # Shorter for alerts

        result += f"🔥 **{item['title']}**\n"
        if short_summary and short_summary != "• ":
            result += f"*{short_summary}*\n"
        result += f"[Source]({item['link']})\n\n"
    return result
