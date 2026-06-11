from datetime import datetime, timezone

from src.analyzers.trend_detector import TrendDetector
from src.processors.models import ProcessedItem


def make_processed_item(title, categories=None):
    return ProcessedItem(
        title=title,
        description="",
        url="https://example.com/a",
        source="RSS",
        published_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        categories=categories if categories is not None else [],
    )


class TestTrendDetector:
    def test_top_keywords_counted_by_frequency(self):
        items = [
            make_processed_item("Alpha Research published"),
            make_processed_item("Alpha Research expands"),
            make_processed_item("Beta launches"),
        ]
        trends = TrendDetector().detect_trends(items)
        top = trends["top_keywords"][0]
        # Single capitalized words are extracted (e.g., "Alpha", not "Alpha Research")
        assert top["keyword"] == "Alpha"
        assert top["count"] == 2

    def test_total_items_reported(self):
        items = [make_processed_item("Something") for _ in range(3)]
        trends = TrendDetector().detect_trends(items)
        assert trends["total_items"] == 3

    def test_category_distribution(self):
        items = [
            make_processed_item("a", categories=["LLM", "Security"]),
            make_processed_item("b", categories=["LLM"]),
            make_processed_item("c", categories=["Other"]),
        ]
        trends = TrendDetector().detect_trends(items)
        assert trends["categories_distribution"]["LLM"] == 2
        assert trends["categories_distribution"]["Security"] == 1

    def test_empty_categories_counted_as_other(self):
        items = [make_processed_item("no categories")]
        trends = TrendDetector().detect_trends(items)
        assert trends["categories_distribution"] == {"Other": 1}
