from typing import List

from src.collectors.base import NewsItem


class ProcessedItem(NewsItem):
    """분류·랭킹을 거친 뉴스 항목.

    파이프라인 중간부터 dict로 타입이 소실되던 문제를 해결하기 위해
    NewsItem을 확장한 타입 모델로 끝까지 전달한다.
    """

    categories: List[str]
    importance_score: float = 0.0
