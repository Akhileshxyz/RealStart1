from typing import Any, List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User, UserRole
from app.models.project import Project, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.permission_service import PermissionService
from app.core.permissions import TeamProjectsPermission

router = APIRouter()

from app.services.subscription_service import SubscriptionService
from app.api.v1.locality import forward_geocode_mappls
from app.services.analytics_service import ProjectAnalyticsService

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

    try:
        # Check Subscription Limits
        if current_user.role == UserRole.DEVELOPER:
            await SubscriptionService.check_project_limit(current_user.id)

        # Check slug uniqueness
        existing = await Project.find_one(Project.slug == project_in.slug)
        if existing:
            raise HTTPException(status_code=400, detail="Project slug already exists")

        # If user is a developer, ensure they link it to themselves or their organization
        if current_user.role == UserRole.DEVELOPER:
             project_in.developer_id = current_user.id
        
        # Auto-populating Latitude/Longitude if missing
        if not project_in.latitude or not project_in.longitude:
            geo_query = None
            if project_in.google_maps_link:
                geo_query = project_in.google_maps_link
            elif project_in.landmark:
                geo_query = f"{project_in.landmark}, {project_in.city or ''}"
            elif project_in.address_line_1:
                geo_query = f"{project_in.address_line_1}, {project_in.city or ''}"
            
            if geo_query:
                # Attempt to Geocode
                geo_data = await forward_geocode_mappls(geo_query)
                if geo_data and geo_data.get("latitude"):
                    project_in.latitude = float(geo_data["latitude"])
                    project_in.longitude = float(geo_data["longitude"])
        
        project = Project(
            **project_in.model_dump(),
            status=ProjectStatus.PENDING # Enforce Pending
        )
        await project.insert()
        return ProjectResponse.model_validate(project.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Debug Error: {str(e)}")

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
    # Permission Check
    await PermissionService.enforce(current_user, TeamProjectsPermission.VIEW_PROJECTS.value)

    # Determine Developer ID Scope
    developer_id = None
    if current_user.role == UserRole.DEVELOPER:
        developer_id = current_user.id
    elif current_user.role in [UserRole.SALES, UserRole.MARKETING, UserRole.MANAGER]:
         # For team members, we need to find their linked developer
         # Ideally, we should cache this or store in token, but here we query
         from app.models.team import DeveloperTeamMember
         member = await DeveloperTeamMember.find_one(DeveloperTeamMember.user_id == current_user.id)
         if member:
             developer_id = member.developer_id
    
    if developer_id:
        projects = await Project.find(Project.developer_id == developer_id).skip(skip).limit(limit).to_list()
    else:
        # Admins or unlinked users (should be caught by enforce, but strictly Admins see all?)
        # For now, let's say Admins see all
        projects = await Project.find_all().skip(skip).limit(limit).to_list()
        
    return [ProjectResponse.model_validate(p.model_dump()) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get specific project details and documents.
    """
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Access Control Enforced via Service
    await PermissionService.enforce(
        current_user, 
        TeamProjectsPermission.VIEW_PROJECTS.value, 
        developer_id_scope=project.developer_id
    )

    # Fetch Analytics
    analytics_data = await ProjectAnalyticsService.get_project_dashboard_stats(project.id)
    
    # Calculate Sold Units if not explicitly set
    if project.sold_units is None and project.total_units is not None and project.available_units is not None:
        project.sold_units = project.total_units - project.available_units

    p_resp = ProjectResponse.model_validate(project.model_dump())
    p_resp.analytics = analytics_data
    
    return p_resp

@router.put("/{project_id}", response_model=Any)
async def update_project(
    project_id: UUID,
    project_in: ProjectUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a project.
    - If status is APPROVED: Creates a ProjectChangeRequest.
    - If PENDING/REJECTED/DRAFT: Updates directly.
    """
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Access Control Enforced via Service
    await PermissionService.enforce(current_user, TeamProjectsPermission.EDIT_PROJECTS.value, developer_id_scope=project.developer_id)

    # Logic
    if project.status == ProjectStatus.APPROVED and current_user.role in [UserRole.DEVELOPER, UserRole.MANAGER]: # Managers might edit too
        # Create Change Request
        from app.models.change_request import ProjectChangeRequest, RequestType
        
        request = ProjectChangeRequest(
            project_id=project.id,
            request_type=RequestType.UPDATE,
            data=project_in.model_dump(exclude_unset=True)
        )
        await request.insert()
        return {"message": "Update request submitted for approval", "request_id": request.id}
    else:
        # Direct Update
        update_data = project_in.model_dump(exclude_unset=True)
        
        if current_user.role in [UserRole.DEVELOPER, UserRole.MANAGER, UserRole.SALES, UserRole.MARKETING]:
             if project.status == ProjectStatus.REJECTED:
                 update_data["status"] = ProjectStatus.PENDING
        
        await project.set(update_data)
        project.updated_at = datetime.utcnow()
        await project.save()
        return ProjectResponse.model_validate(project.model_dump())

@router.delete("/{project_id}", response_model=dict)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a listing (Soft Delete).
    """
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Access Control
    await PermissionService.enforce(current_user, TeamProjectsPermission.EDIT_PROJECTS.value, developer_id_scope=project.developer_id)

    # Soft Delete
    project.is_active = False
    project.status = ProjectStatus.DELETED
    await project.save()
    
    return {"message": "Project deleted successfully"}

@router.patch("/{project_id}/hide", response_model=ProjectResponse)
async def toggle_project_visibility(
    project_id: UUID,
    is_hidden: bool = Body(..., embed=True),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Toggle project visibility (Hide/Show).
    """
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Access Control
    await PermissionService.enforce(current_user, TeamProjectsPermission.EDIT_PROJECTS.value, developer_id_scope=project.developer_id)
    
    project.is_hidden = is_hidden
    if is_hidden:
        project.hidden_at = datetime.utcnow()
    else:
        project.hidden_at = None
        
    await project.save()
    return ProjectResponse.model_validate(project.model_dump())
