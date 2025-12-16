"""
Cache invalidation utilities for coordinated cache clearing.

This module provides functions to invalidate cache entries when data is modified.
"""

import logging
from typing import Optional
from uuid import UUID

from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)


async def invalidate_user_cache(user_id: UUID) -> int:
    """
    Invalidate all cache entries related to a specific user.

    Args:
        user_id: User UUID

    Returns:
        Number of keys deleted
    """
    patterns = [
        f"realstart:user:id:{user_id}",  # User object cache
        f"realstart:user:{user_id}:*",  # User-specific data (history, wishlist, etc.)
        f"realstart:lead:*:user:{user_id}",  # Lead relationships
    ]

    total_deleted = 0
    for pattern in patterns:
        if "*" in pattern:
            deleted = await redis_client.delete_pattern(pattern)
        else:
            deleted = await redis_client.delete(pattern)
        total_deleted += deleted

    logger.info(f"Invalidated {total_deleted} cache entries for user {user_id}")
    return total_deleted


async def invalidate_project_cache(
    project_id: Optional[UUID] = None,
    slug: Optional[str] = None
) -> int:
    """
    Invalidate all cache entries related to a specific project.

    Args:
        project_id: Project UUID
        slug: Project slug

    Returns:
        Number of keys deleted
    """
    patterns = []

    if project_id:
        patterns.extend([
            f"realstart:project:id:{project_id}",  # Project by ID
            f"realstart:project:{project_id}:*",  # Project-specific data
            f"realstart:lead:project:{project_id}:*",  # Project leads
        ])

    if slug:
        patterns.append(f"realstart:project:slug:{slug}*")  # Project by slug (all statuses)

    # Invalidate list caches (public, admin, developer views)
    patterns.extend([
        "realstart:public:projects:*",  # Public project lists
        "realstart:admin:projects:*",  # Admin project lists
        "realstart:projects:*",  # All project lists
        "realstart:projects:geospatial:all",  # Geospatial cache
    ])

    total_deleted = 0
    for pattern in patterns:
        if "*" in pattern:
            deleted = await redis_client.delete_pattern(pattern)
        else:
            deleted = await redis_client.delete(pattern)
        total_deleted += deleted

    logger.info(f"Invalidated {total_deleted} cache entries for project {project_id or slug}")
    return total_deleted


async def invalidate_lead_cache(project_id: UUID, user_id: UUID) -> int:
    """
    Invalidate cache entries for a specific lead relationship.

    Args:
        project_id: Project UUID
        user_id: User UUID

    Returns:
        Number of keys deleted
    """
    patterns = [
        f"realstart:lead:project:{project_id}:user:{user_id}",  # Specific lead
        f"realstart:project:{project_id}:leads*",  # Project's lead list
        f"realstart:user:{user_id}:history:*",  # User's view history
        f"realstart:user:{user_id}:wishlist:*",  # User's wishlist
    ]

    total_deleted = 0
    for pattern in patterns:
        if "*" in pattern:
            deleted = await redis_client.delete_pattern(pattern)
        else:
            deleted = await redis_client.delete(pattern)
        total_deleted += deleted

    logger.info(f"Invalidated {total_deleted} cache entries for lead (project:{project_id}, user:{user_id})")
    return total_deleted


async def invalidate_landmark_cache(
    landmark_id: Optional[str] = None,
    city: Optional[str] = None
) -> int:
    """
    Invalidate cache entries for landmarks.

    Args:
        landmark_id: Landmark ID
        city: City name

    Returns:
        Number of keys deleted
    """
    patterns = []

    if landmark_id:
        patterns.append(f"realstart:landmark:details:{landmark_id}")

    if city:
        patterns.append(f"realstart:public:landmarks:city:{city}")

    # Always invalidate the all landmarks cache
    patterns.append("realstart:public:landmarks:all")

    total_deleted = 0
    for pattern in patterns:
        deleted = await redis_client.delete(pattern)
        total_deleted += deleted

    logger.info(f"Invalidated {total_deleted} cache entries for landmarks")
    return total_deleted


async def invalidate_webhook_cache(developer_id: UUID) -> int:
    """
    Invalidate webhook subscription cache for a developer.

    Args:
        developer_id: Developer UUID

    Returns:
        Number of keys deleted
    """
    patterns = [
        f"realstart:webhooks:dev:{developer_id}:active",
        f"realstart:user:{developer_id}:webhooks",
    ]

    total_deleted = 0
    for pattern in patterns:
        deleted = await redis_client.delete(pattern)
        total_deleted += deleted

    logger.info(f"Invalidated {total_deleted} webhook cache entries for developer {developer_id}")
    return total_deleted


async def invalidate_admin_cache(resource_type: str) -> int:
    """
    Invalidate admin dashboard cache for a specific resource type.

    Args:
        resource_type: Type of resource ('users', 'developers', 'projects', 'requests')

    Returns:
        Number of keys deleted
    """
    pattern = f"realstart:admin:{resource_type}:*"
    deleted = await redis_client.delete_pattern(pattern)

    logger.info(f"Invalidated {deleted} admin cache entries for {resource_type}")
    return deleted


async def invalidate_all_user_sessions() -> int:
    """
    Invalidate all user session caches (use with caution).

    Returns:
        Number of keys deleted
    """
    pattern = "realstart:user:id:*"
    deleted = await redis_client.delete_pattern(pattern)

    logger.warning(f"Invalidated ALL user session caches: {deleted} entries")
    return deleted


async def invalidate_all_project_lists() -> int:
    """
    Invalidate all project list caches (public, admin, developer views).

    Returns:
        Number of keys deleted
    """
    patterns = [
        "realstart:public:projects:*",
        "realstart:admin:projects:*",
        "realstart:projects:*",
    ]

    total_deleted = 0
    for pattern in patterns:
        deleted = await redis_client.delete_pattern(pattern)
        total_deleted += deleted

    logger.info(f"Invalidated {total_deleted} project list cache entries")
    return total_deleted


# Export all invalidation functions
__all__ = [
    'invalidate_user_cache',
    'invalidate_project_cache',
    'invalidate_lead_cache',
    'invalidate_landmark_cache',
    'invalidate_webhook_cache',
    'invalidate_admin_cache',
    'invalidate_all_user_sessions',
    'invalidate_all_project_lists',
]
