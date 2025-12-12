from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from app.api import deps
from app.models.lead import ProjectLead, LeadStatus
from app.models.project import Project
from app.models.user import User
from app.services.webhook_service import WebhookService

router = APIRouter()

@router.post("/{slug}/wishlist")
async def toggle_wishlist(
    slug: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Toggle wishlist status for a project.
    """
    project = await Project.find_one(Project.slug == slug)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    lead = await ProjectLead.find_one(ProjectLead.project_id == project.id, ProjectLead.user_id == current_user.id)
    if not lead:
        lead = ProjectLead(project_id=project.id, user_id=current_user.id)
    
    # Toggle
    lead.is_wishlisted = not lead.is_wishlisted
    if lead.is_wishlisted:
        lead.wishlisted_at = datetime.utcnow()
        await WebhookService.dispatch_event("lead.wishlist", {
            "project_slug": slug,
            "user_email": current_user.email,
            "is_wishlisted": True
        }, project.developer_id)
    
    await lead.save()
    return {"message": "Updated", "is_wishlisted": lead.is_wishlisted}

@router.post("/{slug}/legal-request")
async def request_legal(
    slug: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Request legal consultation.
    """
    project = await Project.find_one(Project.slug == slug)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    lead = await ProjectLead.find_one(ProjectLead.project_id == project.id, ProjectLead.user_id == current_user.id)
    if not lead:
        lead = ProjectLead(project_id=project.id, user_id=current_user.id)
    
    lead.is_legal_requested = True
    lead.legal_requested_at = datetime.utcnow()
    lead.status = LeadStatus.CONTACTED # Implicitly interested
    await lead.save()
    
    await WebhookService.dispatch_event("lead.legal_request", {
            "project_slug": slug,
            "user_email": current_user.email,
            "user_phone": current_user.phone
    }, project.developer_id)
    
    return {"message": "Legal consultation requested"}

@router.post("/{slug}/book-visit")
async def book_visit(
    slug: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Book a visit. (Simplified: just marks as booked now)
    """
    project = await Project.find_one(Project.slug == slug)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    lead = await ProjectLead.find_one(ProjectLead.project_id == project.id, ProjectLead.user_id == current_user.id)
    if not lead:
        lead = ProjectLead(project_id=project.id, user_id=current_user.id)
    
    lead.visit_booked_at = datetime.utcnow()
    lead.visit_status = "BOOKED"
    await lead.save()
    
    await WebhookService.dispatch_event("lead.visit_booked", {
            "project_slug": slug,
            "user_email": current_user.email,
            "user_phone": current_user.phone
    }, project.developer_id)
    
    return {"message": "Visit booked"}
