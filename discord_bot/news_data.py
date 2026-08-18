import feedparser
import datetime
import time

# List of RSS feeds for financial news
NEWS_FEEDS = [
    "https://finance.yahoo.com/news/rssindex",
    # Add more feeds if needed
]

import re

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
        # Keep only the last 500 (this is a simple approach, a queue or timestamp-based cleanup is better for production)
        seen_news_links = set(list(seen_news_links)[-500:])

    return major_news_alerts

def get_daily_news_summary():
    """Gets a summary of recent general news."""
    latest_news = fetch_latest_news()
    if not latest_news:
        return "Could not fetch news at this time."

    summary = "**Latest Financial News Summary:**\n\n"
    # Just take the top 5 recent news articles
    for i, item in enumerate(latest_news[:5]):
        summary += f"**{item['title']}**\n{item['link']}\n\n"

    return summary
