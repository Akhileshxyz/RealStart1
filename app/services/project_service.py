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
    status: Optional[ProjectStatus] = None
) -> Optional[Project]:
    """
    Get project by slug from database.

    Args:
        slug: Project slug
        status: Optional status filter (e.g., APPROVED for public endpoints)

    Returns:
        Project object or None if not found
    """
    logger.debug(f"Fetching project by slug: {slug}")

    if status:
        # If filtering by APPROVED (Public), also enforce is_hidden=False
        if status == ProjectStatus.APPROVED:
            from beanie.operators import Or
            project = await Project.find_one(
                Project.slug == slug, 
                Project.status == status,
                Or(Project.is_hidden == False, Project.is_hidden == None)
            )
        else:
            project = await Project.find_one(Project.slug == slug, Project.status == status)
    else:
        project = await Project.find_one(Project.slug == slug)

    return project


async def get_project_by_id(project_id: UUID) -> Optional[Project]:
    """
    Get project by ID from database.

    Args:
        project_id: Project UUID

    Returns:
        Project object or None if not found
    """
    logger.debug(f"Fetching project by ID: {project_id}")
    return await Project.get(project_id)


async def get_approved_projects(
    skip: int = 0,
    limit: int = 20,
    city_id: Optional[UUID] = None
):
    """
    Get paginated list of approved projects.

    Returns:
        tuple: (List of approved Project objects, total count)
    """
    # Build base criteria for public projects - handle missing fields as well
    from beanie.operators import Or
    criteria = [
        Project.status == ProjectStatus.APPROVED,
        Or(Project.is_hidden == False, Project.is_hidden == None),
        Or(Project.is_active == True, Project.is_active == None)
    ]
    
    if city_id:
        from app.models.city import City
        city = await City.get(city_id)
        if city:
            # Aggregate project IDs from city lists
            raw_ids = []
            if city.top_developed_projects: raw_ids.extend(city.top_developed_projects)
            if city.upcoming_projects_list: raw_ids.extend(city.upcoming_projects_list)
            
            # Convert to pure UUID objects for standard subtype (0x04) matching
            project_uuids = []
            for item in raw_ids:
                try:
                    if isinstance(item, UUID): project_uuids.append(item)
                    elif isinstance(item, str): project_uuids.append(UUID(item))
                    else: project_uuids.append(UUID(str(item)))
                except (ValueError, TypeError): continue
            
            # Remove duplicates
            project_uuids = list(set(project_uuids))
            
            logger.debug(f"City: {city.name}, total linked projects: {len(project_uuids)}")
            if project_uuids:
                from beanie.operators import In
                criteria.append(In(Project.id, project_uuids))
            else:
                return [], 0
        else:
            logger.warning(f"City NOT found for ID: {city_id}")
            return [], 0
            
    # Execute query using Beanie DSL
    projects = await Project.find(*criteria).sort("-created_at").skip(skip).limit(limit).to_list()
    total = await Project.find(*criteria).count()
    
    logger.debug(f"Public API: Found {len(projects)} projects (Total: {total}) for city: {city_id}")

    return projects, total


async def get_all_projects_for_geospatial():
    """
    Get all projects for geospatial calculations (landmarks nearby).
    """
    # Simply query all projects directly (Cache removed)
    logger.debug("Fetching all projects for geospatial calculations")
    projects = await Project.find_all().to_list()
    return projects


# Export functions
__all__ = [
    'get_project_by_slug',
    'get_project_by_id',
    'get_approved_projects',
    'get_all_projects_for_geospatial',
]
