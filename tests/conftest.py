from datetime import datetime, timezone

import pytest

from src.collectors.base import NewsItem


@pytest.fixture
def make_item():
    """NewsItem 팩토리. 필요한 필드만 덮어쓰고 나머지는 기본값 사용."""

    def _make(
        title="Sample Title",
        description="Sample description",
        url="https://example.com/article",
        source="RSS",
        published_at=None,
        **kwargs,
    ):
        return NewsItem(
            title=title,
            description=description,
            url=url,
            source=source,
            published_at=published_at or datetime(2020, 1, 1, tzinfo=timezone.utc),
            **kwargs,
        )

    return _make
