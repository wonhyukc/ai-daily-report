import time
from datetime import datetime, timezone

from src.collectors import rss_collector as rss_module
from src.collectors.rss_collector import RSSCollector


class TestNewsItemTimezone:
    """이슈 #1: NewsItem.published_at은 항상 UTC aware여야 함"""

    def test_naive_datetime_is_coerced_to_utc(self, make_item):
        item = make_item(published_at=datetime(2026, 1, 1, 12, 0, 0))  # naive
        assert item.published_at.tzinfo is not None
        assert item.published_at == datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    def test_aware_datetime_is_preserved(self, make_item):
        aware = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        item = make_item(published_at=aware)
        assert item.published_at == aware


class FakeEntry(dict):
    """feedparser 엔트리 흉내 (dict + 속성 접근)"""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


class FakeFeed:
    def __init__(self, entries):
        self.entries = entries


class TestRssCollectorTimezone:
    """이슈 #1: RSS 수집 결과는 UTC aware datetime이어야 함"""

    def test_published_parsed_becomes_utc_aware(self, monkeypatch):
        entry = FakeEntry(
            title="Some article",
            summary="summary",
            link="https://example.com/a",
            published_parsed=time.struct_time((2026, 6, 10, 12, 30, 0, 2, 161, 0)),
        )
        monkeypatch.setattr(
            rss_module.feedparser, "parse", lambda url: FakeFeed([entry])
        )
        monkeypatch.setattr(rss_module.time, "sleep", lambda s: None)

        items = RSSCollector(["https://example.com/feed"]).collect()
        assert len(items) == 1
        assert items[0].published_at == datetime(
            2026, 6, 10, 12, 30, 0, tzinfo=timezone.utc
        )

    def test_entry_without_dates_gets_aware_now(self, monkeypatch):
        entry = FakeEntry(
            title="No date article",
            summary="summary",
            link="https://example.com/b",
        )
        monkeypatch.setattr(
            rss_module.feedparser, "parse", lambda url: FakeFeed([entry])
        )
        monkeypatch.setattr(rss_module.time, "sleep", lambda s: None)

        items = RSSCollector(["https://example.com/feed"]).collect()
        assert items[0].published_at.tzinfo is not None
