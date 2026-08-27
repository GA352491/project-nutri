"""
NutriPlan Redis Cache Layer
============================
Provides a unified, async-safe cache wrapper with:
  - Typed get/set/delete with automatic JSON serialization
  - TTL-controlled cache entries
  - Cache-aside pattern helper (get_or_set)
  - Namespace prefixing to avoid key collisions between services
  - Graceful no-op fallback when Redis is unavailable (local dev safety)

Usage:
    from nutriplan_shared.cache import cache

    # Set
    await cache.set("plan", user_id, plan_data, ttl=3600)

    # Get
    plan = await cache.get("plan", user_id)

    # Get or compute + cache
    plan = await cache.get_or_set("plan", user_id, compute_fn, ttl=3600)

    # Invalidate
    await cache.delete("plan", user_id)
"""
from __future__ import annotations

import json
import logging
import asyncio
from typing import Any, Callable, Optional, Awaitable
from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# TTL presets (seconds)
TTL_PLAN = 3600          # 1 hour  – rolling 7-day meal plan per user
TTL_FOOD_SEARCH = 300    # 5 min   – recipe & food search results
TTL_BIOMETRICS = 60      # 60 sec  – realtime wearable snapshot
TTL_NOTIFICATIONS = 30   # 30 sec  – notification badge count
TTL_SESSION = 900        # 15 min  – auth session helper

NAMESPACE_SEP = ":"


class CacheLayer:
    """
    Async Redis cache layer with namespace support, JSON serialization,
    TTL management, and graceful fallback when Redis is down.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self._url = redis_url
        self._client: Any = None

    async def _get_client(self) -> Any:
        if self._client is None:
            try:
                import redis.asyncio as aioredis
                self._client = aioredis.from_url(self._url, decode_responses=True)
                await self._client.ping()
                logger.info("✅ Redis Cache Layer: connected to %s", self._url)
            except Exception as exc:
                logger.warning("⚠️  Redis unavailable (%s) — Cache running in no-op mode", exc)
                self._client = _NoOpRedis()
        return self._client

    def _key(self, namespace: str, identity: str) -> str:
        return f"nutriplan{NAMESPACE_SEP}{namespace}{NAMESPACE_SEP}{identity}"

    async def get(self, namespace: str, identity: str) -> Optional[Any]:
        """Return cached value or None if missing/expired."""
        client = await self._get_client()
        try:
            raw = await client.get(self._key(namespace, identity))
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as exc:
            logger.warning("Cache GET failed [%s/%s]: %s", namespace, identity, exc)
            return None

    async def set(self, namespace: str, identity: str, value: Any, ttl: int = TTL_PLAN) -> bool:
        """Store value as JSON with TTL. Returns True on success."""
        client = await self._get_client()
        try:
            await client.setex(self._key(namespace, identity), ttl, json.dumps(value, default=str))
            logger.debug("Cache SET [%s/%s] TTL=%ds", namespace, identity, ttl)
            return True
        except Exception as exc:
            logger.warning("Cache SET failed [%s/%s]: %s", namespace, identity, exc)
            return False

    async def delete(self, namespace: str, identity: str) -> bool:
        """Invalidate a cache entry."""
        client = await self._get_client()
        try:
            await client.delete(self._key(namespace, identity))
            logger.debug("Cache DEL [%s/%s]", namespace, identity)
            return True
        except Exception as exc:
            logger.warning("Cache DEL failed [%s/%s]: %s", namespace, identity, exc)
            return False

    async def get_or_set(
        self,
        namespace: str,
        identity: str,
        compute: Callable[[], Awaitable[Any]],
        ttl: int = TTL_PLAN
    ) -> Any:
        """
        Cache-aside helper: returns cached value if present,
        otherwise calls `compute()`, stores the result, and returns it.
        """
        cached = await self.get(namespace, identity)
        if cached is not None:
            logger.debug("Cache HIT [%s/%s]", namespace, identity)
            return cached

        logger.debug("Cache MISS [%s/%s] — computing...", namespace, identity)
        result = await compute()
        if result is not None:
            await self.set(namespace, identity, result, ttl)
        return result

    async def stats(self) -> dict:
        """Return Redis INFO memory + keyspace stats for admin dashboard."""
        client = await self._get_client()
        try:
            info = await client.info("all")
            keyspace = {k: v for k, v in info.items() if k.startswith("db")}
            return {
                "connected": True,
                "redis_version": info.get("redis_version", "unknown"),
                "used_memory_human": info.get("used_memory_human", "N/A"),
                "used_memory_peak_human": info.get("used_memory_peak_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate_pct": round(
                    info.get("keyspace_hits", 0) /
                    max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100,
                    2
                ),
                "keyspace": keyspace,
                "rdb_last_bgsave_status": info.get("rdb_last_bgsave_status", "N/A"),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
            }
        except Exception as exc:
            logger.warning("Cache STATS failed: %s", exc)
            return {
                "connected": False,
                "error": str(exc),
                "used_memory_human": "N/A",
                "hit_rate_pct": 0,
                "keyspace_hits": 0,
                "keyspace_misses": 0,
            }


class _NoOpRedis:
    """Silent fallback used when Redis is unavailable in local dev."""
    async def get(self, *a, **kw): return None
    async def setex(self, *a, **kw): return True
    async def delete(self, *a, **kw): return True
    async def ping(self, *a, **kw): return True
    async def info(self, *a, **kw): return {}


# Singleton instance — import this everywhere
cache = CacheLayer(redis_url=settings.REDIS_URL)
