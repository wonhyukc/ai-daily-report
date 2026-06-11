import hashlib
from typing import List, Set
from pathlib import Path
from datetime import datetime, timedelta
from src.collectors.base import NewsItem
from src.utils import logger
from config.settings import CACHE_DIR


class Deduplicator:
    def __init__(self):
        self.cache_file = CACHE_DIR / "url_hashes.txt"
        self.cache = self._load_cache()
        self._pending_hashes: Set[str] = set()

    def _load_cache(self) -> Set[str]:
        """Load previously seen URLs from cache"""
        if self.cache_file.exists():
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return set(line.strip() for line in f if line.strip())
        return set()

    def _save_cache(self):
        """Save cache to file"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            for hash_val in self.cache:
                f.write(f"{hash_val}\n")

    def _get_url_hash(self, url: str) -> str:
        """Generate hash of normalized URL"""
        normalized = url.lower().replace("https://", "").replace("http://", "").replace("www.", "")
        return hashlib.md5(normalized.encode()).hexdigest()

    def deduplicate(self, items: List[NewsItem]) -> List[NewsItem]:
        """Remove duplicate items.

        새로 본 해시는 pending에만 쌓이고, commit_cache()가 호출되기 전에는
        영속되지 않는다. 파이프라인 후속 단계가 실패하거나 DRY_RUN이면
        커밋하지 않음으로써 기사가 영구 유실되는 것을 방지한다.
        """
        logger.info(f"Deduplicating {len(items)} items...")
        unique_items = []

        for item in items:
            url_hash = self._get_url_hash(item.url)

            if url_hash not in self.cache and url_hash not in self._pending_hashes:
                unique_items.append(item)
                self._pending_hashes.add(url_hash)

        logger.info(f"After deduplication: {len(unique_items)} unique items (removed {len(items) - len(unique_items)})")
        return unique_items

    def commit_cache(self):
        """Persist pending hashes. 리포트 저장이 성공한 뒤에만 호출할 것."""
        if not self._pending_hashes:
            return
        self.cache.update(self._pending_hashes)
        self._save_cache()
        logger.info(f"Dedup cache committed ({len(self._pending_hashes)} new entries)")
        self._pending_hashes = set()
