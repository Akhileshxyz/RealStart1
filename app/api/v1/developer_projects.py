from typing import Any, List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User, UserRole
from app.models.project import Project, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter()

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new project.
    Role required: DEVELOPER.
    Status defaults to PENDING.
    """
    # Verify role
    if current_user.role not in [UserRole.DEVELOPER, UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN]:
         raise HTTPException(status_code=403, detail="Not authorized to create projects")

    # Check slug uniqueness
    existing = await Project.find_one(Project.slug == project_in.slug)
    if existing:
        raise HTTPException(status_code=400, detail="Project slug already exists")

    # If user is a developer, ensure they link it to themselves or their organization
    # For simplicity, we assume the input developer_id is valid or we overwrite it with current user's org
    # Here we just take the input but we could enforce logic.
    
    project = Project(
        **project_in.model_dump(),
        status=ProjectStatus.PENDING # Enforce Pending
    )
    await project.insert()
    return project

@router.get("/my-projects", response_model=List[ProjectResponse])
async def list_my_projects(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    List projects created by or belonging to the current developer.
    Shows ALL statuses (Pending, Approved, Rejected).
    """
    # Filter by developer_id if user is a developer
    query = {}
    if current_user.role == UserRole.DEVELOPER:
        query = Project.developer_id == current_user.id
        # Note: This assumes the user's ID is the developer_id used in projects.
        # If projects were created with a different developer_id (e.g. org ID), this needs adjustment.
        # For now, we strictly match the user ID.
        projects = await Project.find(query).skip(skip).limit(limit).to_list()
    else:
        # Admins see all or strict filtering?
        # Keeping behavior simple as per previous placeholder
        projects = await Project.find_all().skip(skip).limit(limit).to_list()
        
    return projects

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_in: ProjectUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Edit an existing listing.
    Role required: DEVELOPER (owner) or ADMIN.
    Note: Editing a project typically resets its status to PENDING for re-approval.
    """
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify RBAC: Developer can only edit their own project
    if current_user.role == UserRole.DEVELOPER:
        if project.developer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to edit this project")
    elif current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.MANAGER]:
        # If not developer and not admin/manager
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update logic
    update_data = project_in.model_dump(exclude_unset=True)
    
    # Reset status to PENDING if edited by Developer (to require re-approval)
    if current_user.role == UserRole.DEVELOPER:
        update_data["status"] = ProjectStatus.PENDING
    
    # Apply updates
    await project.set(update_data)
    project.updated_at = datetime.utcnow()
    await project.save()
    
    return project

@router.delete("/{project_id}", response_model=dict)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a listing.
    Role required: DEVELOPER (owner) or ADMIN.
    """
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify RBAC: Developer can only delete their own project
    if current_user.role == UserRole.DEVELOPER:
        if project.developer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this project")
    elif current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.MANAGER]:
         raise HTTPException(status_code=403, detail="Not authorized")

    await project.delete()
    return {"message": "Project deleted successfully"}

@router.patch("/{project_id}/visibility", response_model=ProjectResponse)
async def toggle_project_visibility(
    project_id: UUID,
    is_hidden: bool = Body(..., embed=True),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Toggle project visibility (Hide/Show).
    Role required: DEVELOPER (owner) or ADMIN.
    """
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user.role == UserRole.DEVELOPER:
        if project.developer_id != current_user.id:
             raise HTTPException(status_code=403, detail="Not authorized")
    elif current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.MANAGER]:
         raise HTTPException(status_code=403, detail="Not authorized")
    
    project.is_hidden = is_hidden
    await project.save()
    return project
