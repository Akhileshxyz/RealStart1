"""
No-op Caching decorators and utilities (Redis disabled).
"""

import functools
import logging
from typing import Any, Callable, Optional, Union
from datetime import timedelta

logger = logging.getLogger(__name__)


def generate_cache_key(*parts: Any) -> str:
    return ":".join(str(p) for p in parts)


def hash_dict(data: dict) -> str:
    return ""


def cache_result(
    key_pattern: str,
    ttl: Optional[Union[int, timedelta]] = None,
    key_builder: Optional[Callable] = None
):
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # No caching (Redis disabled)
            return await func(*args, **kwargs)

        wrapper.invalidate_cache = lambda *args, **kwargs: None
        return wrapper
    return decorator


def cache_user_data(ttl: Optional[int] = None):
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def cache_public_data(ttl: Optional[int] = None):
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class CacheManager:
    @staticmethod
    async def warm_cache(key: str, fetcher: Callable, ttl: Optional[int] = None):
        pass

    @staticmethod
    async def get_or_set(
        key: str,
        fetcher: Callable,
        ttl: Optional[int] = None
    ) -> Any:
        return await fetcher()

    @staticmethod
    async def invalidate_related(pattern: str):
        return 0


__all__ = [
    'cache_result',
    'cache_user_data',
    'cache_public_data',
    'generate_cache_key',
    'hash_dict',
    'CacheManager'
]
