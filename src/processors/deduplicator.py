import hashlib
from typing import Dict, List, Set
from pathlib import Path
from datetime import datetime, timedelta, timezone
from src.collectors.base import NewsItem
from src.utils import logger
from config.settings import CACHE_DIR, PROCESSING


class Deduplicator:
    def __init__(self):
        self.cache_file = CACHE_DIR / "url_hashes.txt"
        self.ttl = timedelta(hours=PROCESSING.get("cache_ttl_hours", 24))
        self.cache = self._load_cache()
        self._pending_hashes: Set[str] = set()

    def _load_cache(self) -> Dict[str, datetime]:
        """Load previously seen URL hashes, dropping entries older than TTL.

        포맷: "{hash}\t{ISO timestamp}" — 타임스탬프 없는 레거시 줄은
        현재 시각으로 간주해 유지한다 (오래된 기사 일괄 재노출 방지).
        """
        if not self.cache_file.exists():
            return {}

        now = datetime.now(timezone.utc)
        entries: Dict[str, datetime] = {}
        with open(self.cache_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                hash_val, _, ts_raw = line.partition("\t")
                try:
                    seen_at = datetime.fromisoformat(ts_raw) if ts_raw else now
                except ValueError:
                    seen_at = now
                if now - seen_at <= self.ttl:
                    entries[hash_val] = seen_at
        return entries

    def _save_cache(self):
        """Save cache to file"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            for hash_val, seen_at in self.cache.items():
                f.write(f"{hash_val}\t{seen_at.isoformat()}\n")

    def _get_url_hash(self, url: str) -> str:
        """Generate hash of normalized URL"""
        # Issue #5: URL 없는 HackerNews 글의 dedup 해시 충돌 해결
        # URL을 정규화하여 http://example.com ≈ https://www.example.com 으로 취급
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
            # Issue #5: HackerNews 항목 중 URL이 없는 경우 source:title로 대체 해싱
            # 이렇게 하면 URL 없는 여러 항목이 같은 빈 문자열로 충돌하지 않음
            hash_source = item.url or f"{item.source}:{item.title}"
            url_hash = self._get_url_hash(hash_source)

            if url_hash not in self.cache and url_hash not in self._pending_hashes:
                unique_items.append(item)
                self._pending_hashes.add(url_hash)

        logger.info(f"After deduplication: {len(unique_items)} unique items (removed {len(items) - len(unique_items)})")
        return unique_items

    def commit_cache(self):
        """Persist pending hashes. 리포트 저장이 성공한 뒤에만 호출할 것."""
        if not self._pending_hashes:
            return
        now = datetime.now(timezone.utc)
        for hash_val in self._pending_hashes:
            self.cache[hash_val] = now
        self._save_cache()
        logger.info(f"Dedup cache committed ({len(self._pending_hashes)} new entries)")
        self._pending_hashes = set()
