from typing import List
from src.collectors.base import NewsItem
from src.processors.models import ProcessedItem
from src.utils import logger, contains_word
from config.settings import CATEGORIES


class Classifier:
    def classify_items(self, items: List[NewsItem]) -> List[ProcessedItem]:
        """Classify items into categories"""
        logger.info(f"Classifying {len(items)} items...")
        classified = []

        for item in items:
            categories = self._classify_text(item.title + " " + item.description)
            classified.append(
                ProcessedItem(**item.model_dump(), categories=categories)
            )

        logger.info(f"Classification complete")
        return classified

    def _classify_text(self, text: str) -> List[str]:
        """Classify text into categories based on keywords"""
        # Issue #6: Substring keyword matching causes false positives
        # contains_word()로 단어 경계 매칭 사용 (부분문자열 매칭 방지)
        # 예: "anthropic" 검색 시 "misanthropic"에 매칭되지 않음
        matched_categories = []

        for category, keywords in CATEGORIES.items():
            if any(contains_word(text, keyword) for keyword in keywords):
                matched_categories.append(category)

        return matched_categories if matched_categories else ["Other"]
