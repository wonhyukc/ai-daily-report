import requests
from typing import List
from datetime import datetime, timezone
from .base import NewsItem, BaseCollector
from src.utils import logger


class HackerNewsCollector(BaseCollector):
    def __init__(self):
        super().__init__("HackerNews")
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.timeout = 10

    def collect(self) -> List[NewsItem]:
        logger.info(f"Collecting from {self.source_name}...")
        items = []

        try:
            # Get top story IDs
            top_stories_url = f"{self.base_url}/topstories.json"
            response = requests.get(top_stories_url, timeout=self.timeout)
            response.raise_for_status()
            story_ids = response.json()[:30]  # Get top 30

            # Collect story details
            for story_id in story_ids:
                try:
                    story_url = f"{self.base_url}/item/{story_id}.json"
                    response = requests.get(story_url, timeout=self.timeout)
                    response.raise_for_status()
                    story = response.json()

                    # Filter by keywords (AI-related)
                    if self._is_ai_related(story.get("title", "")):
                        # Ask HN 등 외부 링크 없는 글은 HN 퍼머링크로 대체
                        # (빈 URL은 dedup 해시 충돌과 깨진 링크를 유발)
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
                except Exception as e:
                    logger.debug(f"Error collecting story {story_id}: {e}")
                    continue

            logger.info(f"Collected {len(items)} items from {self.source_name}")
            return items

        except Exception as e:
            logger.error(f"Error collecting from {self.source_name}: {e}")
            return []

    def _is_ai_related(self, title: str) -> bool:
        keywords = ["AI", "machine learning", "neural", "LLM", "GPT", "model", "algorithm"]
        return any(keyword.lower() in title.lower() for keyword in keywords)
