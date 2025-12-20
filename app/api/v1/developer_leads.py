from typing import Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from app.api import deps
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.lead import ProjectLead, LeadStatus
from app.schemas.lead import LeadResponse, LeadUpdate
from app.schemas.developer_dashboard import (
    DeveloperDashboardMetrics,
    ProjectMetrics,
    EnhancedDeveloperDashboard,
    TrendDataPoint,
    LeadStatusCount,
    CityMetrics,
    RecentActivityItem,
    ProjectPerformance
)
from app.services.project_service import get_project_by_slug
from app.core.redis_client import redis_client
from app.core.config import settings
from app.services.permission_service import PermissionService
from app.core.permissions import TeamLeadsPermission
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
    """
    # 1. Find Project (to get developer_id for scope check)
    project = await get_project_by_slug(slug=slug, use_cache=True)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Authorization Check (Basic View Access)
    await PermissionService.enforce(current_user, TeamLeadsPermission.VIEW_LEADS_BASIC.value, developer_id_scope=project.developer_id)
    
    # 3. Check for Full Access (to decide on redaction)
    can_view_full = await PermissionService.has_permission(current_user, TeamLeadsPermission.VIEW_LEADS_FULL.value)

    # 4. Fetch Leads
    leads = await ProjectLead.find(ProjectLead.project_id == project.id).to_list()
    
    # 5. Augment with User Info
    response_leads = []
    for lead in leads:
        user = await User.get(lead.user_id)
        
        # Redaction Logic
        user_email = user.email if user else None
        user_phone = user.phone if user else None
        
        if not can_view_full:
            # Redact
            user_email = "***@***.com" if user_email else None
            user_phone = "******" + user_phone[-4:] if user_phone and len(user_phone) > 4 else "**********"

        lead_resp = LeadResponse(
            id=lead.id,
            project_id=lead.project_id,
            user_id=lead.user_id,
            status=lead.status,
            last_viewed_at=lead.last_viewed_at,
            view_count=len(lead.viewed_at_history),
            developer_notes=lead.developer_notes,
            user_full_name=user.full_name if user else "Unknown User",
            user_email=user_email,
            user_phone=user_phone
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
    lead = await ProjectLead.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    # Scope check requires knowing the project's developer
    project = await Project.get(lead.project_id)
    if not project:
         raise HTTPException(status_code=404, detail="Project linked to lead not found")

    await PermissionService.enforce(current_user, TeamLeadsPermission.MANAGE_LEADS.value, developer_id_scope=project.developer_id)
         
    lead.status = LeadStatus.PURCHASED
    await lead.save()
    
    user = await User.get(lead.user_id)
    # Return full details as managing leads implies full access usually
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
    lead = await ProjectLead.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    project = await Project.get(lead.project_id)
    if not project:
         raise HTTPException(status_code=404, detail="Project linked to lead not found")

    await PermissionService.enforce(current_user, TeamLeadsPermission.MANAGE_LEADS.value, developer_id_scope=project.developer_id)
         
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


from app.core.permissions import TeamDashboardPermission

@router.get("/dashboard", response_model=EnhancedDeveloperDashboard)
async def get_developer_dashboard(
    period: str = Query("week", regex="^(day|week|month|year)$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get comprehensive analytics dashboard for developer with:
    - Total Visitors, Visit Bookings, Legal Consultations, Interested Buyers
    - Visitors & Leads Trend (time series)
    - Leads by Project
    - Leads by City (user location)
    - Projects Performance with conversion rates
    - Recent Activity feed
    - Lead Status Distribution
    """
    # Authorization check
    await PermissionService.enforce(current_user, TeamDashboardPermission.VIEW_DASHBOARD.value)

    # Calculate date range
    if start_date and end_date:
        period_start = start_date
        period_end = end_date
        period_type = "custom"
    else:
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
            period_start = period_end - timedelta(days=7)

    # Get developer's projects
    if current_user.role == UserRole.DEVELOPER:
        projects = await Project.find(Project.developer_id == current_user.id).to_list()
    elif current_user.role in [UserRole.SALES, UserRole.MARKETING, UserRole.MANAGER]:
        from app.models.team import DeveloperTeamMember
        member = await DeveloperTeamMember.find_one(DeveloperTeamMember.user_id == current_user.id)
        if member:
            projects = await Project.find(Project.developer_id == member.developer_id).to_list()
        else:
            projects = []
    else:
        projects = await Project.find_all().to_list()

    # Initialize collections
    from collections import defaultdict
    total_visitors_set = set()
    visit_bookings_count = 0
    legal_consultations_count = 0
    interested_buyers_set = set()
    trend_data = defaultdict(lambda: {"visitors": set(), "leads": set()})
    city_data = defaultdict(lambda: {"leads": set(), "visitors": set()})
    status_counts = defaultdict(int)
    recent_activities = []
    project_performance_data = []
    leads_by_project_data = []

    # Process each project
    for project in projects:
        leads = await ProjectLead.find(ProjectLead.project_id == project.id).to_list()

        project_visitors = set()
        project_plot_visits = 0
        project_legal = 0
        project_interested = 0
        project_views = 0
        project_total_leads = len(leads)

        for lead in leads:
            user = await User.get(lead.user_id)
            status_counts[lead.status.value] += 1

            # Process views
            if lead.viewed_at_history:
                for view_time in lead.viewed_at_history:
                    if period_start <= view_time <= period_end:
                        total_visitors_set.add(lead.user_id)
                        project_visitors.add(lead.user_id)
                        project_views += 1
                        date_key = view_time.date().isoformat()
                        trend_data[date_key]["visitors"].add(lead.user_id)
                        # Use address as city proxy (can be enhanced with actual city lookup)
                        city = getattr(project, 'address', None) or "Unknown"
                        city_data[city]["visitors"].add(lead.user_id)

                        if len(recent_activities) < 50:
                            recent_activities.append({
                                "activity_type": "view",
                                "user_name": user.full_name if user else "Unknown",
                                "user_email": user.email if user else None,
                                "project_name": project.name,
                                "project_slug": project.slug,
                                "timestamp": view_time
                            })

            # Process wishlists
            if lead.is_wishlisted and lead.wishlisted_at and period_start <= lead.wishlisted_at <= period_end:
                interested_buyers_set.add(lead.user_id)
                project_interested += 1
                date_key = lead.wishlisted_at.date().isoformat()
                trend_data[date_key]["leads"].add(lead.user_id)
                city = getattr(project, 'address', None) or "Unknown"
                city_data[city]["leads"].add(lead.user_id)

                if len(recent_activities) < 50:
                    recent_activities.append({
                        "activity_type": "wishlist",
                        "user_name": user.full_name if user else "Unknown",
                        "user_email": user.email if user else None,
                        "project_name": project.name,
                        "project_slug": project.slug,
                        "timestamp": lead.wishlisted_at
                    })

            # Process legal requests
            if lead.is_legal_requested and lead.legal_requested_at and period_start <= lead.legal_requested_at <= period_end:
                legal_consultations_count += 1
                project_legal += 1
                date_key = lead.legal_requested_at.date().isoformat()
                trend_data[date_key]["leads"].add(lead.user_id)
                city = getattr(project, 'address', None) or "Unknown"
                city_data[city]["leads"].add(lead.user_id)

                if len(recent_activities) < 50:
                    recent_activities.append({
                        "activity_type": "legal_request",
                        "user_name": user.full_name if user else "Unknown",
                        "user_email": user.email if user else None,
                        "project_name": project.name,
                        "project_slug": project.slug,
                        "timestamp": lead.legal_requested_at
                    })

            # Process visit bookings
            if lead.visit_booked_at and period_start <= lead.visit_booked_at <= period_end:
                visit_bookings_count += 1
                project_plot_visits += 1
                date_key = lead.visit_booked_at.date().isoformat()
                trend_data[date_key]["leads"].add(lead.user_id)
                city = getattr(project, 'address', None) or "Unknown"
                city_data[city]["leads"].add(lead.user_id)

                if len(recent_activities) < 50:
                    recent_activities.append({
                        "activity_type": "visit_booking",
                        "user_name": user.full_name if user else "Unknown",
                        "user_email": user.email if user else None,
                        "project_name": project.name,
                        "project_slug": project.slug,
                        "timestamp": lead.visit_booked_at
                    })

        # Project performance
        conversion_rate = (project_interested / len(project_visitors) * 100) if project_visitors else 0
        project_performance_data.append(ProjectPerformance(
            project_id=project.id,
            project_name=project.name,
            project_slug=project.slug,
            city=getattr(project, 'address', None),
            visitors=len(project_visitors),
            conversion_rate=round(conversion_rate, 2),
            total_leads=project_total_leads
        ))

        # Leads by project
        leads_by_project_data.append(ProjectMetrics(
            project_id=project.id,
            project_name=project.name,
            project_slug=project.slug,
            city=getattr(project, 'address', None),
            visitors=len(project_visitors),
            plot_visits=project_plot_visits,
            legal_consultations=project_legal,
            interested_visitors=project_interested,
            total_views=project_views
        ))

    # Build trend data
    trend_list = [TrendDataPoint(date=date_str, visitors=len(trend_data[date_str]["visitors"]),
                  leads=len(trend_data[date_str]["leads"])) for date_str in sorted(trend_data.keys())]

    # Build city metrics
    city_metrics_list = [CityMetrics(city=city, leads=len(data["leads"]), visitors=len(data["visitors"]))
                         for city, data in city_data.items()]
    city_metrics_list.sort(key=lambda x: x.leads, reverse=True)

    # Build lead status distribution
    status_distribution = [LeadStatusCount(status=status, count=count) for status, count in status_counts.items()]

    # Sort recent activities
    recent_activities.sort(key=lambda x: x["timestamp"], reverse=True)
    recent_activity_items = [RecentActivityItem(**activity) for activity in recent_activities[:20]]

    # Build response
    return EnhancedDeveloperDashboard(
        period_start=period_start,
        period_end=period_end,
        period_type=period_type,
        total_visitors=len(total_visitors_set),
        visit_bookings=visit_bookings_count,
        legal_consultations=legal_consultations_count,
        interested_buyers=len(interested_buyers_set),
        visitors_leads_trend=trend_list,
        leads_by_project=leads_by_project_data,
        leads_by_city=city_metrics_list,
        projects_performance=project_performance_data,
        recent_activity=recent_activity_items,
        lead_status_distribution=status_distribution
    )
