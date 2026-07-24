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


class AsyncRedisClient:
    """
    Async client for Upstash Redis using connection pooling and strict timeouts.
    """

    def __init__(self, redis_url: Optional[str] = None):
        self._url = redis_url or settings.REDIS_URL
        self._pool: Optional[aioredis.ConnectionPool] = None
        self._redis: Optional[aioredis.Redis] = None

    def _get_redis(self) -> Optional[aioredis.Redis]:
        """Lazy initialization of async Redis connection pool."""
        if self._redis is not None:
            return self._redis

        if not self._url:
            logger.warning("[RedisClient] REDIS_URL environment variable is empty. Caching disabled.")
            return None

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
                socket_connect_timeout=2.0,
                socket_timeout=2.0,
                health_check_interval=30,
                retry_on_timeout=True,
                **ssl_kwargs
            )
            self._redis = aioredis.Redis(connection_pool=self._pool)
            logger.info("[RedisClient] Async Redis connection pool initialized.")
            return self._redis
        except Exception as exc:
            logger.warning("[RedisClient] Failed to initialize connection pool: %s", str(exc))
            return None

    async def ping(self) -> bool:
        """Ping Redis server to check connectivity."""
        r = self._get_redis()
        if not r:
            return False
        try:
            return await r.ping()
        except Exception as exc:
            logger.warning("[RedisClient] Ping failed: %s", str(exc))
            return False

    async def get(self, key: str) -> Optional[str]:
        """
        Fetches string value for key. Returns None if key not found or error occurs.
        """
        r = self._get_redis()
        if not r:
            return None

        start_time = time.monotonic()
        try:
            val = await r.get(key)
            latency_ms = round((time.monotonic() - start_time) * 1000, 1)
            if val:
                logger.info("[Redis Cache] GET HIT for key='%s' (%s ms)", key, latency_ms)
            else:
                logger.info("[Redis Cache] GET MISS for key='%s' (%s ms)", key, latency_ms)
            return val
        except Exception as exc:
            latency_ms = round((time.monotonic() - start_time) * 1000, 1)
            logger.warning("[Redis Cache] GET error for key='%s' (%s ms): %s", key, latency_ms, str(exc))
            return None

    async def set(self, key: str, value: str, ttl_seconds: int = 86400) -> bool:
        """
        Stores key-value pair with TTL (seconds). Returns True on success, False on failure.
        """
        r = self._get_redis()
        if not r:
            return False

        start_time = time.monotonic()
        try:
            res = await r.set(key, value, ex=ttl_seconds)
            latency_ms = round((time.monotonic() - start_time) * 1000, 1)
            logger.info("[Redis Cache] SET SUCCESS key='%s' TTL=%ds (%s ms)", key, ttl_seconds, latency_ms)
            return bool(res)
        except Exception as exc:
            latency_ms = round((time.monotonic() - start_time) * 1000, 1)
            logger.warning("[Redis Cache] SET error for key='%s' (%s ms): %s", key, latency_ms, str(exc))
            return False

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
