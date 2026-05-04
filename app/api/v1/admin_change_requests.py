from typing import Any, List, Optional
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from app.api import deps
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.change_request import ProjectChangeRequest, RequestStatus, RequestType
from app.schemas.change_request import ChangeRequestResponse
from app.utils.cache_invalidation import invalidate_project_cache

router = APIRouter()

@router.get("/", response_model=List[ChangeRequestResponse])
async def list_change_requests(
    status: Optional[RequestStatus] = Query(None),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    List change requests. Filter by status if provided.
    """
    import traceback
    try:
        if status:
            requests = await ProjectChangeRequest.find(ProjectChangeRequest.status == status).sort("-created_at").to_list()
        else:
            requests = await ProjectChangeRequest.find_all().sort("-created_at").to_list()
        return requests
    except Exception as e:
        with open("c:\\laragon\\www\\realstart-be\\logs\\debug_error.log", "a") as f:
            f.write(f"\n--- Change Requests Error {datetime.now()} ---\n")
            f.write(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{request_id}/approve", response_model=ChangeRequestResponse)
async def approve_request(
    request_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Approve a change request and apply changes.
    """
    req = await ProjectChangeRequest.get(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if req.status != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request already processed")
        
    project = await Project.get(req.project_id)
    if not project:
         # Edge case: Project deleted meanwhile?
         req.status = RequestStatus.REJECTED
         req.admin_notes = "Project no longer exists"
         await req.save()
         raise HTTPException(status_code=404, detail="Target Project not found")

    # Apply Changes
    if req.request_type == RequestType.UPDATE:
        # Apply update
        from app.schemas.project import ProjectUpdate
        
        # Re-validate and convert types (strings back to UUID/datetime)
        try:
            update_data = ProjectUpdate.model_validate(req.data).model_dump(exclude_unset=True)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid data in change request: {str(e)}")

        if update_data:
            # Track old slug for cache invalidation
            old_slug = project.slug
            
            # Update data with current timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            # Use direct $set update for maximum reliability
            await project.update({"$set": update_data})
            
            # Refresh project object from DB to ensure it has latest state
            project = await Project.get(project.id)
            if not project:
                raise HTTPException(status_code=404, detail="Project lost during update")
            
            # Invalidate cache
            await invalidate_project_cache(project_id=project.id, slug=old_slug)
            if project.slug != old_slug:
                await invalidate_project_cache(slug=project.slug)
        
    elif req.request_type == RequestType.DELETE:
        # Delete project
        await project.delete()
        
    # Mark Approved
    req.status = RequestStatus.APPROVED
    req.updated_at = datetime.now(timezone.utc)
    await req.save()
    
    return req

@router.post("/{request_id}/reject", response_model=ChangeRequestResponse)
async def reject_request(
    request_id: UUID,
    reason: str = Body(embed=True),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Reject a change request.
    """
    req = await ProjectChangeRequest.get(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    req.status = RequestStatus.REJECTED
    req.admin_notes = reason
    req.updated_at = datetime.now(timezone.utc)
    await req.save()
    
    return req
