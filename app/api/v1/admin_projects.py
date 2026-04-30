from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from app.api import deps
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.schemas.project import ProjectResponse, ProjectAdminUpdate, ProjectSelection
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
        query = {"is_active": {"$ne": False}}
        if status:
            if status == ProjectStatus.DELETED:
                query = {"status": ProjectStatus.DELETED}
            else:
                query = {"status": status, "is_active": {"$ne": False}}
        
        projects = await Project.find(query).skip(skip).limit(limit).to_list()
            
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

@router.patch("/{project_id}/pending", response_model=ProjectResponse)
async def move_to_pending_admin(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Move a project back to PENDING status.
    """
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.status = ProjectStatus.PENDING
    await project.save()

    # Invalidate cache
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

@router.get("/selection", response_model=List[ProjectSelection])
async def get_projects_selection_list(
    status: Optional[ProjectStatus] = Query(None),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Lightweight list of projects for selection lists.
    """
    query = {}
    if status:
        query["status"] = status
    
    return await Project.find(query).project(ProjectSelection).to_list()
    
@router.delete("/{project_id}", response_model=dict)
async def delete_project_admin(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Delete a project listing (Soft Delete).
    """
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Soft Delete
    project.is_active = False
    project.status = ProjectStatus.DELETED
    await project.save()
    
    # Invalidate cache
    await invalidate_project_cache(project_id=project.id, slug=project.slug)
    
    return {"message": "Project deleted successfully"}

@router.post("/bulk-delete", response_model=dict)
async def bulk_delete_projects_admin(
    project_ids: List[UUID] = Body(..., embed=True),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Delete multiple projects (Soft Delete).
    """
    if not project_ids:
        raise HTTPException(status_code=400, detail="No project IDs provided")
        
    # Update projects
    await Project.find({"_id": {"$in": project_ids}}).update({"$set": {"is_active": False, "status": ProjectStatus.DELETED}})
    
    # Invalidate cache for all
    # For bulk, we might just invalidate all or do one by one. 
    # One by one is safer if slug is needed, but slower.
    # Let's invalidate general project list cache if possible, or just individual ones.
    for pid in project_ids:
        await invalidate_project_cache(project_id=pid)
        
    return {"message": f"Successfully deleted {len(project_ids)} projects"}
