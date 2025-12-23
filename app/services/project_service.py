"""
Centralized project service with caching.

This service consolidates project lookup operations and provides
caching to avoid repeated database queries across multiple endpoints.
"""

import logging
from typing import Optional
from uuid import UUID

from app.models.project import Project, ProjectStatus
from app.core.redis_client import redis_client
from app.core.config import settings

logger = logging.getLogger(__name__)


async def get_project_by_slug(
    slug: str,
    status: Optional[ProjectStatus] = None,
    use_cache: bool = True
) -> Optional[Project]:
    """
    Get project by slug with caching.

    This function is used across multiple endpoints and consolidates
    the lookup logic with caching to avoid repeated database queries.

    Args:
        slug: Project slug
        status: Optional status filter (e.g., APPROVED for public endpoints)
        use_cache: Whether to use caching (default: True)

    Returns:
        Project object or None if not found
    """
    # Build cache key with status if provided
    cache_key = redis_client.make_key("project", "slug", slug)
    if status:
        cache_key = f"{cache_key}:{status.value}"

    # Try cache first if enabled
    if use_cache:
        cached_project = await redis_client.get(cache_key)
        if cached_project:
            logger.debug(f"Project cache HIT for slug: {slug}")
            return Project(**cached_project)

    # Cache miss - query database
    logger.debug(f"Project cache MISS for slug: {slug}")

    if status:
        # If filtering by APPROVED (Public), also enforce is_hidden=False
        if status == ProjectStatus.APPROVED:
            project = await Project.find_one(
                Project.slug == slug, 
                Project.status == status,
                Project.is_hidden == False
            )
        else:
            project = await Project.find_one(Project.slug == slug, Project.status == status)
    else:
        project = await Project.find_one(Project.slug == slug)

    # Cache the result if found
    if project and use_cache:
        project_dict = project.model_dump()
        # Cache for 2-4 hours as per plan
        ttl = settings.REDIS_CACHE_TTL_PUBLIC
        await redis_client.set(cache_key, project_dict, ttl)
        logger.debug(f"Cached project slug: {slug} with TTL: {ttl}s")

    return project


async def get_project_by_id(
    project_id: UUID,
    use_cache: bool = True
) -> Optional[Project]:
    """
    Get project by ID with caching.

    Args:
        project_id: Project UUID
        use_cache: Whether to use caching (default: True)

    Returns:
        Project object or None if not found
    """
    cache_key = redis_client.make_key("project", "id", str(project_id))

    # Try cache first if enabled
    if use_cache:
        cached_project = await redis_client.get(cache_key)
        if cached_project:
            logger.debug(f"Project cache HIT for ID: {project_id}")
            return Project(**cached_project)

    # Cache miss - query database
    logger.debug(f"Project cache MISS for ID: {project_id}")
    project = await Project.get(project_id)

    # Cache the result if found
    if project and use_cache:
        project_dict = project.model_dump()
        ttl = settings.REDIS_CACHE_TTL_PUBLIC
        await redis_client.set(cache_key, project_dict, ttl)

    return project


async def get_approved_projects(
    skip: int = 0,
    limit: int = 20,
    use_cache: bool = True
):
    """
    Get paginated list of approved projects with caching.

    Args:
        skip: Number of records to skip
        limit: Number of records to return
        use_cache: Whether to use caching (default: True)

    Returns:
        List of approved Project objects
    """
    cache_key = redis_client.make_key("public", "projects", "approved", str(skip), str(limit))

    # Try cache first if enabled
    if use_cache:
        cached_projects = await redis_client.get(cache_key)
        if cached_projects:
            logger.debug(f"Approved projects cache HIT (skip={skip}, limit={limit})")
            return [Project(**p) for p in cached_projects]

    # Cache miss - query database
    logger.debug(f"Approved projects cache MISS (skip={skip}, limit={limit})")
    projects = await Project.find(
        Project.status == ProjectStatus.APPROVED,
        Project.is_hidden == False
    ).skip(skip).limit(limit).to_list()

    # Cache the results
    if projects and use_cache:
        projects_dict = [p.model_dump() for p in projects]
        ttl = settings.REDIS_CACHE_TTL_PUBLIC  # 1 hour for public project lists
        await redis_client.set(cache_key, projects_dict, ttl)
        logger.debug(f"Cached approved projects list (skip={skip}, limit={limit})")

    return projects


async def get_all_projects_for_geospatial(use_cache: bool = True):
    """
    Get all projects for geospatial calculations (landmarks nearby).

    This query fetches all projects and is expensive. Caching is critical.

    Args:
        use_cache: Whether to use caching (default: True)

    Returns:
        List of all Project objects with coordinates
    """
    cache_key = redis_client.make_key("projects", "geospatial", "all")

    # Try cache first if enabled
    if use_cache:
        cached_projects = await redis_client.get(cache_key)
        if cached_projects:
            try:
                logger.debug("Geospatial projects cache HIT")
                return [Project(**p) for p in cached_projects]
            except Exception as e:
                logger.warning(f"Failed to deserialize project cache: {e}. Falling back to DB.")
                # Fallthrough to DB query


    # Cache miss - query database (expensive)
    logger.debug("Geospatial projects cache MISS - fetching all projects")
    projects = await Project.find_all().to_list()

    # Cache the results
    if projects and use_cache:
        # Only cache necessary fields for geospatial calculations
        projects_dict = [p.model_dump() for p in projects]
        ttl = 3600  # 1 hour TTL for geospatial data
        await redis_client.set(cache_key, projects_dict, ttl)
        logger.debug(f"Cached {len(projects)} projects for geospatial calculations")

    return projects


# Export functions
__all__ = [
    'get_project_by_slug',
    'get_project_by_id',
    'get_approved_projects',
    'get_all_projects_for_geospatial',
]
