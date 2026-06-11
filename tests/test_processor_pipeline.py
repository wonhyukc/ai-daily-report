import pytest

from src.processors import processor_pipeline as pipeline_module
from src.processors import deduplicator as deduplicator_module
from src.processors.processor_pipeline import ProcessorPipeline


@pytest.fixture
def pipeline(tmp_path, monkeypatch):
    """실제 캐시 디렉토리를 건드리지 않는 파이프라인"""
    monkeypatch.setattr(deduplicator_module, "CACHE_DIR", tmp_path)
    return ProcessorPipeline()


class TestContentFiltering:
    """이슈 #8: PROCESSING.exclude_keywords / min_word_count 적용"""

    def test_excluded_keyword_filters_item(self, pipeline, make_item):
        items = [make_item(title="Great sponsored content about AI", description="")]
        assert pipeline._filter_items(items) == []

    def test_exclude_keyword_requires_word_boundary(self, pipeline, make_item):
        # "ad"는 제외 키워드지만 "adapter"는 걸리면 안 됨
        items = [make_item(title="New adapter design for GPUs", description="")]
        assert len(pipeline._filter_items(items)) == 1

    def test_short_description_is_filtered(self, pipeline, make_item):
        items = [make_item(title="Some title", description="too short text")]
        assert pipeline._filter_items(items) == []

    def test_empty_description_is_kept(self, pipeline, make_item):
        # HN 링크 글은 설명이 비어 있음 — 분량 검사 대상 아님
        items = [make_item(title="Show HN: my new AI tool", description="")]
        assert len(pipeline._filter_items(items)) == 1

    def test_long_description_is_kept(self, pipeline, make_item):
        long_desc = " ".join(["word"] * 60)
        items = [make_item(title="Some title", description=long_desc)]
        assert len(pipeline._filter_items(items)) == 1
