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
    if status:
        requests = await ProjectChangeRequest.find(ProjectChangeRequest.status == status).sort("-created_at").to_list()
    else:
        requests = await ProjectChangeRequest.find_all().sort("-created_at").to_list()
    return requests

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
        update_data = req.data
        update_data["updated_at"] = datetime.now(timezone.utc)
        await project.set(update_data)
        
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
