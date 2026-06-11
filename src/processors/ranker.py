from typing import List
from datetime import datetime, timezone
from src.processors.models import ProcessedItem
from src.utils import logger, contains_word
from config.settings import COMPETITORS


class Ranker:
    def __init__(self):
        self.competitor_score = 3  # Bonus for competitor mentions
        self.recency_score = 2  # Bonus for recent items
        self.source_weights = {
            "ArXiv": 2.0,
            "HackerNews": 1.5,
            "RSS": 1.0,
        }

    def rank_items(self, items: List[ProcessedItem]) -> List[ProcessedItem]:
        """Rank items by importance"""
        logger.info(f"Ranking {len(items)} items...")

        for item in items:
            item.importance_score = self._calculate_score(item)

        # Sort by importance score
        items.sort(key=lambda x: x.importance_score, reverse=True)

        logger.info(f"Ranking complete")
        return items

    def _calculate_score(self, item: ProcessedItem) -> float:
        """Calculate importance score"""
        score = 1.0

        # Source weight
        score *= self.source_weights.get(item.source, 1.0)

        # Competitor mention bonus
        text = item.title + " " + item.description
        if any(contains_word(text, comp) for comp in COMPETITORS):
            score += self.competitor_score

        # Category importance
        high_priority_categories = ['GenerativeAI', 'LLM', 'Security']
        if any(cat in high_priority_categories for cat in item.categories):
            score += 1.0

        # Recency (items published today get bonus)
        # published_at은 NewsItem validator가 UTC aware를 보장
        if item.published_at:
            try:
                now = datetime.now(timezone.utc)
                age_hours = (now - item.published_at).total_seconds() / 3600
                if age_hours < 24:
                    score += self.recency_score * (1 - age_hours / 24)
            except Exception:
                pass  # If datetime calculation fails, skip recency bonus

        return score
