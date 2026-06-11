from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import NewsItem
from .hackernews_collector import HackerNewsCollector
from .arxiv_collector import ArxivCollector
from .rss_collector import RSSCollector
from src.utils import logger
from config.settings import NEWS_SOURCES


class CollectorManager:
    def __init__(self):
        self.collectors = []

    def _init_collectors(self):
        """Initialize enabled collectors"""
        self.collectors = []

        if NEWS_SOURCES.get("hackernews", {}).get("enabled"):
            self.collectors.append(HackerNewsCollector())

        if NEWS_SOURCES.get("arxiv", {}).get("enabled"):
            self.collectors.append(ArxivCollector())

        if NEWS_SOURCES.get("rss_feeds", {}).get("enabled"):
            feeds = NEWS_SOURCES.get("rss_feeds", {}).get("feeds", [])
            if feeds:
                self.collectors.append(RSSCollector(feeds))

    def collect_all(self) -> List[NewsItem]:
        """Collect news from all enabled sources in parallel"""
        logger.info("Starting news collection from all sources...")
        self._init_collectors()

        if not self.collectors:
            logger.warning("No news sources are enabled. Nothing to collect.")
            return []

        all_items = []

        # Use ThreadPoolExecutor for parallel collection
        with ThreadPoolExecutor(max_workers=len(self.collectors)) as executor:
            futures = {executor.submit(collector.collect): collector.source_name
                       for collector in self.collectors}

            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    items = future.result()
                    all_items.extend(items)
                    logger.info(f"✓ {source_name}: {len(items)} items")
                except Exception as e:
                    logger.error(f"✗ {source_name}: {e}")

        logger.info(f"Total collected: {len(all_items)} items")
        return all_items
