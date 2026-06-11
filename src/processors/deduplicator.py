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
        """Remove duplicate items"""
        logger.info(f"Deduplicating {len(items)} items...")
        unique_items = []
        new_hashes = []

        for item in items:
            url_hash = self._get_url_hash(item.url)

            if url_hash not in self.cache:
                unique_items.append(item)
                new_hashes.append(url_hash)

        self.cache.update(new_hashes)
        self._save_cache()

        logger.info(f"After deduplication: {len(unique_items)} unique items (removed {len(items) - len(unique_items)})")
        return unique_items
