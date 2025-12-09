from datetime import datetime
from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from app.api import deps
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.models.lead import ProjectLead
from app.schemas.project import ProjectResponse

router = APIRouter()

@router.get("/", response_model=List[ProjectResponse])
async def list_public_projects(
    skip: int = 0,
    limit: int = 20
) -> Any:
    """
    List all APPROVED projects visible to public.
    """
    projects = await Project.find(
        Project.status == ProjectStatus.APPROVED
    ).skip(skip).limit(limit).to_list()
    return projects

@router.get("/{slug}", response_model=ProjectResponse)
async def get_public_project(
    slug: str,
    current_user: Optional[User] = Depends(deps.get_current_user_optional) # Need to implement optional Auth dep or handle try/except
) -> Any:
    """
    Get a specific APPROVED project by slug.
    Logs the view if user is logged in.
    """
    project = await Project.find_one(
        Project.slug == slug,
        Project.status == ProjectStatus.APPROVED
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Log View if User is logged in
    if current_user:
        lead = await ProjectLead.find_one(
            ProjectLead.project_id == project.id,
            ProjectLead.user_id == current_user.id
        )
        if lead:
            lead.last_viewed_at = datetime.utcnow()
            lead.viewed_at_history.append(datetime.utcnow())
            await lead.save()
        else:
            lead = ProjectLead(
                project_id=project.id,
                user_id=current_user.id,
                viewed_at_history=[datetime.utcnow()]
            )
            await lead.insert()
            
    return project
