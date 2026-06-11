from datetime import datetime, timedelta, timezone

from src.processors.models import ProcessedItem
from src.processors.ranker import Ranker


def make_processed_item(
    title="quantum breakthrough",
    description="",
    source="RSS",
    categories=None,
    published_at=None,
):
    """경쟁사/고우선 카테고리/최신성 보너스가 없는 중립 아이템"""
    return ProcessedItem(
        title=title,
        description=description,
        url="https://example.com/a",
        source=source,
        categories=categories or [],
        published_at=published_at or datetime(2020, 1, 1, tzinfo=timezone.utc),
    )


class TestSourceWeight:
    def test_arxiv_outweighs_rss(self):
        ranker = Ranker()
        arxiv_score = ranker._calculate_score(make_processed_item(source="ArXiv"))
        rss_score = ranker._calculate_score(make_processed_item(source="RSS"))
        assert arxiv_score == 2.0
        assert rss_score == 1.0

    def test_unknown_source_defaults_to_weight_one(self):
        ranker = Ranker()
        assert ranker._calculate_score(make_processed_item(source="Unknown")) == 1.0


class TestBonuses:
    def test_competitor_mention_adds_bonus(self):
        ranker = Ranker()
        neutral = ranker._calculate_score(make_processed_item())
        with_competitor = ranker._calculate_score(
            make_processed_item(title="OpenAI launches new product")
        )
        assert with_competitor == neutral + ranker.competitor_score

    def test_high_priority_category_adds_bonus(self):
        ranker = Ranker()
        neutral = ranker._calculate_score(make_processed_item())
        with_category = ranker._calculate_score(
            make_processed_item(categories=["Security"])
        )
        assert with_category == neutral + 1.0

    def test_recent_item_gets_recency_bonus(self):
        ranker = Ranker()
        old = ranker._calculate_score(make_processed_item())
        recent = ranker._calculate_score(
            make_processed_item(published_at=datetime.now(timezone.utc))
        )
        assert recent > old
        assert recent <= old + ranker.recency_score

    def test_item_older_than_a_day_gets_no_recency_bonus(self):
        ranker = Ranker()
        two_days_ago = datetime.now(timezone.utc) - timedelta(hours=48)
        assert (
            ranker._calculate_score(make_processed_item(published_at=two_days_ago))
            == 1.0
        )


class TestCompetitorWordBoundary:
    """이슈 #6: 'Meta' ⊂ 'metadata' 같은 경쟁사 매칭 오탐 방지"""

    def test_metadata_does_not_match_meta(self):
        ranker = Ranker()
        score = ranker._calculate_score(
            make_processed_item(title="Improving metadata pipelines")
        )
        assert score == 1.0  # 경쟁사 보너스 없음

    def test_meta_as_word_still_matches(self):
        ranker = Ranker()
        score = ranker._calculate_score(
            make_processed_item(title="Meta announces new research lab")
        )
        assert score == 1.0 + ranker.competitor_score


class TestRankItems:
    def test_items_sorted_by_score_descending(self):
        ranker = Ranker()
        items = [
            make_processed_item(title="low priority item", source="RSS"),
            make_processed_item(title="research paper", source="ArXiv"),
        ]
        ranked = ranker.rank_items(items)
        scores = [item.importance_score for item in ranked]
        assert scores == sorted(scores, reverse=True)
        assert ranked[0].source == "ArXiv"
