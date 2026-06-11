import pytest

from src.processors import deduplicator as deduplicator_module
from src.processors.deduplicator import Deduplicator


@pytest.fixture
def cache_dir(tmp_path, monkeypatch):
    """Deduplicator가 임시 디렉토리를 캐시 경로로 쓰도록 격리"""
    monkeypatch.setattr(deduplicator_module, "CACHE_DIR", tmp_path)
    return tmp_path


class TestUrlHash:
    def test_protocol_and_www_are_normalized(self, cache_dir):
        d = Deduplicator()
        assert d._get_url_hash("https://www.example.com/a") == d._get_url_hash(
            "http://example.com/a"
        )

    def test_different_urls_have_different_hashes(self, cache_dir):
        d = Deduplicator()
        assert d._get_url_hash("https://example.com/a") != d._get_url_hash(
            "https://example.com/b"
        )


class TestDeduplicate:
    def test_first_run_keeps_all_unique_items(self, cache_dir, make_item):
        d = Deduplicator()
        items = [
            make_item(url="https://example.com/1"),
            make_item(url="https://example.com/2"),
        ]
        assert len(d.deduplicate(items)) == 2

    def test_items_seen_in_previous_run_are_filtered(self, cache_dir, make_item):
        first = Deduplicator()
        first.deduplicate([make_item(url="https://example.com/1")])

        second = Deduplicator()
        result = second.deduplicate(
            [
                make_item(url="https://example.com/1"),
                make_item(url="https://example.com/2"),
            ]
        )
        assert len(result) == 1
        assert result[0].url == "https://example.com/2"

    def test_cache_file_is_persisted(self, cache_dir, make_item):
        d = Deduplicator()
        d.deduplicate([make_item(url="https://example.com/1")])
        cache_file = cache_dir / "url_hashes.txt"
        assert cache_file.exists()
        assert len(cache_file.read_text(encoding="utf-8").strip().splitlines()) == 1
