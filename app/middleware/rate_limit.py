from fastapi import Request, HTTPException, status
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class InMemoryRateLimiter:
    """
    Simple in-memory rate limiter.
    For production, use Redis-based rate limiter.
    """
    def __init__(self):
        self.requests = defaultdict(list)
        self.cleanup_threshold = 1000  # Clean up after this many entries

    def is_rate_limited(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """
        Check if a request should be rate limited.

        Args:
            key: Unique identifier (e.g., IP address + endpoint)
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds

        Returns:
            True if rate limited, False otherwise
        """
        now = datetime.now()
        window_start = now - timedelta(seconds=window_seconds)

        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]

        # Check rate limit
        if len(self.requests[key]) >= max_requests:
            logger.warning(f"Rate limit exceeded for {key}")
            return True

        # Add current request
        self.requests[key].append(now)

        # Periodic cleanup
        if len(self.requests) > self.cleanup_threshold:
            self._cleanup_old_entries()

        return False

    def _cleanup_old_entries(self):
        """Remove entries older than 1 hour"""
        cutoff = datetime.now() - timedelta(hours=1)
        keys_to_remove = []

        for key, times in self.requests.items():
            self.requests[key] = [t for t in times if t > cutoff]
            if not self.requests[key]:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.requests[key]


# Global rate limiter instance
rate_limiter = InMemoryRateLimiter()


def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    """
    Rate limiting decorator for FastAPI endpoints.

    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds

    Usage:
        @app.get("/endpoint")
        @rate_limit(max_requests=10, window_seconds=60)
        async def endpoint(request: Request):
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get('request') or args[0]
            client_ip = request.client.host
            endpoint = request.url.path
            key = f"{client_ip}:{endpoint}"

            if rate_limiter.is_rate_limited(key, max_requests, window_seconds):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later."
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator
