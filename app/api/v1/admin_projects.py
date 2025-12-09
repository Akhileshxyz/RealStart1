from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.schemas.project import ProjectResponse, ProjectAdminUpdate

router = APIRouter()

@router.get("/", response_model=List[ProjectResponse])
async def list_all_projects_admin(
    status: ProjectStatus = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    List all projects. Filter by status.
    """
    query = {}
    if status:
        query = {"status": status}
    
    if query:
        projects = await Project.find(query).skip(skip).limit(limit).to_list()
    else:
        projects = await Project.find_all().skip(skip).limit(limit).to_list()
    return projects

@router.patch("/{project_id}/approve", response_model=ProjectResponse)
async def approve_project(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Approve a project.
    """
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.status = ProjectStatus.APPROVED
    await project.save()
    return project

@router.patch("/{project_id}/reject", response_model=ProjectResponse)
async def reject_project(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Reject a project.
    """
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.status = ProjectStatus.REJECTED
    await project.save()
    return project
