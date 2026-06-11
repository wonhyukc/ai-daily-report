from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, field_validator
from datetime import datetime, timezone


class NewsItem(BaseModel):
    title: str
    description: str
    url: str
    source: str
    published_at: datetime
    image_url: Optional[str] = None
    author: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    @field_validator("published_at")
    @classmethod
    def ensure_timezone_aware(cls, value: datetime) -> datetime:
        """naive datetime은 UTC로 간주 — 이후 단계는 aware를 전제로 동작"""
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


class BaseCollector(ABC):
    def __init__(self, source_name: str):
        self.source_name = source_name

    @abstractmethod
    def collect(self) -> List[NewsItem]:
        """Collect news items from source"""
        pass
