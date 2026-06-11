from typing import List
from datetime import timezone
from src.collectors.base import NewsItem
from .deduplicator import Deduplicator
from .classifier import Classifier
from .ranker import Ranker
from src.utils import logger


class ProcessorPipeline:
    def __init__(self):
        self.deduplicator = Deduplicator()
        self.classifier = Classifier()
        self.ranker = Ranker()

    def _normalize_datetime(self, items: List[NewsItem]) -> List[NewsItem]:
        """Normalize all datetimes to UTC"""
        for item in items:
            if item.published_at.tzinfo is None:
                item.published_at = item.published_at.replace(tzinfo=timezone.utc)
        return items

    def process(self, items: List[NewsItem]) -> List[dict]:
        """Process raw news items through the pipeline"""
        logger.info(f"Starting processing pipeline with {len(items)} items...")

        # Step 0: Normalize datetimes
        items = self._normalize_datetime(items)

        # Step 1: Deduplication
        logger.info("Step 1: Deduplication")
        unique_items = self.deduplicator.deduplicate(items)

        # Step 2: Classification
        logger.info("Step 2: Classification")
        classified_items = self.classifier.classify_items(unique_items)

        # Step 3: Ranking
        logger.info("Step 3: Ranking")
        ranked_items = self.ranker.rank_items(classified_items)

        logger.info(f"Processing complete. Final item count: {len(ranked_items)}")
        return ranked_items

    def commit_cache(self):
        """Dedup 캐시 영속화. 리포트 저장이 성공한 뒤에만 호출할 것."""
        self.deduplicator.commit_cache()
