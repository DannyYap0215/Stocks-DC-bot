import urllib.request
import json
import re
from collections import Counter

# Common non-ticker words that often get capitalized on WSB
IGNORE_LIST = {"A", "I", "ARE", "ON", "IT", "ALL", "NOW", "THIS", "THE", "IS", "US",
               "WE", "YOU", "TO", "DO", "SO", "OR", "IF", "BE", "AS", "AT", "BY",
               "HE", "MY", "NO", "OF", "UP", "AN", "AM", "ME", "FOR", "AND", "BUT",
               "NOT", "OUT", "HAS", "HAD", "WAS", "DID", "CAN", "DD", "YOLO", "FOMO",
               "PUMP", "DUMP", "CALL", "PUT", "MOON", "WSB", "API", "GDP", "CPI", "USA"}

def extract_tickers(text):
    """Finds words that look like stock tickers (1-5 uppercase letters)"""
    words = re.findall(r'\b[A-Z]{1,5}\b', text)
    return [word for word in words if word not in IGNORE_LIST]

def get_reddit_sentiment(subreddit="wallstreetbets", limit=50):
    """Fetches top posts from a subreddit and calculates most mentioned tickers using an alternative proxy/feed."""

    # Reddit blocks standard User-Agents hard now. To bypass without full API keys,
    # we can use a popular third-party scraper feed or RSS parser, but a simpler robust method
    # is to fetch the public RSS feed using standard library tools, as RSS is rarely blocked 403.
    import feedparser

    url = f"https://www.reddit.com/r/{subreddit}/hot/.rss?limit={limit}"

    try:
        feed = feedparser.parse(url)
        if not feed.entries:
             return "❌ Error fetching Reddit data. Reddit may be blocking the request."

        all_tickers = []
        for entry in feed.entries:
            title = entry.get('title', '')
            summary = entry.get('summary', '')

            all_tickers.extend(extract_tickers(title))
            all_tickers.extend(extract_tickers(summary))

        counter = Counter(all_tickers)
        top_tickers = counter.most_common(5)

        if not top_tickers:
            return f"Couldn't find enough ticker mentions in r/{subreddit} today."

        result = f"🦍 **Top Trending on r/{subreddit}** 🦍\n\n"
        for i, (ticker, count) in enumerate(top_tickers):
            # Very basic mock sentiment - the more it's talked about, the more "hype" it has
            hype_meter = "🔥" * min(5, (count // 2) + 1)
            result += f"**{i+1}. {ticker}** - {count} mentions {hype_meter}\n"

        return result

    except Exception as e:
        print(f"Error parsing Reddit RSS: {e}")
        return "❌ Error fetching Reddit data."
