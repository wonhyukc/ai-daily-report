import feedparser
from typing import List
from datetime import datetime
import time
from .base import NewsItem, BaseCollector
from src.utils import logger


class RSSCollector(BaseCollector):
    def __init__(self, feeds: List[str]):
        super().__init__("RSS")
        self.feeds = feeds

    def collect(self) -> List[NewsItem]:
        logger.info(f"Collecting from {len(self.feeds)} RSS feeds...")
        items = []

        for feed_url in self.feeds:
            try:
                logger.debug(f"Parsing feed: {feed_url}")
                feed = feedparser.parse(feed_url)

                for entry in feed.entries[:10]:  # Get top 10 from each feed
                    try:
                        # Extract published date
                        published_at = datetime.now()
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            published_at = datetime(*entry.published_parsed[:6])
                        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                            published_at = datetime(*entry.updated_parsed[:6])

                        item = NewsItem(
                            title=entry.get('title', ''),
                            description=entry.get('summary', '')[:500],
                            url=entry.get('link', ''),
                            source=self.source_name,
                            published_at=published_at,
                            author=entry.get('author', None)
                        )
                        items.append(item)
                    except Exception as e:
                        logger.debug(f"Error parsing entry: {e}")
                        continue

                time.sleep(1)  # Rate limiting

            except Exception as e:
                logger.error(f"Error parsing RSS feed {feed_url}: {e}")
                continue

        logger.info(f"Collected {len(items)} items from RSS feeds")
        return items
