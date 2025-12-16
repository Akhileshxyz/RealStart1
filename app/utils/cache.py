"""
Caching decorators and utilities for Redis-based caching.

This module provides reusable decorators and helpers for caching function results.
"""

import functools
import hashlib
import logging
from typing import Any, Callable, Optional, Union
from datetime import timedelta

from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)


def generate_cache_key(*parts: Any) -> str:
    """
    Generate a cache key from parts.

    Args:
        *parts: Variable parts to create key from

    Returns:
        Cache key string
    """
    return redis_client.make_key(*[str(p) for p in parts])


def hash_dict(data: dict) -> str:
    """
    Create a hash from a dictionary for cache keys.

    Args:
        data: Dictionary to hash

    Returns:
        MD5 hash string
    """
    # Sort keys for consistent hashing
    sorted_items = sorted(data.items())
    dict_str = str(sorted_items)
    return hashlib.md5(dict_str.encode()).hexdigest()[:8]


def cache_result(
    key_pattern: str,
    ttl: Optional[Union[int, timedelta]] = None,
    key_builder: Optional[Callable] = None
):
    """
    Decorator to cache function results in Redis.

    Args:
        key_pattern: Pattern for cache key (e.g., "user:id:{user_id}")
        ttl: Time to live in seconds or timedelta
        key_builder: Custom function to build cache key from args/kwargs

    Example:
        @cache_result("project:slug:{slug}", ttl=3600)
        async def get_project(slug: str):
            return await Project.find_one(Project.slug == slug)
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Try to extract parameters from kwargs for key pattern
                cache_key = key_pattern.format(**kwargs) if kwargs else key_pattern

            # Try to get from cache
            cached_value = await redis_client.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for function '{func.__name__}': {cache_key}")
                return cached_value

            # Cache miss - call function
            logger.debug(f"Cache miss for function '{func.__name__}': {cache_key}")
            result = await func(*args, **kwargs)

            # Store in cache if result is not None
            if result is not None:
                await redis_client.set(cache_key, result, ttl)

            return result

        # Add cache invalidation helper
        wrapper.invalidate_cache = lambda *args, **kwargs: redis_client.delete(
            key_builder(*args, **kwargs) if key_builder else key_pattern.format(**kwargs)
        )

        return wrapper
    return decorator


def cache_user_data(ttl: Optional[int] = None):
    """
    Decorator for caching user-specific data.

    Args:
        ttl: Time to live (defaults to REDIS_CACHE_TTL_USER from settings)

    Example:
        @cache_user_data(ttl=600)
        async def get_user_history(user_id: UUID):
            return await get_history(user_id)
    """
    from app.core.config import settings

    actual_ttl = ttl if ttl is not None else settings.REDIS_CACHE_TTL_USER

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user_id from args or kwargs
            user_id = kwargs.get('user_id') or (args[0] if args else None)
            if not user_id:
                # No user_id - don't cache
                return await func(*args, **kwargs)

            cache_key = generate_cache_key("user", str(user_id), func.__name__)

            # Try cache
            cached_value = await redis_client.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call function
            result = await func(*args, **kwargs)

            # Cache result
            if result is not None:
                await redis_client.set(cache_key, result, actual_ttl)

            return result

        return wrapper
    return decorator


def cache_public_data(ttl: Optional[int] = None):
    """
    Decorator for caching public data (no authentication required).

    Args:
        ttl: Time to live (defaults to REDIS_CACHE_TTL_PUBLIC from settings)

    Example:
        @cache_public_data(ttl=3600)
        async def get_approved_projects(skip: int = 0, limit: int = 20):
            return await Project.find(status=APPROVED).to_list()
    """
    from app.core.config import settings

    actual_ttl = ttl if ttl is not None else settings.REDIS_CACHE_TTL_PUBLIC

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and args
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            if kwargs:
                key_parts.append(hash_dict(kwargs))

            cache_key = generate_cache_key("public", *key_parts)

            # Try cache
            cached_value = await redis_client.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call function
            result = await func(*args, **kwargs)

            # Cache result
            if result is not None:
                await redis_client.set(cache_key, result, actual_ttl)

            return result

        return wrapper
    return decorator


class CacheManager:
    """
    Helper class for managing cache operations.
    """

    @staticmethod
    async def warm_cache(key: str, fetcher: Callable, ttl: Optional[int] = None):
        """
        Warm up cache with data.

        Args:
            key: Cache key
            fetcher: Async function to fetch data
            ttl: Time to live
        """
        try:
            data = await fetcher()
            if data is not None:
                await redis_client.set(key, data, ttl)
                logger.info(f"Cache warmed for key: {key}")
        except Exception as e:
            logger.error(f"Failed to warm cache for {key}: {e}")

    @staticmethod
    async def get_or_set(
        key: str,
        fetcher: Callable,
        ttl: Optional[int] = None
    ) -> Any:
        """
        Get value from cache or fetch and set if not exists.

        Args:
            key: Cache key
            fetcher: Async function to fetch data if not in cache
            ttl: Time to live

        Returns:
            Cached or fetched value
        """
        # Try cache first
        cached = await redis_client.get(key)
        if cached is not None:
            return cached

        # Fetch and cache
        data = await fetcher()
        if data is not None:
            await redis_client.set(key, data, ttl)

        return data

    @staticmethod
    async def invalidate_related(pattern: str):
        """
        Invalidate all cache keys matching a pattern.

        Args:
            pattern: Key pattern with wildcards
        """
        deleted = await redis_client.delete_pattern(pattern)
        logger.info(f"Invalidated {deleted} cache keys matching pattern: {pattern}")
        return deleted


# Export commonly used functions
__all__ = [
    'cache_result',
    'cache_user_data',
    'cache_public_data',
    'generate_cache_key',
    'hash_dict',
    'CacheManager'
]
