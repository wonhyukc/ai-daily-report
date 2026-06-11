from src.analyzers.trend_detector import TrendDetector


class TestTrendDetector:
    def test_top_keywords_counted_by_frequency(self):
        items = [
            {"title": "Alpha Research published", "categories": []},
            {"title": "Alpha Research expands", "categories": []},
            {"title": "Beta launches", "categories": []},
        ]
        trends = TrendDetector().detect_trends(items)
        top = trends["top_keywords"][0]
        assert top["keyword"] == "Alpha Research"
        assert top["count"] == 2

    def test_total_items_reported(self):
        items = [{"title": "Something", "categories": []}] * 3
        trends = TrendDetector().detect_trends(items)
        assert trends["total_items"] == 3

    def test_category_distribution(self):
        items = [
            {"title": "a", "categories": ["LLM", "Security"]},
            {"title": "b", "categories": ["LLM"]},
            {"title": "c", "categories": []},
        ]
        trends = TrendDetector().detect_trends(items)
        assert trends["categories_distribution"]["LLM"] == 2
        assert trends["categories_distribution"]["Security"] == 1

    def test_missing_categories_default_to_other(self):
        items = [{"title": "no categories key"}]
        trends = TrendDetector().detect_trends(items)
        assert trends["categories_distribution"] == {"Other": 1}
