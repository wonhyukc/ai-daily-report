from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


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


class BaseCollector(ABC):
    def __init__(self, source_name: str):
        self.source_name = source_name

    @abstractmethod
    def collect(self) -> List[NewsItem]:
        """Collect news items from source"""
        pass
