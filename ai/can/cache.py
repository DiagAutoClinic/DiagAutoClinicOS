# ai/can/cache.py

from functools import lru_cache
from typing import Dict, Any, Optional
import time
from ..utils.logging import logger

class CANCache:
    def __init__(self, max_size: int = 512, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
        self._cache: Dict[str, Dict[str, Any]] = {}

    @lru_cache(maxsize=512)
    def get_pid_definition(self, pid: str) -> Optional[Dict[str, Any]]:
        """Get PID definition with caching."""
        cache_key = f"pid_{pid}"

        # Check if cached and not expired
        if cache_key in self._cache:
            cached_item = self._cache[cache_key]
            if time.time() - cached_item['timestamp'] < self.ttl:
                logger.debug(f"Cache hit for PID {pid}")
                return cached_item['data']
            else:
                # Expired, remove from cache
                del self._cache[cache_key]

        # Not in cache or expired - would query database here
        # For now, return None (implement actual database query in integration)
        logger.debug(f"Cache miss for PID {pid}")
        return None

    def set_pid_definition(self, pid: str, definition: Dict[str, Any]):
        """Cache a PID definition."""
        cache_key = f"pid_{pid}"
        self._cache[cache_key] = {
            'data': definition,
            'timestamp': time.time()
        }
        logger.debug(f"Cached PID {pid} definition")

    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()
        self.get_pid_definition.cache_clear()  # Clear LRU cache
        logger.info("CAN cache cleared")

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            'cached_items': len(self._cache),
            'max_size': self.max_size,
            'ttl': self.ttl
        }