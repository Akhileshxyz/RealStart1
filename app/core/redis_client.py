"""
Redis client with connection pooling and caching utilities.

This module provides:
- Redis connection pool management
- Health check mechanism
- Graceful degradation if Redis is unavailable
- Helper functions for get/set/delete operations
- JSON serialization/deserialization
- Cache key prefixing
"""

import json
import logging
from typing import Any, Optional, Union
from datetime import timedelta, datetime
from uuid import UUID

import redis.asyncio as redis
from redis.asyncio import ConnectionPool
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Async Redis client with connection pooling and helper methods.
    """

    def __init__(self):
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self._available = False

    async def initialize(self):
        """Initialize Redis connection pool"""
        if not settings.ENABLE_REDIS_CACHE:
            logger.info("Redis caching is disabled")
            return

        try:
            self._pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            self._client = redis.Redis(connection_pool=self._pool)

            # Test connection
            await self._client.ping()
            self._available = True
            logger.info(f"Redis connected successfully: {settings.REDIS_URL}")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            logger.warning("Application will continue without caching")
            self._available = False

    async def close(self):
        """Close Redis connection pool"""
        if self._client:
            await self._client.close()
        if self._pool:
            await self._pool.disconnect()
        logger.info("Redis connection closed")

    @property
    def is_available(self) -> bool:
        """Check if Redis is available"""
        return self._available and settings.ENABLE_REDIS_CACHE

    async def health_check(self) -> bool:
        """Perform health check on Redis connection"""
        if not self.is_available:
            return False

        try:
            await self._client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            self._available = False
            return False

    def _serialize(self, value: Any) -> str:
        """Serialize value to JSON string"""
        if isinstance(value, (str, int, float, bool)) and value is not None:
            return json.dumps(value)
            
        def default_serializer(obj):
            if hasattr(obj, "model_dump"):
                return obj.model_dump()
            if hasattr(obj, "dict"):
                return obj.dict()
            if isinstance(obj, (datetime, UUID)):
                return str(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        return json.dumps(value, default=default_serializer)

    def _deserialize(self, value: Optional[str]) -> Any:
        """Deserialize JSON string to Python object"""
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def make_key(self, *parts: str) -> str:
        """
        Create cache key with prefix.

        Example:
            make_key("user", "id", "123") -> "realstart:user:id:123"
        """
        prefix = "realstart"
        return f"{prefix}:" + ":".join(str(p) for p in parts)

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from Redis.

        Args:
            key: Cache key

        Returns:
            Deserialized value or None if key doesn't exist or Redis unavailable
        """
        if not self.is_available:
            return None

        try:
            value = await self._client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return self._deserialize(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """
        Set value in Redis with optional TTL.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds or timedelta

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            return False

        try:
            serialized = self._serialize(value)

            if ttl is None:
                ttl = settings.REDIS_CACHE_TTL_DEFAULT

            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())

            await self._client.setex(key, ttl, serialized)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False

    async def delete(self, *keys: str) -> int:
        """
        Delete one or more keys from Redis.

        Args:
            *keys: Variable number of cache keys to delete

        Returns:
            Number of keys deleted
        """
        if not self.is_available or not keys:
            return 0

        try:
            deleted = await self._client.delete(*keys)
            logger.debug(f"Cache DELETE: {deleted} keys deleted")
            return deleted
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return 0

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.

        Args:
            pattern: Key pattern with wildcards (e.g., "user:*")

        Returns:
            Number of keys deleted
        """
        if not self.is_available:
            return 0

        try:
            keys = []
            async for key in self._client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                deleted = await self._client.delete(*keys)
                logger.debug(f"Cache DELETE PATTERN '{pattern}': {deleted} keys deleted")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Redis DELETE PATTERN error for '{pattern}': {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        if not self.is_available:
            return False

        try:
            result = await self._client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False

    async def expire(self, key: str, ttl: Union[int, timedelta]) -> bool:
        """
        Set TTL on an existing key.

        Args:
            key: Cache key
            ttl: Time to live in seconds or timedelta

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            return False

        try:
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())

            result = await self._client.expire(key, ttl)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment a counter key.

        Args:
            key: Cache key
            amount: Amount to increment by

        Returns:
            New value or None if error
        """
        if not self.is_available:
            return None

        try:
            return await self._client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis INCREMENT error for key {key}: {e}")
            return None

    async def get_ttl(self, key: str) -> Optional[int]:
        """
        Get remaining TTL for a key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds, -1 if no TTL, -2 if key doesn't exist, None if error
        """
        if not self.is_available:
            return None

        try:
            return await self._client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error for key {key}: {e}")
            return None

    async def clear_all(self) -> bool:
        """
        Clear all keys in current database (USE WITH CAUTION).

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            return False

        try:
            await self._client.flushdb()
            logger.warning("Redis database flushed - all keys deleted")
            return True
        except Exception as e:
            logger.error(f"Redis FLUSHDB error: {e}")
            return False


# Global Redis client instance
redis_client = RedisClient()


# Convenience functions for common operations
async def get_cache(key: str) -> Optional[Any]:
    """Get value from cache"""
    return await redis_client.get(key)


async def set_cache(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Set value in cache"""
    return await redis_client.set(key, value, ttl)


async def delete_cache(*keys: str) -> int:
    """Delete one or more cache keys"""
    return await redis_client.delete(*keys)


async def delete_cache_pattern(pattern: str) -> int:
    """Delete all keys matching pattern"""
    return await redis_client.delete_pattern(pattern)
