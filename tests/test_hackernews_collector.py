from src.collectors import hackernews_collector as hn_module
from src.collectors.hackernews_collector import HackerNewsCollector


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def make_fake_get(stories):
    """topstories와 개별 item 요청을 흉내내는 requests.get 대체물"""

    def fake_get(url, timeout=None):
        if url.endswith("/topstories.json"):
            return FakeResponse(list(stories.keys()))
        story_id = int(url.rsplit("/", 1)[-1].removesuffix(".json"))
        return FakeResponse(stories[story_id])

    return fake_get


class TestUrllessStories:
    """이슈 #5: 외부 링크 없는 글(Ask HN 등)은 HN 퍼머링크를 가져야 함"""

    def test_story_without_url_gets_permalink(self, monkeypatch):
        stories = {
            101: {"id": 101, "title": "Ask HN: best LLM stack?", "time": 1700000000, "by": "alice"},
        }
        monkeypatch.setattr(
            hn_module.requests, "get", make_fake_get(stories)
        )
        items = HackerNewsCollector().collect()
        assert len(items) == 1
        assert items[0].url == "https://news.ycombinator.com/item?id=101"

    def test_two_urlless_stories_have_distinct_urls(self, monkeypatch):
        stories = {
            101: {"id": 101, "title": "Ask HN: best LLM stack?", "time": 1700000000},
            102: {"id": 102, "title": "Ask HN: favorite LLM paper?", "time": 1700000100},
        }
        monkeypatch.setattr(
            hn_module.requests, "get", make_fake_get(stories)
        )
        items = HackerNewsCollector().collect()
        assert len(items) == 2
        assert items[0].url != items[1].url

    def test_story_with_url_keeps_original(self, monkeypatch):
        stories = {
            103: {
                "id": 103,
                "title": "New LLM benchmark released",
                "url": "https://example.com/benchmark",
                "time": 1700000000,
            },
        }
        monkeypatch.setattr(
            hn_module.requests, "get", make_fake_get(stories)
        )
        items = HackerNewsCollector().collect()
        assert items[0].url == "https://example.com/benchmark"
