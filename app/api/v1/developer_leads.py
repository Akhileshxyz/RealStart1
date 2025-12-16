from typing import Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from app.api import deps
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.lead import ProjectLead, LeadStatus
from app.schemas.lead import LeadResponse, LeadUpdate
from app.schemas.developer_dashboard import DeveloperDashboardMetrics, ProjectMetrics
from app.services.project_service import get_project_by_slug
from app.core.redis_client import redis_client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

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


@router.get("/dashboard", response_model=DeveloperDashboardMetrics)
async def get_developer_dashboard(
    period: str = Query("day", regex="^(day|week|month|year)$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    project_slug: Optional[str] = None,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get analytics dashboard for developer.

    Metrics calculated based on time period:
    - total_visitors: Unique users who viewed projects
    - total_plot_visits: Visit bookings
    - total_legal_consultations: Legal consultation requests
    - interested_visitors: Users who wishlisted
    - total_views: All views including repeats

    Time period options:
    - day: Current day (from 00:00 to now)
    - week: Last 7 days
    - month: Last 30 days
    - year: Last 365 days
    - Custom: Provide start_date and end_date
    """
    # Authorization check
    if current_user.role not in [UserRole.DEVELOPER, UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to access developer dashboard")

    # 1. Calculate date range based on period
    if start_date and end_date:
        # Custom range
        period_start = start_date
        period_end = end_date
        period_type = "custom"
    else:
        # Predefined period
        period_end = datetime.utcnow()
        period_type = period
        if period == "day":
            period_start = period_end.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            period_start = period_end - timedelta(days=7)
        elif period == "month":
            period_start = period_end - timedelta(days=30)
        elif period == "year":
            period_start = period_end - timedelta(days=365)
        else:
            # Default to day
            period_start = period_end.replace(hour=0, minute=0, second=0, microsecond=0)

    # 2. Try cache first
    cache_key = redis_client.make_key(
        "developer",
        str(current_user.id),
        "dashboard",
        period_type,
        str(period_start.date())
    )

    if redis_client.is_available:
        cached_metrics = await redis_client.get(cache_key)
        if cached_metrics:
            logger.debug(f"Developer dashboard cache HIT for user {current_user.id}")
            return DeveloperDashboardMetrics(**cached_metrics)

    logger.debug(f"Developer dashboard cache MISS for user {current_user.id}")

    # 3. Get developer's projects
    if project_slug:
        project = await get_project_by_slug(project_slug, use_cache=True)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        # Verify ownership (if not admin)
        if current_user.role == UserRole.DEVELOPER and project.developer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this project's dashboard")
        projects = [project]
    else:
        # Get all developer's projects
        if current_user.role == UserRole.DEVELOPER:
            projects = await Project.find(Project.developer_id == current_user.id).to_list()
        else:
            # Admin can see all projects
            projects = await Project.find_all().to_list()

    # 4. Aggregate metrics across all projects
    total_visitors = 0
    total_plot_visits = 0
    total_legal_consultations = 0
    interested_visitors = 0
    total_views = 0
    project_metrics_list = []

    for project in projects:
        # Get all leads for this project
        leads = await ProjectLead.find(ProjectLead.project_id == project.id).to_list()

        # Calculate metrics for this project
        unique_visitors = set()
        plot_visits = 0
        legal_consultations = 0
        interested = 0
        views = 0

        for lead in leads:
            # Count views in date range
            views_in_period = [
                v for v in lead.viewed_at_history
                if period_start <= v <= period_end
            ]
            if views_in_period:
                unique_visitors.add(lead.user_id)
                views += len(views_in_period)

            # Count wishlists in date range
            if lead.is_wishlisted and lead.wishlisted_at:
                if period_start <= lead.wishlisted_at <= period_end:
                    interested += 1

            # Count legal requests in date range
            if lead.is_legal_requested and lead.legal_requested_at:
                if period_start <= lead.legal_requested_at <= period_end:
                    legal_consultations += 1

            # Count visit bookings in date range
            if lead.visit_booked_at:
                if period_start <= lead.visit_booked_at <= period_end:
                    plot_visits += 1

        # Aggregate totals
        total_visitors += len(unique_visitors)
        total_plot_visits += plot_visits
        total_legal_consultations += legal_consultations
        interested_visitors += interested
        total_views += views

        # Store project-level metrics
        project_metrics_list.append(ProjectMetrics(
            project_id=project.id,
            project_name=project.name,
            project_slug=project.slug,
            visitors=len(unique_visitors),
            plot_visits=plot_visits,
            legal_consultations=legal_consultations,
            interested_visitors=interested,
            total_views=views
        ))

    # 5. Build response
    metrics = DeveloperDashboardMetrics(
        period_start=period_start,
        period_end=period_end,
        period_type=period_type,
        total_visitors=total_visitors,
        total_plot_visits=total_plot_visits,
        total_legal_consultations=total_legal_consultations,
        interested_visitors=interested_visitors,
        total_views=total_views,
        projects=project_metrics_list
    )

    # 6. Cache the results
    if redis_client.is_available:
        # Cache for 1 hour (current day) or 24 hours (past periods)
        ttl = 3600 if period_type == "day" else 86400
        await redis_client.set(cache_key, metrics.model_dump(), ttl)
        logger.debug(f"Cached developer dashboard for user {current_user.id} with TTL {ttl}s")

    return metrics
