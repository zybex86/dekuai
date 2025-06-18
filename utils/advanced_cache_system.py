"""
🚀 FAZA 6.1 - KROK 2: Advanced Caching System
Multi-level persistent cache with smart invalidation

Features:
- Persistent file-based cache between sessions
- TTL (Time-to-Live) with smart expiration policies
- Multi-level cache hierarchy (memory + disk)
- Cache warming for popular games
- Cache statistics and performance analytics
"""

import os
import json
import pickle
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Single cache entry with metadata."""

    data: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl_seconds: int
    game_name: str
    data_hash: str

    def is_expired(self) -> bool:
        """Check if cache entry has expired based on TTL."""
        if self.ttl_seconds <= 0:  # No expiration
            return False
        return datetime.now() > (self.created_at + timedelta(seconds=self.ttl_seconds))

    def is_stale(self, max_age_hours: int = 24) -> bool:
        """Check if cache entry is considered stale."""
        return datetime.now() > (self.created_at + timedelta(hours=max_age_hours))

    def update_access(self):
        """Update access statistics."""
        self.last_accessed = datetime.now()
        self.access_count += 1


@dataclass
class CacheStats:
    """Cache performance statistics."""

    memory_hits: int = 0
    disk_hits: int = 0
    misses: int = 0
    expired_entries: int = 0
    evictions: int = 0
    total_requests: int = 0
    cache_size_memory: int = 0
    cache_size_disk: int = 0
    hit_rate: float = 0.0
    average_retrieval_time: float = 0.0

    def calculate_hit_rate(self):
        """Calculate overall cache hit rate."""
        if self.total_requests == 0:
            self.hit_rate = 0.0
        else:
            hits = self.memory_hits + self.disk_hits
            self.hit_rate = (hits / self.total_requests) * 100


class AdvancedCacheSystem:
    """
    🚀 FAZA 6.1 - KROK 2: Multi-level persistent cache system

    Architecture:
    - Level 1 (Memory): Fast access, limited size (100 entries)
    - Level 2 (Disk): Persistent storage, larger capacity (1000 entries)
    - Smart eviction: LRU + access frequency + TTL
    - Auto-cleanup: Expired entries removal
    """

    def __init__(
        self,
        cache_dir: str = "cache",
        memory_size_limit: int = 100,
        disk_size_limit: int = 1000,
        default_ttl_hours: int = 24,
        enable_warming: bool = True,
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # Cache configuration
        self.memory_size_limit = memory_size_limit
        self.disk_size_limit = disk_size_limit
        self.default_ttl_seconds = default_ttl_hours * 3600
        self.enable_warming = enable_warming

        # Multi-level cache storage
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._disk_cache_index: Dict[str, str] = {}  # key -> filename mapping

        # Performance tracking
        self.stats = CacheStats()
        self._lock = threading.RLock()

        # Popular games for cache warming
        self.popular_games = [
            "Zelda Tears of the Kingdom",
            "Super Mario Odyssey",
            "Hollow Knight",
            "Celeste",
            "Hades",
            "Stardew Valley",
            "Animal Crossing",
            "Mario Kart 8",
            "Metroid Dread",
            "Super Mario Bros Wonder",
            "Kirby",
            "Splatoon 3",
        ]

        # Initialize system
        self._load_disk_cache_index()
        self._cleanup_expired_entries()

        if self.enable_warming:
            self._warm_cache_async()

        logger.info(
            f"✅ Advanced Cache System initialized: memory={memory_size_limit}, disk={disk_size_limit}"
        )

    def get(self, key: str, game_name: str = "") -> Optional[Any]:
        """
        Retrieve data from multi-level cache.

        Search order: Memory → Disk → None
        """
        start_time = time.time()

        with self._lock:
            self.stats.total_requests += 1
            cache_key = self._normalize_key(key)

            # Level 1: Memory cache
            if cache_key in self._memory_cache:
                entry = self._memory_cache[cache_key]

                if entry.is_expired():
                    self._evict_from_memory(cache_key)
                    self.stats.expired_entries += 1
                else:
                    entry.update_access()
                    self.stats.memory_hits += 1
                    self._update_retrieval_time(start_time)
                    logger.debug(
                        f"💾 Memory cache HIT for '{key}' (access #{entry.access_count})"
                    )
                    return entry.data

            # Level 2: Disk cache
            if cache_key in self._disk_cache_index:
                entry = self._load_from_disk(cache_key)

                if entry and not entry.is_expired():
                    entry.update_access()
                    self.stats.disk_hits += 1

                    # Promote to memory cache
                    self._promote_to_memory(cache_key, entry)

                    self._update_retrieval_time(start_time)
                    logger.debug(f"💿 Disk cache HIT for '{key}' (promoted to memory)")
                    return entry.data
                elif entry:
                    # Expired disk entry
                    self._evict_from_disk(cache_key)
                    self.stats.expired_entries += 1

            # Cache miss
            self.stats.misses += 1
            logger.debug(f"🔍 Cache MISS for '{key}'")
            return None

    def put(
        self, key: str, data: Any, game_name: str = "", ttl_hours: Optional[int] = None
    ) -> bool:
        """
        Store data in multi-level cache.

        Strategy: Always store in memory, optionally persist to disk
        """
        with self._lock:
            cache_key = self._normalize_key(key)
            ttl_seconds = (ttl_hours or (self.default_ttl_seconds // 3600)) * 3600

            # Create cache entry
            entry = CacheEntry(
                data=data,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                ttl_seconds=ttl_seconds,
                game_name=game_name or key,
                data_hash=self._calculate_hash(data),
            )

            # Store in memory cache
            self._store_in_memory(cache_key, entry)

            # Store in disk cache for persistence
            if self._should_persist_to_disk(entry):
                self._store_in_disk(cache_key, entry)

            logger.debug(
                f"💾 Cached '{key}' (TTL: {ttl_hours or self.default_ttl_seconds//3600}h)"
            )
            return True

    def _store_in_memory(self, cache_key: str, entry: CacheEntry):
        """Store entry in memory cache with LRU eviction."""
        # Check memory limit
        if len(self._memory_cache) >= self.memory_size_limit:
            self._evict_lru_from_memory()

        self._memory_cache[cache_key] = entry
        self.stats.cache_size_memory = len(self._memory_cache)

    def _store_in_disk(self, cache_key: str, entry: CacheEntry):
        """Store entry in persistent disk cache."""
        try:
            # Check disk limit
            if len(self._disk_cache_index) >= self.disk_size_limit:
                self._evict_lru_from_disk()

            filename = f"cache_{cache_key}.pkl"
            filepath = self.cache_dir / filename

            with open(filepath, "wb") as f:
                pickle.dump(entry, f)

            self._disk_cache_index[cache_key] = filename
            self.stats.cache_size_disk = len(self._disk_cache_index)

            # Update disk index
            self._save_disk_cache_index()

        except Exception as e:
            logger.error(f"Failed to store to disk cache: {e}")

    def _load_from_disk(self, cache_key: str) -> Optional[CacheEntry]:
        """Load entry from disk cache."""
        try:
            if cache_key not in self._disk_cache_index:
                return None

            filename = self._disk_cache_index[cache_key]
            filepath = self.cache_dir / filename

            if not filepath.exists():
                # Cleanup stale index entry
                del self._disk_cache_index[cache_key]
                return None

            with open(filepath, "rb") as f:
                entry = pickle.load(f)

            return entry

        except Exception as e:
            logger.error(f"Failed to load from disk cache: {e}")
            return None

    def _promote_to_memory(self, cache_key: str, entry: CacheEntry):
        """Promote disk cache entry to memory cache."""
        if len(self._memory_cache) >= self.memory_size_limit:
            self._evict_lru_from_memory()

        self._memory_cache[cache_key] = entry
        self.stats.cache_size_memory = len(self._memory_cache)

    def _evict_lru_from_memory(self):
        """Evict least recently used entry from memory cache."""
        if not self._memory_cache:
            return

        # Find LRU entry
        lru_key = min(
            self._memory_cache.keys(),
            key=lambda k: (
                self._memory_cache[k].last_accessed,
                -self._memory_cache[k].access_count,  # Prefer frequently accessed
            ),
        )

        self._evict_from_memory(lru_key)

    def _evict_lru_from_disk(self):
        """Evict least recently used entry from disk cache."""
        if not self._disk_cache_index:
            return

        # Load entries to compare access times
        entries_with_keys = []
        for cache_key in list(self._disk_cache_index.keys())[
            :10
        ]:  # Sample for performance
            entry = self._load_from_disk(cache_key)
            if entry:
                entries_with_keys.append((cache_key, entry))

        if entries_with_keys:
            # Find LRU entry from sample
            lru_key, _ = min(
                entries_with_keys,
                key=lambda x: (x[1].last_accessed, -x[1].access_count),
            )
            self._evict_from_disk(lru_key)

    def _evict_from_memory(self, cache_key: str):
        """Remove entry from memory cache."""
        if cache_key in self._memory_cache:
            del self._memory_cache[cache_key]
            self.stats.evictions += 1
            self.stats.cache_size_memory = len(self._memory_cache)

    def _evict_from_disk(self, cache_key: str):
        """Remove entry from disk cache."""
        try:
            if cache_key in self._disk_cache_index:
                filename = self._disk_cache_index[cache_key]
                filepath = self.cache_dir / filename

                if filepath.exists():
                    filepath.unlink()

                del self._disk_cache_index[cache_key]
                self.stats.evictions += 1
                self.stats.cache_size_disk = len(self._disk_cache_index)

                self._save_disk_cache_index()

        except Exception as e:
            logger.error(f"Failed to evict from disk: {e}")

    def _cleanup_expired_entries(self):
        """Remove expired entries from both cache levels."""
        current_time = datetime.now()

        # Cleanup memory cache
        expired_memory_keys = [
            key for key, entry in self._memory_cache.items() if entry.is_expired()
        ]

        for key in expired_memory_keys:
            self._evict_from_memory(key)

        # Cleanup disk cache (sample check for performance)
        sample_disk_keys = list(self._disk_cache_index.keys())[:20]
        for cache_key in sample_disk_keys:
            entry = self._load_from_disk(cache_key)
            if entry and entry.is_expired():
                self._evict_from_disk(cache_key)

        if expired_memory_keys or sample_disk_keys:
            logger.info(
                f"🧹 Cleaned up {len(expired_memory_keys)} expired memory entries"
            )

    def _should_persist_to_disk(self, entry: CacheEntry) -> bool:
        """Determine if entry should be persisted to disk."""
        # Persist if:
        # 1. TTL > 1 hour (worth persisting)
        # 2. Popular game
        # 3. Large data size

        if entry.ttl_seconds > 3600:  # > 1 hour
            return True

        if any(
            popular in entry.game_name.lower()
            for popular in ["zelda", "mario", "hollow", "celeste", "hades"]
        ):
            return True

        return False

    def _warm_cache_async(self):
        """Asynchronously warm cache with popular games."""

        def warm_cache():
            try:
                from agent_tools import search_and_scrape_game

                logger.info("🔥 Starting cache warming for popular games...")

                for game in self.popular_games[:5]:  # Limit initial warming
                    cache_key = self._normalize_key(game)

                    if (
                        cache_key not in self._memory_cache
                        and cache_key not in self._disk_cache_index
                    ):
                        try:
                            # This would trigger actual scraping and caching
                            # For now, just log the intent
                            logger.debug(f"🔥 Would warm cache for: {game}")
                            time.sleep(0.1)  # Avoid overwhelming
                        except Exception as e:
                            logger.debug(f"Cache warming failed for {game}: {e}")

                logger.info("✅ Cache warming completed")

            except Exception as e:
                logger.error(f"Cache warming error: {e}")

        # Run in background thread
        warming_thread = threading.Thread(target=warm_cache, daemon=True)
        warming_thread.start()

    def _load_disk_cache_index(self):
        """Load disk cache index from file."""
        index_file = self.cache_dir / "cache_index.json"

        try:
            if index_file.exists():
                with open(index_file, "r") as f:
                    self._disk_cache_index = json.load(f)
                logger.info(
                    f"📂 Loaded disk cache index: {len(self._disk_cache_index)} entries"
                )
        except Exception as e:
            logger.error(f"Failed to load cache index: {e}")
            self._disk_cache_index = {}

    def _save_disk_cache_index(self):
        """Save disk cache index to file."""
        index_file = self.cache_dir / "cache_index.json"

        try:
            with open(index_file, "w") as f:
                json.dump(self._disk_cache_index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")

    def _normalize_key(self, key: str) -> str:
        """Normalize cache key for consistency."""
        return key.lower().strip().replace(" ", "_")

    def _calculate_hash(self, data: Any) -> str:
        """Calculate hash of data for integrity checking."""
        try:
            data_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.md5(data_str.encode()).hexdigest()
        except:
            return hashlib.md5(str(data).encode()).hexdigest()

    def _update_retrieval_time(self, start_time: float):
        """Update average retrieval time statistics."""
        retrieval_time = time.time() - start_time

        if self.stats.average_retrieval_time == 0:
            self.stats.average_retrieval_time = retrieval_time
        else:
            # Exponential moving average
            self.stats.average_retrieval_time = (
                0.9 * self.stats.average_retrieval_time + 0.1 * retrieval_time
            )

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache performance statistics."""
        self.stats.calculate_hit_rate()

        return {
            "cache_performance": {
                "total_requests": self.stats.total_requests,
                "memory_hits": self.stats.memory_hits,
                "disk_hits": self.stats.disk_hits,
                "misses": self.stats.misses,
                "hit_rate": f"{self.stats.hit_rate:.2f}%",
                "average_retrieval_time": f"{self.stats.average_retrieval_time*1000:.2f}ms",
            },
            "cache_status": {
                "memory_size": f"{self.stats.cache_size_memory}/{self.memory_size_limit}",
                "disk_size": f"{self.stats.cache_size_disk}/{self.disk_size_limit}",
                "expired_entries_cleaned": self.stats.expired_entries,
                "total_evictions": self.stats.evictions,
            },
            "cache_health": {
                "memory_usage": f"{(self.stats.cache_size_memory/self.memory_size_limit)*100:.1f}%",
                "disk_usage": f"{(self.stats.cache_size_disk/self.disk_size_limit)*100:.1f}%",
                "efficiency": (
                    "HIGH"
                    if self.stats.hit_rate > 70
                    else "MEDIUM" if self.stats.hit_rate > 40 else "LOW"
                ),
            },
        }

    def invalidate_game(self, game_name: str):
        """Invalidate all cache entries for a specific game."""
        invalidated = 0

        # Invalidate from memory
        keys_to_remove = [
            key
            for key, entry in self._memory_cache.items()
            if game_name.lower() in entry.game_name.lower()
        ]

        for key in keys_to_remove:
            self._evict_from_memory(key)
            invalidated += 1

        # Invalidate from disk (sample check)
        sample_keys = list(self._disk_cache_index.keys())[:50]
        for cache_key in sample_keys:
            entry = self._load_from_disk(cache_key)
            if entry and game_name.lower() in entry.game_name.lower():
                self._evict_from_disk(cache_key)
                invalidated += 1

        logger.info(f"🗑️ Invalidated {invalidated} cache entries for '{game_name}'")
        return invalidated

    def clear_all_cache(self):
        """Clear all cache data (emergency cleanup)."""
        # Clear memory
        memory_count = len(self._memory_cache)
        self._memory_cache.clear()

        # Clear disk
        disk_count = len(self._disk_cache_index)
        for filename in self._disk_cache_index.values():
            filepath = self.cache_dir / filename
            if filepath.exists():
                filepath.unlink()

        self._disk_cache_index.clear()
        self._save_disk_cache_index()

        # Reset stats
        self.stats = CacheStats()

        logger.warning(
            f"🗑️ Cleared ALL cache: {memory_count} memory + {disk_count} disk entries"
        )


# Global advanced cache instance
_advanced_cache: Optional[AdvancedCacheSystem] = None


def get_advanced_cache() -> AdvancedCacheSystem:
    """Get global advanced cache instance (singleton pattern)."""
    global _advanced_cache

    if _advanced_cache is None:
        _advanced_cache = AdvancedCacheSystem(
            cache_dir="cache",
            memory_size_limit=100,
            disk_size_limit=1000,
            default_ttl_hours=24,
            enable_warming=True,
        )

    return _advanced_cache
