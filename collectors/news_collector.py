import feedparser

RSS_FEEDS = [
    ("Reuters Business", "https://feeds.reuters.com/reuters/businessNews"),
    ("BBC Business", "http://feeds.bbci.co.uk/news/business/rss.xml"),
    ("Yahoo Finance", "https://finance.yahoo.com/rss/topstories"),
    ("CNBC Markets", "https://www.cnbc.com/id/20910258/device/rss/rss.html"),
    ("MarketWatch", "http://feeds.marketwatch.com/marketwatch/topstories/"),
    ("Investing.com", "https://www.investing.com/rss/news.rss"),
]


def get_news(max_per_feed=4):
    all_news = []
    for source, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_feed]:
                summary = entry.get("summary", entry.get("description", ""))
                # Clean up HTML tags from summary
                import re
                summary = re.sub(r"<[^>]+>", "", summary)[:300]
                all_news.append(
                    {
                        "source": source,
                        "title": entry.get("title", "No title"),
                        "summary": summary.strip(),
                        "link": entry.get("link", ""),
                        "published": entry.get("published", ""),
                    }
                )
        except Exception as e:
            print(f"  Error fetching news from {source}: {e}")
    return all_news
