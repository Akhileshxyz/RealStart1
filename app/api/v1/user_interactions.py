from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.api import deps
from app.models.lead import ProjectLead, LeadStatus
from app.models.project import Project
from app.models.user import User
from app.services.webhook_service import WebhookService

from app.services.project_service import get_project_by_slug
from app.utils.cache_invalidation import invalidate_lead_cache, invalidate_user_cache

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/{slug}/view")
async def log_view(
    slug: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Log a view for a project.
    """
    project = await get_project_by_slug(slug=slug, use_cache=True)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    lead = await ProjectLead.find_one(ProjectLead.project_id == project.id, ProjectLead.user_id == current_user.id)
    if not lead:
        lead = ProjectLead(project_id=project.id, user_id=current_user.id)
    
    # Update view history
    now = datetime.now(timezone.utc)
    lead.last_viewed_at = now
    if lead.viewed_at_history is None:
        lead.viewed_at_history = []
    lead.viewed_at_history.append(now)
    
    # Ensure status is at least VIEWED
    # (If it was higher like CONTACTED, don't downgrade it, but usually VIEWED is the base)
    
    await lead.save()
    # Invalidate caches
    await invalidate_lead_cache(project.id, current_user.id)
    return {"message": "View logged"}

@router.post("/{slug}/wishlist")
@limiter.limit("30/minute")
async def toggle_wishlist(
    request: Request,
    slug: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Toggle wishlist status for a project.
    """
    project = await get_project_by_slug(slug=slug, use_cache=True)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    lead = await ProjectLead.find_one(ProjectLead.project_id == project.id, ProjectLead.user_id == current_user.id)
    if not lead:
        lead = ProjectLead(project_id=project.id, user_id=current_user.id)
    
    # Toggle
    lead.is_wishlisted = not lead.is_wishlisted
    if lead.is_wishlisted:
        lead.wishlisted_at = datetime.now(timezone.utc)
        await WebhookService.dispatch_event("lead.wishlist", {
            "project_slug": slug,
            "user_email": current_user.email,
            "is_wishlisted": True
        }, project.developer_id)
    
    await lead.save()
    # Invalidate caches
    await invalidate_lead_cache(project.id, current_user.id)
    return {"message": "Updated", "is_wishlisted": lead.is_wishlisted}

@router.post("/{slug}/legal-request")
@limiter.limit("10/minute")
async def request_legal(
    request: Request,
    slug: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Request legal consultation.
    """
    project = await get_project_by_slug(slug=slug, use_cache=True)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    lead = await ProjectLead.find_one(ProjectLead.project_id == project.id, ProjectLead.user_id == current_user.id)
    if not lead:
        lead = ProjectLead(project_id=project.id, user_id=current_user.id)
    
    lead.is_legal_requested = True
    lead.legal_requested_at = datetime.now(timezone.utc)
    lead.status = LeadStatus.CONTACTED # Implicitly interested
    await lead.save()
    
    await WebhookService.dispatch_event("lead.legal_request", {
            "project_slug": slug,
            "user_email": current_user.email,
            "user_phone": current_user.phone
    }, project.developer_id)
    
    return {"message": "Legal consultation requested"}

@router.post("/{slug}/book-visit")
@limiter.limit("10/minute")
async def book_visit(
    request: Request,
    slug: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Book a visit. (Simplified: just marks as booked now)
    """
    project = await get_project_by_slug(slug=slug, use_cache=True)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    lead = await ProjectLead.find_one(ProjectLead.project_id == project.id, ProjectLead.user_id == current_user.id)
    if not lead:
        lead = ProjectLead(project_id=project.id, user_id=current_user.id)
    
    lead.visit_booked_at = datetime.now(timezone.utc)
    lead.visit_status = "BOOKED"
    await lead.save()
    
    await WebhookService.dispatch_event("lead.visit_booked", {
            "project_slug": slug,
            "user_email": current_user.email,
            "user_phone": current_user.phone
    }, project.developer_id)
    
    return {"message": "Visit booked"}
