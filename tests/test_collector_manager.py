import pytest

from src.collectors import collector_manager as collector_manager_module
from src.collectors.collector_manager import CollectorManager

ALL_DISABLED = {
    "hackernews": {"enabled": False},
    "arxiv": {"enabled": False},
    "rss_feeds": {"enabled": False},
}


class TestCollectAll:
    def test_returns_empty_list_when_all_sources_disabled(self, monkeypatch):
        """이슈 #7: 모든 소스 비활성화 시 max_workers=0 ValueError가 나면 안 됨"""
        monkeypatch.setattr(collector_manager_module, "NEWS_SOURCES", ALL_DISABLED)
        manager = CollectorManager()
        assert manager.collect_all() == []
