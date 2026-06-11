from datetime import datetime, timezone

from src.generators.html_generator import HTMLGenerator
from src.processors.models import ProcessedItem


def make_processed_item(**overrides):
    fields = {
        "title": "Sample article",
        "description": "description",
        "url": "https://example.com/a",
        "source": "RSS",
        "published_at": datetime(2026, 6, 10, tzinfo=timezone.utc),
        "categories": ["LLM"],
        "importance_score": 1.0,
    }
    fields.update(overrides)
    return ProcessedItem(**fields)


SAMPLE_TRENDS = {
    "top_keywords": [
        {"keyword": "Claude", "count": 5},
        {"keyword": "Open Source", "count": 3},
    ],
    "total_items": 2,
    "categories_distribution": {"LLM": 2, "Security": 1},
}


class TestTrendsSection:
    """이슈 #4: 트렌드 분석 결과가 HTML 리포트에 포함되어야 함"""

    def test_trends_section_rendered(self):
        html = HTMLGenerator().generate([make_processed_item()], trends=SAMPLE_TRENDS)
        assert "트렌드 분석" in html
        assert "Claude" in html
        assert "Open Source" in html

    def test_category_distribution_rendered(self):
        html = HTMLGenerator().generate([make_processed_item()], trends=SAMPLE_TRENDS)
        assert "Security" in html

    def test_generate_without_trends_still_works(self):
        html = HTMLGenerator().generate([make_processed_item()])
        assert "Sample article" in html
        assert "트렌드 분석" not in html
