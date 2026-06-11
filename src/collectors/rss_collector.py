import feedparser
from typing import List
from datetime import datetime, timezone
import time
from .base import NewsItem, BaseCollector
from src.utils import logger
from config.settings import NEWS_SOURCES


class RSSCollector(BaseCollector):
    def __init__(self, feeds: List[str]):
        super().__init__("RSS")
        self.feeds = feeds
        self.max_items_per_feed = NEWS_SOURCES.get("rss_feeds", {}).get("max_items_per_feed", 10)

    def collect(self) -> List[NewsItem]:
        logger.info(f"Collecting from {len(self.feeds)} RSS feeds...")
        items = []

        for feed_url in self.feeds:
            try:
                logger.debug(f"Parsing feed: {feed_url}")
                feed = feedparser.parse(feed_url)

                # Issue #14: Check feed status and warn if dead
                status = getattr(feed, 'status', 200)  # Default 200 for mock/test feeds
                if status >= 400:
                    logger.warning(f"Feed {feed_url} returned HTTP {status} (dead feed)")
                    continue
                if not feed.entries:
                    logger.warning(f"Feed {feed_url} returned 0 entries (dead or invalid feed)")
                    continue

                for entry in feed.entries[:self.max_items_per_feed]:
                    try:
                        # Issue #1: DateTime timezone handling (naive/aware mismatch)
                        # 모든 타임스탐프를 UTC aware로 통일하여 naive datetime과의 비교 오류 방지
                        published_at = datetime.now(timezone.utc)
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                            published_at = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

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
