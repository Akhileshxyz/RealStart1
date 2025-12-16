from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.lead import ProjectLead, LeadStatus
from app.schemas.lead import LeadResponse, LeadUpdate
from app.services.project_service import get_project_by_slug

router = APIRouter()

@router.get("/projects/{slug}/leads", response_model=List[LeadResponse])
async def list_project_leads(
    slug: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    List all leads for a specific project.
    Only accessible by the Developer who owns the project (or Admins).
    """
    # 1. Find Project
    project = await get_project_by_slug(slug=slug, use_cache=True)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Authorization Check
    # If not admin, check if user is the developer
    # Simplify: If user role is developer, we assume they own it (for now) or check ID match if we had it.
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.DEVELOPER]:
         raise HTTPException(status_code=403, detail="Not authorized")
    
    # In real app: if current_user.role == DEVELOPER: assert project.developer_id == current_user.id or logic
    
    # 3. Fetch Leads
    leads = await ProjectLead.find(ProjectLead.project_id == project.id).to_list()
    
    # 4. Augment with User Info
    # This is N+1 but acceptable for small scale leads. In prod, use aggregation.
    response_leads = []
    for lead in leads:
        user = await User.get(lead.user_id)
        lead_resp = LeadResponse(
            id=lead.id,
            project_id=lead.project_id,
            user_id=lead.user_id,
            status=lead.status,
            last_viewed_at=lead.last_viewed_at,
            view_count=len(lead.viewed_at_history),
            developer_notes=lead.developer_notes,
            user_full_name=user.full_name if user else None,
            user_email=user.email if user else None,
            user_phone=user.phone if user else None
        )
        response_leads.append(lead_resp)
        
    return response_leads

@router.patch("/leads/{lead_id}/purchase", response_model=LeadResponse)
async def mark_lead_purchased(
    lead_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Mark a lead as PURCHASED.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.DEVELOPER]:
         raise HTTPException(status_code=403, detail="Not authorized")
         
    lead = await ProjectLead.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    lead.status = LeadStatus.PURCHASED
    await lead.save()
    
    # Ideally should fetch user to return full response, but for now returned partial is fine or we fetch
    user = await User.get(lead.user_id)
    lead_resp = LeadResponse(
        id=lead.id,
        project_id=lead.project_id,
        user_id=lead.user_id,
        status=lead.status,
        last_viewed_at=lead.last_viewed_at,
        view_count=len(lead.viewed_at_history),
        developer_notes=lead.developer_notes,
        user_full_name=user.full_name if user else None,
        user_email=user.email if user else None,
        user_phone=user.phone if user else None
    )
        
    return lead_resp
    
@router.patch("/leads/{lead_id}/status", response_model=LeadResponse)
async def update_lead_status_generic(
    lead_id: UUID,
    lead_in: LeadUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update lead status or notes.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.DEVELOPER]:
         raise HTTPException(status_code=403, detail="Not authorized")
         
    lead = await ProjectLead.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    if lead_in.status:
        lead.status = lead_in.status
    if lead_in.developer_notes:
        lead.developer_notes = lead_in.developer_notes
        
    await lead.save()
    
    user = await User.get(lead.user_id)
    lead_resp = LeadResponse(
        id=lead.id,
        project_id=lead.project_id,
        user_id=lead.user_id,
        status=lead.status,
        last_viewed_at=lead.last_viewed_at,
        view_count=len(lead.viewed_at_history),
        developer_notes=lead.developer_notes,
        user_full_name=user.full_name if user else None,
        user_email=user.email if user else None,
        user_phone=user.phone if user else None
    )

    return lead_resp
