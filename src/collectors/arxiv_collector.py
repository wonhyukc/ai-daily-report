import arxiv
from typing import List
from datetime import datetime, timedelta, timezone
from .base import NewsItem, BaseCollector
from src.utils import logger
from config.settings import NEWS_SOURCES


class ArxivCollector(BaseCollector):
    def __init__(self):
        super().__init__("ArXiv")
        arxiv_config = NEWS_SOURCES.get("arxiv", {})
        self.categories = arxiv_config.get("categories", ["cs.AI", "cs.LG", "stat.ML"])
        self.max_results = arxiv_config.get("max_results", 50)

    def collect(self) -> List[NewsItem]:
        logger.info(f"Collecting from {self.source_name}...")
        items = []

        try:
            client = arxiv.Client()

            for category in self.categories:
                try:
                    # Search for recent papers in this category
                    search = arxiv.Search(
                        query=f"cat:{category}",
                        sort_by=arxiv.SortCriterion.SubmittedDate,
                        sort_order=arxiv.SortOrder.Descending,
                        max_results=self.max_results // len(self.categories)
                    )

                    for result in client.results(search):
                        item = NewsItem(
                            title=result.title,
                            description=result.summary[:500],  # Limit description
                            url=result.entry_id,
                            source=self.source_name,
                            published_at=result.published,
                            author=", ".join([author.name for author in result.authors[:3]])
                        )
                        items.append(item)
                except Exception as e:
                    logger.debug(f"Error searching ArXiv category {category}: {e}")
                    continue

            logger.info(f"Collected {len(items)} items from {self.source_name}")
            return items

        except Exception as e:
            logger.error(f"Error collecting from {self.source_name}: {e}")
            return []
