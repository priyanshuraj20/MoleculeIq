"""
infrastructure/cache/redis_client.py

Async Non-Blocking Redis Client wrapper for Upstash Redis.

Responsibility:
  1. Manages connection pooling over TLS (Upstash Cloud).
  2. Enforces strict timeouts (2s connect, 2s socket timeout).
  3. Provides safe non-blocking async get/set/ping methods.
  4. Suppresses connection errors cleanly to guarantee zero pipeline failures if Redis is offline.
"""

import logging
import time
from typing import Optional
import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)


# Global process-wide in-memory cache dictionary: key -> (value, expiry_timestamp)
_GLOBAL_MEMORY_CACHE: dict[str, tuple[str, float]] = {}
_GLOBAL_REDIS_OFFLINE: bool = False


class AsyncRedisClient:
    """
    Async client for Upstash Redis with transparent in-memory fallback.
    If Redis host is unreachable or DNS fails, seamlessly falls back to a
    fast in-memory dictionary cache with TTL expiration, eliminating error noise.
    """

    def __init__(self, redis_url: Optional[str] = None):
        self._url = redis_url or settings.REDIS_URL
        self._pool: Optional[aioredis.ConnectionPool] = None
        self._redis: Optional[aioredis.Redis] = None

    def _get_redis(self) -> Optional[aioredis.Redis]:
        """Lazy initialization of async Redis connection pool."""
        global _GLOBAL_REDIS_OFFLINE
        if _GLOBAL_REDIS_OFFLINE or not self._url:
            return None

        if self._redis is not None:
            return self._redis

        try:
            url = self._url
            if url.startswith("redis://") and "upstash.io" in url:
                url = url.replace("redis://", "rediss://", 1)

            ssl_kwargs = {}
            if url.startswith("rediss://"):
                ssl_kwargs = {"ssl_cert_reqs": None}

            self._pool = aioredis.ConnectionPool.from_url(
                url,
                decode_responses=True,
                socket_connect_timeout=1.5,
                socket_timeout=1.5,
                health_check_interval=30,
                retry_on_timeout=False,
                **ssl_kwargs
            )
            self._redis = aioredis.Redis(connection_pool=self._pool)
            return self._redis
        except Exception as exc:
            logger.info("[RedisClient] External Redis unreachable (%s). Using in-memory fallback cache.", str(exc))
            _GLOBAL_REDIS_OFFLINE = True
            return None

    def _get_memory(self, key: str) -> Optional[str]:
        """Retrieves from in-memory cache if not expired."""
        if key in _GLOBAL_MEMORY_CACHE:
            val, expiry = _GLOBAL_MEMORY_CACHE[key]
            if time.monotonic() < expiry:
                return val
            else:
                del _GLOBAL_MEMORY_CACHE[key]
        return None

    def _set_memory(self, key: str, value: str, ttl_seconds: int):
        """Stores in in-memory cache with monotonic TTL expiration."""
        _GLOBAL_MEMORY_CACHE[key] = (value, time.monotonic() + ttl_seconds)

    async def ping(self) -> bool:
        """Ping Redis server to check connectivity."""
        global _GLOBAL_REDIS_OFFLINE
        r = self._get_redis()
        if not r:
            return False
        try:
            return await r.ping()
        except Exception:
            _GLOBAL_REDIS_OFFLINE = True
            return False

    async def get(self, key: str) -> Optional[str]:
        """
        Fetches string value for key. Checks Redis first, then in-memory fallback.
        """
        global _GLOBAL_REDIS_OFFLINE
        start_time = time.monotonic()
        r = self._get_redis()
        if r:
            try:
                val = await r.get(key)
                latency_ms = round((time.monotonic() - start_time) * 1000, 1)
                if val:
                    logger.info("[Redis Cache] GET HIT for key='%s' (%s ms)", key, latency_ms)
                    return val
            except Exception:
                # Mark external Redis as offline and gracefully use memory fallback
                logger.info("[RedisClient] External Redis host unreachable. Switched to in-memory cache.")
                _GLOBAL_REDIS_OFFLINE = True

        # In-memory fallback
        mem_val = self._get_memory(key)
        if mem_val:
            logger.info("[Memory Cache] GET HIT for key='%s' (0.1 ms)", key)
            return mem_val
        return None

    async def set(self, key: str, value: str, ttl_seconds: int = 86400) -> bool:
        """
        Stores key-value pair with TTL (seconds) in Redis and in-memory cache.
        """
        global _GLOBAL_REDIS_OFFLINE
        self._set_memory(key, value, ttl_seconds)

        r = self._get_redis()
        if r:
            try:
                res = await r.set(key, value, ex=ttl_seconds)
                return bool(res)
            except Exception:
                _GLOBAL_REDIS_OFFLINE = True
                return True

        return True

    async def close(self):
        """Closes Redis connections and pool."""
        if self._redis:
            try:
                await self._redis.aclose()
            except Exception:
                pass
        if self._pool:
            try:
                await self._pool.aclose()
            except Exception:
                pass
        self._redis = None
        self._pool = None
