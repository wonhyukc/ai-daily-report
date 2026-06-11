from typing import List
from src.collectors.base import NewsItem
from .deduplicator import Deduplicator
from .classifier import Classifier
from .ranker import Ranker
from src.utils import logger, contains_word
from config.settings import PROCESSING


class ProcessorPipeline:
    def __init__(self):
        self.deduplicator = Deduplicator()
        self.classifier = Classifier()
        self.ranker = Ranker()

    def process(self, items: List[NewsItem]) -> List[dict]:
        """Process raw news items through the pipeline"""
        logger.info(f"Starting processing pipeline with {len(items)} items...")

        # datetime 정규화는 NewsItem validator가 보장 (UTC aware)

        # Step 1: Deduplication
        logger.info("Step 1: Deduplication")
        unique_items = self.deduplicator.deduplicate(items)

        # Step 1.5: Content filtering
        logger.info("Step 1.5: Content filtering")
        filtered_items = self._filter_items(unique_items)

        # Step 2: Classification
        logger.info("Step 2: Classification")
        classified_items = self.classifier.classify_items(filtered_items)

        # Step 3: Ranking
        logger.info("Step 3: Ranking")
        ranked_items = self.ranker.rank_items(classified_items)

        logger.info(f"Processing complete. Final item count: {len(ranked_items)}")
        return ranked_items

    def _filter_items(self, items: List[NewsItem]) -> List[NewsItem]:
        """PROCESSING 설정 기반 콘텐츠 필터링 (exclude_keywords, min_word_count)"""
        min_words = PROCESSING.get("min_word_count", 0)
        exclude_keywords = PROCESSING.get("exclude_keywords", [])
        kept = []

        for item in items:
            text = f"{item.title} {item.description}"
            if any(contains_word(text, keyword) for keyword in exclude_keywords):
                continue
            # 설명이 있는 항목만 최소 분량 검사 (HN 링크 글은 설명이 비어 있음)
            if item.description and len(item.description.split()) < min_words:
                continue
            kept.append(item)

        logger.info(f"After filtering: {len(kept)} items (removed {len(items) - len(kept)})")
        return kept

    def commit_cache(self):
        """Dedup 캐시 영속화. 리포트 저장이 성공한 뒤에만 호출할 것."""
        self.deduplicator.commit_cache()
