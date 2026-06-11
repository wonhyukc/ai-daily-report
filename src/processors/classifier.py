from typing import List
from src.collectors.base import NewsItem
from src.utils import logger
from config.settings import CATEGORIES


class Classifier:
    def classify_items(self, items: List[NewsItem]) -> List[dict]:
        """Classify items into categories"""
        logger.info(f"Classifying {len(items)} items...")
        classified = []

        for item in items:
            categories = self._classify_text(item.title + " " + item.description)
            classified.append({
                **item.dict(),
                "categories": categories
            })

        logger.info(f"Classification complete")
        return classified

    def _classify_text(self, text: str) -> List[str]:
        """Classify text into categories based on keywords"""
        text_lower = text.lower()
        matched_categories = []

        for category, keywords in CATEGORIES.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                matched_categories.append(category)

        return matched_categories if matched_categories else ["Other"]
