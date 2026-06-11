from typing import List
from datetime import datetime, timezone
from src.utils import logger
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

    def rank_items(self, items: List[dict]) -> List[dict]:
        """Rank items by importance"""
        logger.info(f"Ranking {len(items)} items...")

        for item in items:
            score = self._calculate_score(item)
            item['importance_score'] = score

        # Sort by importance score
        items.sort(key=lambda x: x['importance_score'], reverse=True)

        logger.info(f"Ranking complete")
        return items

    def _calculate_score(self, item: dict) -> float:
        """Calculate importance score"""
        score = 1.0

        # Source weight
        source = item.get('source', 'RSS')
        score *= self.source_weights.get(source, 1.0)

        # Competitor mention bonus
        text = (item.get('title', '') + " " + item.get('description', '')).lower()
        if any(comp.lower() in text for comp in COMPETITORS):
            score += self.competitor_score

        # Category importance
        categories = item.get('categories', [])
        high_priority_categories = ['GenerativeAI', 'LLM', 'Security']
        if any(cat in high_priority_categories for cat in categories):
            score += 1.0

        # Recency (items published today get bonus)
        published = item.get('published_at')
        if published:
            try:
                now = datetime.now(timezone.utc)
                # Handle both naive and aware datetimes
                if published.tzinfo is None:
                    published = published.replace(tzinfo=timezone.utc)
                age_hours = (now - published).total_seconds() / 3600
                if age_hours < 24:
                    score += self.recency_score * (1 - age_hours / 24)
            except Exception:
                pass  # If datetime calculation fails, skip recency bonus

        return score
