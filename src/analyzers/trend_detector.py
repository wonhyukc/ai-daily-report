from typing import List, Dict
from collections import Counter
import re
from src.processors.models import ProcessedItem
from src.utils import logger


class TrendDetector:
    def detect_trends(self, items: List[ProcessedItem]) -> Dict:
        """Detect trends from items (Phase 1: simple keyword extraction)"""
        logger.info("Detecting trends...")

        # Extract all keywords from titles
        keywords = []
        stopwords = {"The", "This", "That", "How", "Why", "What", "When", "Where", "And", "With", "For"}
        for item in items:
            # Extract capitalized words (including acronyms like GPT, NVIDIA, OpenAI) as keywords
            words = re.findall(r'\b[A-Z][A-Za-z0-9]*\b', item.title)
            keywords.extend(w for w in words if w not in stopwords)

        # Count keyword frequency
        keyword_counts = Counter(keywords)
        top_keywords = keyword_counts.most_common(20)

        trends = {
            'top_keywords': [{'keyword': k, 'count': v} for k, v in top_keywords],
            'total_items': len(items),
            'categories_distribution': self._get_category_distribution(items),
        }

        logger.info(f"Detected {len(top_keywords)} top keywords")
        return trends

    def _get_category_distribution(self, items: List[ProcessedItem]) -> Dict:
        """Get category distribution"""
        category_counts = Counter()

        for item in items:
            for category in (item.categories or ['Other']):
                category_counts[category] += 1

        return dict(category_counts.most_common(10))
