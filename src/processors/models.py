from typing import List

from src.collectors.base import NewsItem


class ProcessedItem(NewsItem):
    """분류·랭킹을 거친 뉴스 항목.

    Issue #11: Preserve typed models through pipeline
    파이프라인 중간부터 dict로 타입이 소실되던 문제를 해결하기 위해
    NewsItem을 확장한 타입 모델로 끝까지 전달한다.

    규칙:
    - 새 필드 추가 시 여기서 먼저 정의
    - dict로 변환하지 말 것 (model_dump() 사용 시만 예외)
    """

    categories: List[str]
    importance_score: float = 0.0
