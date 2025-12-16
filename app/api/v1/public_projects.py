from datetime import datetime, timezone
from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.api import deps
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.models.lead import ProjectLead
from app.schemas.project import ProjectResponse
from app.services.project_service import get_approved_projects, get_project_by_slug

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.get("/", response_model=List[ProjectResponse])
@limiter.limit("60/minute")
async def list_public_projects(
    request: Request,
    skip: int = 0,
    limit: int = 20
) -> Any:
    """
    List all APPROVED projects visible to public.
    TIER 1 CACHING: Results cached for 1 hour.
    RATE LIMIT: 60 requests per minute.
    """
    projects = await get_approved_projects(skip=skip, limit=limit, use_cache=True)
    return projects

@router.get("/{slug}", response_model=ProjectResponse)
@limiter.limit("120/minute")
async def get_public_project(
    request: Request,
    slug: str,
    current_user: Optional[User] = Depends(deps.get_current_user_optional) # Need to implement optional Auth dep or handle try/except
) -> Any:
    """
    Get a specific APPROVED project by slug.
    Logs the view if user is logged in.
    """
    project = await get_project_by_slug(slug=slug, status=ProjectStatus.APPROVED, use_cache=True)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Log View if User is logged in
    if current_user:
        lead = await ProjectLead.find_one(
            ProjectLead.project_id == project.id,
            ProjectLead.user_id == current_user.id
        )
        if lead:
            lead.last_viewed_at = datetime.now(timezone.utc)
            lead.viewed_at_history.append(datetime.now(timezone.utc))
            await lead.save()
        else:
            lead = ProjectLead(
                project_id=project.id,
                user_id=current_user.id,
                viewed_at_history=[datetime.now(timezone.utc)]
            )
            await lead.insert()
            
    return project
