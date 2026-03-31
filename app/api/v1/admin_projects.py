from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.schemas.project import ProjectResponse, ProjectAdminUpdate
from app.utils.cache_invalidation import invalidate_project_cache
from app.models.subscription import DeveloperSubscription, SubscriptionStatus
from typing import Dict
from app.models.communication import ProjectCommunication, CommunicationType

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
    import traceback
    try:
        query = {}
        if status:
            query = {"status": status}
        
        if query:
            projects = await Project.find(query).skip(skip).limit(limit).to_list()
        else:
            projects = await Project.find_all().skip(skip).limit(limit).to_list()
            
        # --- Enhancement: Populate Owner & Subscription Details ---
        developer_ids = list(set([p.developer_id for p in projects if p.developer_id]))
        if developer_ids:
            # Fetch Developers
            # FIX: Use In operator with Beanie syntax or _id query
            # Using raw query with _id for safety
            developers = await User.find({"_id": {"$in": developer_ids}}).to_list()
            dev_map = {u.id: u for u in developers}
            
            # Fetch Active/Latest Subscriptions
            # Optimization: Just fetch all subs for these devs. If many, might need optimization.
            subscriptions = await DeveloperSubscription.find(
                {"developer_id": {"$in": developer_ids}, "status": SubscriptionStatus.ACTIVE}
            ).to_list()
            sub_map = {s.developer_id: s for s in subscriptions}
            
            # Populate Response
            enhanced_projects = []
            for p in projects:
                p_resp = ProjectResponse.model_validate(p.model_dump())
                
                # Owner Info
                if p.developer_id and p.developer_id in dev_map:
                    dev = dev_map[p.developer_id]
                    p_resp.owner_name = dev.full_name
                    p_resp.owner_email = dev.email
                    p_resp.owner_phone = dev.phone
                    
                # Subscription Info
                if p.developer_id and p.developer_id in sub_map:
                    sub = sub_map[p.developer_id]
                    p_resp.subscription_end_date = sub.end_date
                    # p_resp.subscription_plan_name = ... (Would need plan fetch)
                
                enhanced_projects.append(p_resp)
            return enhanced_projects
            
        # If no developers/enhancement needed, still map to ProjectResponse
        return [ProjectResponse.model_validate(p.model_dump()) for p in projects]
    except Exception as e:
        with open("c:\\laragon\\www\\realstart-be\\logs\\debug_error.log", "w") as f:
            f.write(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/{project_id}/details", response_model=ProjectResponse)
async def get_project_details_admin(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get detailed project view for admin.
    """
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    p_resp = ProjectResponse.model_validate(project.model_dump())
    
    # Populate Developer Info
    if project.developer_id:
        dev = await User.get(project.developer_id)
        if dev:
            p_resp.owner_name = dev.full_name
            p_resp.owner_email = dev.email
            p_resp.owner_phone = dev.phone
            
        # Subscription
        sub = await DeveloperSubscription.find_one(
            {"developer_id": project.developer_id, "status": SubscriptionStatus.ACTIVE},
            sort=[("end_date", -1)]
        )
        if sub:
            p_resp.subscription_end_date = sub.end_date
            
    return p_resp

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

    # Invalidate all project caches
    await invalidate_project_cache(project_id=project.id, slug=project.slug)

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

    # Invalidate all project caches
    await invalidate_project_cache(project_id=project.id, slug=project.slug)

    return project

@router.patch("/{project_id}/feature", response_model=ProjectResponse)
async def toggle_featured_project(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Toggle the `is_featured` flag on a project.
    Featured projects appear in the homepage Featured Projects section.
    Invalidates both the project cache and the public featured-projects cache.
    """
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.is_featured = not project.is_featured
    await project.save()

    # Invalidate project cache + featured-projects homepage cache
    await invalidate_project_cache(project_id=project.id, slug=project.slug)
    from app.core.redis_client import redis_client
    await redis_client.delete_pattern(redis_client.make_key("public", "featured_projects", "*"))

    return project

# --- Communication Logging ---

@router.post("/{project_id}/communication", response_model=ProjectCommunication)
async def log_project_communication(
    project_id: UUID,
    comm_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Log a communication (call, email, etc.) for a project.
    """
    project = await Project.get(project_id)
    if not project:
         raise HTTPException(status_code=404, detail="Project not found")
         
    comm = ProjectCommunication(
        project_id=project_id,
        admin_id=current_user.id,
        **comm_data
    )
    await comm.insert()
    return comm

@router.get("/{project_id}/communication", response_model=List[ProjectCommunication])
async def get_project_communication_history(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get communication history for a project.
    """
    project = await Project.get(project_id)
    if not project:
         raise HTTPException(status_code=404, detail="Project not found")
         
    history = await ProjectCommunication.find({"project_id": project_id}).sort("-date").to_list()
    return history
