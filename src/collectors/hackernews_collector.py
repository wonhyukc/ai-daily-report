import requests
from typing import List
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import NewsItem, BaseCollector
from src.utils import logger, contains_word
from config.settings import NEWS_SOURCES


class HackerNewsCollector(BaseCollector):
    def __init__(self):
        super().__init__("HackerNews")
        hn_config = NEWS_SOURCES.get("hackernews", {})
        self.base_url = hn_config.get("base_url", "https://hacker-news.firebaseio.com/v0")
        self.max_stories = hn_config.get("max_stories", 30)
        self.timeout = 10

    def collect(self) -> List[NewsItem]:
        logger.info(f"Collecting from {self.source_name}...")
        items = []

        try:
            # Get top story IDs
            top_stories_url = f"{self.base_url}/topstories.json"
            response = requests.get(top_stories_url, timeout=self.timeout)
            response.raise_for_status()
            story_ids = response.json()[:self.max_stories]

            # Collect story details in parallel
            def fetch_story(story_id):
                try:
                    story_url = f"{self.base_url}/item/{story_id}.json"
                    response = requests.get(story_url, timeout=self.timeout)
                    response.raise_for_status()
                    return response.json()
                except Exception as e:
                    logger.debug(f"Error fetching story {story_id}: {e}")
                    return None

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(fetch_story, story_id): story_id for story_id in story_ids}
                for future in as_completed(futures):
                    story = future.result()
                    if story and self._is_ai_related(story.get("title", "")):
                        story_id = futures[future]
                        story_link = story.get("url") or f"https://news.ycombinator.com/item?id={story_id}"
                        item = NewsItem(
                            title=story.get("title", ""),
                            description=story.get("text", ""),
                            url=story_link,
                            source=self.source_name,
                            published_at=datetime.fromtimestamp(story.get("time", 0), tz=timezone.utc),
                            author=story.get("by", None)
                        )
                        items.append(item)

            logger.info(f"Collected {len(items)} items from {self.source_name}")
            return items

        except Exception as e:
            logger.error(f"Error collecting from {self.source_name}: {e}")
            return []

    def _is_ai_related(self, title: str) -> bool:
        keywords = ["AI", "machine learning", "neural", "LLM", "GPT", "model", "algorithm"]
        return any(contains_word(title, keyword) for keyword in keywords)
