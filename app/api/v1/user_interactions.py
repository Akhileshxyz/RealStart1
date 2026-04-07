from typing import Any, List
from uuid import UUID
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from datetime import datetime, timezone
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.api import deps
from app.models.lead import ProjectLead, LeadStatus
from app.models.project import Project
from app.models.user import User
from app.services.webhook_service import WebhookService
from beanie.operators import In

from app.services.project_service import get_project_by_slug
from app.models.legal_call import LegalCallRequest
from app.schemas.visit import VisitBookingRequest, VisitListItem, ProjectMiniDetail
from app.utils.cache_invalidation import invalidate_lead_cache, invalidate_user_cache, invalidate_developer_dashboard_cache

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
    await invalidate_developer_dashboard_cache(project.developer_id)
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
    await invalidate_developer_dashboard_cache(project.developer_id)
    return {"message": "Updated", "is_wishlisted": lead.is_wishlisted}

@router.post("/{slug}/legal-request")
@limiter.limit("10/minute")
async def request_legal(
    request: Request,
    slug: str,
    topics: list[str] = Body(["General Inquiry"]),
    scheduled_time: datetime = Body(None),
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
    
    # Create Legal Call Request Document
    legal_request = LegalCallRequest(
        user_id=current_user.id,
        project_id=project.id,
        topics=topics,
        scheduled_time=scheduled_time,
        created_at=datetime.utcnow()
    )
    await legal_request.save()
    
    await WebhookService.dispatch_event("lead.legal_request", {
            "project_slug": slug,
            "user_email": current_user.email,
            "user_phone": current_user.phone
    }, project.developer_id)

    # Invalidate developer dashboard cache
    await invalidate_developer_dashboard_cache(project.developer_id)

    return {"message": "Legal consultation requested"}

@router.get("/visits", response_model=list[VisitListItem])
async def list_my_visits(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    List all visits booked by the current user.
    """
    # Fetch all leads with a booked status for this user
    leads = await ProjectLead.find(
        ProjectLead.user_id == current_user.id,
        ProjectLead.visit_status == "BOOKED"
    ).sort("-visit_booked_at").to_list()

    results = []
    # Project IDs to fetch
    project_ids = [l.project_id for l in leads]
    projects_list = await Project.find(In(Project.id, project_ids)).to_list()
    project_map = {p.id: p for p in projects_list}

    for lead in leads:
        project = project_map.get(lead.project_id)
        if not project:
            continue
            
        # Format location name
        loc_parts = []
        if project.landmark: loc_parts.append(project.landmark)
        elif project.address_line_1: loc_parts.append(project.address_line_1)
        if project.city: loc_parts.append(project.city)
        location_name = ", ".join(loc_parts) if loc_parts else "Bengaluru"

        results.append(VisitListItem(
            project=ProjectMiniDetail(
                id=project.id,
                title=project.name,
                location_name=location_name,
                price_display=f"₹{int(project.min_price):,}/sqft" if project.min_price else "Price on Request",
                hero_image=project.gallery_images[0] if project.gallery_images else None
            ),
            visit_date=lead.visit_date or "",
            visit_time=lead.visit_time or "",
            visit_type=lead.visit_type or "in_person",
            cab_required=lead.cab_required,
            status=lead.visit_status or "BOOKED",
            booked_at=lead.visit_booked_at or lead.created_at
        ))

    return results

@router.post("/visits")
@limiter.limit("5/minute")
async def book_visit(
    request: Request,
    booking: VisitBookingRequest,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Comprehensive Visit Booking API.
    Validates slot again on server before confirming.
    """
    project = await Project.get(booking.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 1. Server-side Availability Validation (Safety Check)
    # Ensure this exact slot isn't already taken
    existing_booking = await ProjectLead.find_one(
        ProjectLead.project_id == booking.project_id,
        ProjectLead.visit_date == booking.date,
        ProjectLead.visit_time == booking.time,
        ProjectLead.visit_status == "BOOKED"
    )
    if existing_booking:
        raise HTTPException(status_code=409, detail="This slot has just been booked by someone else. Please choose another.")

    # 2. Get or create lead
    lead = await ProjectLead.find_one(
        ProjectLead.project_id == project.id, 
        ProjectLead.user_id == current_user.id
    )
    if not lead:
        lead = ProjectLead(project_id=project.id, user_id=current_user.id)
    
    # 3. Update with detailed visit data
    lead.visit_booked_at = datetime.now(timezone.utc)
    lead.visit_date = booking.date
    lead.visit_time = booking.time
    lead.visit_type = booking.visit_type
    lead.cab_required = booking.cab_required
    lead.visitor_name = booking.name
    lead.visitor_phone = booking.mobile
    lead.visit_status = "BOOKED"
    lead.status = LeadStatus.CONTACTED # Upgrade status
    
    await lead.save()
    
    # 4. Dispatch Webhook
    await WebhookService.dispatch_event("lead.visit_booked", {
            "project_name": project.name,
            "project_id": str(project.id),
            "user_email": current_user.email,
            "visit_date": booking.date,
            "visit_time": booking.time,
            "visit_type": booking.visit_type,
            "cab_required": booking.cab_required
    }, project.developer_id)

    # Invalidate developer dashboard cache
    await invalidate_developer_dashboard_cache(project.developer_id)

    return {
        "message": "Visit booked successfully",
        "booking_details": {
            "project": project.name,
            "date": booking.date,
            "time": booking.time,
            "visit_type": booking.visit_type
        }
    }

class CancelVisitRequest(BaseModel):
    project_id: UUID

@router.post("/visits/cancel")
async def cancel_visit(
    request: Request,
    data: CancelVisitRequest,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Cancel an existing site visit and free up the time slot.
    """
    lead = await ProjectLead.find_one(
        ProjectLead.project_id == data.project_id,
        ProjectLead.user_id == current_user.id
    )
    if not lead or lead.visit_status != "BOOKED":
        raise HTTPException(status_code=404, detail="No active booking found for this project.")

    project = await Project.get(data.project_id)
    
    # Update status to CANCELLED (frees the slot in availability API)
    old_date = lead.visit_date
    old_time = lead.visit_time
    
    lead.visit_status = "CANCELLED"
    lead.updated_at = datetime.now(timezone.utc)
    await lead.save()

    # Notify Developer
    if project:
        await WebhookService.dispatch_event("lead.visit_cancelled", {
                "project_name": project.name,
                "project_id": str(project.id),
                "user_email": current_user.email,
                "visit_date": old_date,
                "visit_time": old_time
        }, project.developer_id)

    # Invalidate developer dashboard cache
    if project:
        await invalidate_developer_dashboard_cache(project.developer_id)

    return {"message": "Visit cancelled successfully. The slot is now available."}
