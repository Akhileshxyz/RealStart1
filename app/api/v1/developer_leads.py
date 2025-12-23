from typing import Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from collections import defaultdict
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
    ProjectPerformance,
    AnalyticsDashboard,
    OverviewMetrics,
    WeeklyPerformancePoint,
    TopLocation,
    TrafficSource,
    DeviceBreakdown,
    GeographicDistribution,
    ConversionFunnelStage,
    ConversionMetric,
    LeadQualityDistribution,
    ProjectPerformanceRow
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


@router.get("/analytics", response_model=AnalyticsDashboard)
async def get_developer_analytics(
    period: str = Query("month", regex="^(week|month|year)$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get comprehensive analytics dashboard for developer with:
    - Overview: Total Views, Total Leads, Wishlists, Conversion Rate
    - Performance Trends: Weekly Performance
    - Top Locations
    - Traffic Sources breakdown
    - Device Breakdown (Mobile, Desktop, Tablet)
    - Geographic Distribution
    - Conversion Funnel (6 stages)
    - Conversion Metrics (View to Lead, Lead to Site Visit, Site Visit to Booking)
    - Lead Quality Distribution (Hot, Warm, Cold)
    - Project Performance table
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
        if period == "week":
            period_start = period_end - timedelta(days=7)
        elif period == "month":
            period_start = period_end - timedelta(days=30)
        elif period == "year":
            period_start = period_end - timedelta(days=365)
        else:
            period_start = period_end - timedelta(days=30)

    # Calculate comparison period (previous period of same length)
    period_length = period_end - period_start
    comparison_start = period_start - period_length
    comparison_end = period_start

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

    # Initialize tracking variables
    total_views = 0
    total_leads = 0
    wishlists = 0
    unique_viewers = set()
    city_stats = defaultdict(lambda: {"views": 0, "leads": 0})
    weekly_stats = defaultdict(lambda: {"views": 0, "leads": 0, "conversions": 0})
    project_stats = {}

    # Conversion funnel stages
    page_views = 0
    unique_visitors = set()
    project_views = 0
    enquiries = 0
    site_visits = 0
    conversions = 0

    # Lead quality buckets
    hot_leads = 0
    warm_leads = 0
    cold_leads = 0

    # Comparison period metrics
    comp_views = 0
    comp_leads = 0
    comp_site_visits = 0

    # Process each project
    for project in projects:
        leads = await ProjectLead.find(ProjectLead.project_id == project.id).to_list()

        project_views_count = 0
        project_leads_count = 0
        project_conversions = 0

        for lead in leads:
            # Count as lead
            is_current_period_lead = False
            is_comparison_period_lead = False

            # Process views
            if lead.viewed_at_history:
                for view_time in lead.viewed_at_history:
                    if period_start <= view_time <= period_end:
                        total_views += 1
                        page_views += 1
                        project_views += 1
                        unique_visitors.add(lead.user_id)
                        unique_viewers.add(lead.user_id)
                        project_views_count += 1
                        is_current_period_lead = True

                        # Weekly stats
                        week_num = (view_time - period_start).days // 7
                        week_key = f"Week {week_num + 1}"
                        weekly_stats[week_key]["views"] += 1

                        # City stats
                        city = getattr(project, 'address', None) or "Unknown"
                        city_stats[city]["views"] += 1
                    elif comparison_start <= view_time <= comparison_end:
                        comp_views += 1

            # Count lead if they had any interaction in current period
            if is_current_period_lead:
                total_leads += 1
                project_leads_count += 1
                enquiries += 1

                city = getattr(project, 'address', None) or "Unknown"
                city_stats[city]["leads"] += 1

                # Weekly leads
                if lead.viewed_at_history:
                    first_view = min([v for v in lead.viewed_at_history if period_start <= v <= period_end])
                    week_num = (first_view - period_start).days // 7
                    week_key = f"Week {week_num + 1}"
                    weekly_stats[week_key]["leads"] += 1

            # Process wishlists
            if lead.is_wishlisted and lead.wishlisted_at:
                if period_start <= lead.wishlisted_at <= period_end:
                    wishlists += 1

            # Process site visits
            if lead.visit_booked_at:
                if period_start <= lead.visit_booked_at <= period_end:
                    site_visits += 1
                    week_num = (lead.visit_booked_at - period_start).days // 7
                    week_key = f"Week {week_num + 1}"
                    weekly_stats[week_key]["conversions"] += 1
                elif comparison_start <= lead.visit_booked_at <= comparison_end:
                    comp_site_visits += 1

            # Count conversions (purchased leads)
            if lead.status == LeadStatus.PURCHASED:
                if is_current_period_lead:
                    conversions += 1
                    project_conversions += 1

            # Lead quality scoring (Hot: wishlist + visit booked, Warm: wishlist OR visit, Cold: just viewed)
            if is_current_period_lead:
                if lead.is_wishlisted and lead.visit_booked_at:
                    hot_leads += 1
                elif lead.is_wishlisted or lead.visit_booked_at or lead.is_legal_requested:
                    warm_leads += 1
                else:
                    cold_leads += 1

        # Project performance
        conversion_rate = (project_conversions / project_views_count * 100) if project_views_count > 0 else 0

        # Determine trend (simplified: compare current conversion to average)
        avg_conversion = (conversions / total_views * 100) if total_views > 0 else 0
        if conversion_rate > avg_conversion * 1.1:
            trend = "up"
        elif conversion_rate < avg_conversion * 0.9:
            trend = "down"
        else:
            trend = "stable"

        project_stats[str(project.id)] = ProjectPerformanceRow(
            project_id=project.id,
            project_name=project.name,
            project_slug=project.slug,
            views=project_views_count,
            leads=project_leads_count,
            conversion=round(conversion_rate, 2),
            trend=trend
        )

    # Calculate metrics
    conversion_rate = (total_leads / total_views * 100) if total_views > 0 else 0
    view_to_lead_rate = (enquiries / page_views * 100) if page_views > 0 else 0
    lead_to_visit_rate = (site_visits / enquiries * 100) if enquiries > 0 else 0
    visit_to_booking_rate = (conversions / site_visits * 100) if site_visits > 0 else 0

    # Calculate comparison period rates for change percentage
    comp_view_to_lead = (comp_leads / comp_views * 100) if comp_views > 0 else 0
    comp_lead_to_visit = (comp_site_visits / comp_leads * 100) if comp_leads > 0 else 0

    view_to_lead_change = ((view_to_lead_rate - comp_view_to_lead) / comp_view_to_lead * 100) if comp_view_to_lead > 0 else 0
    lead_to_visit_change = ((lead_to_visit_rate - comp_lead_to_visit) / comp_lead_to_visit * 100) if comp_lead_to_visit > 0 else 0

    # Build overview
    overview = OverviewMetrics(
        total_views=total_views,
        total_leads=total_leads,
        wishlists=wishlists,
        conversion_rate=round(conversion_rate, 2)
    )

    # Build weekly performance (ensure all weeks are present)
    num_weeks = max(1, (period_end - period_start).days // 7)
    weekly_performance = []
    for i in range(num_weeks):
        week_key = f"Week {i + 1}"
        weekly_performance.append(WeeklyPerformancePoint(
            week=week_key,
            views=weekly_stats[week_key]["views"],
            leads=weekly_stats[week_key]["leads"],
            conversions=weekly_stats[week_key]["conversions"]
        ))

    # Build top locations
    sorted_cities = sorted(city_stats.items(), key=lambda x: x[1]["leads"], reverse=True)[:5]
    top_locations = [
        TopLocation(
            city=city,
            views=stats["views"],
            leads=stats["leads"],
            share=round((stats["leads"] / total_leads * 100) if total_leads > 0 else 0, 2)
        )
        for city, stats in sorted_cities
    ]

    # Traffic sources - empty list as not tracked in DB
    traffic_sources = []

    # Device breakdown - all zeros as not tracked in DB
    device_breakdown = DeviceBreakdown(
        mobile=0.0,
        desktop=0.0,
        tablet=0.0
    )

    # Geographic distribution
    geographic_distribution = [
        GeographicDistribution(
            city=city,
            views=stats["views"],
            leads=stats["leads"],
            share=round((stats["views"] / total_views * 100) if total_views > 0 else 0, 2)
        )
        for city, stats in sorted(city_stats.items(), key=lambda x: x[1]["views"], reverse=True)
    ]

    # Conversion funnel
    conversion_funnel = [
        ConversionFunnelStage(stage="Page Views", count=page_views, percentage=100.0),
        ConversionFunnelStage(stage="Unique Visitors", count=len(unique_visitors),
                             percentage=round((len(unique_visitors) / page_views * 100) if page_views > 0 else 0, 2)),
        ConversionFunnelStage(stage="Project Views", count=project_views,
                             percentage=round((project_views / page_views * 100) if page_views > 0 else 0, 2)),
        ConversionFunnelStage(stage="Enquiries", count=enquiries,
                             percentage=round((enquiries / page_views * 100) if page_views > 0 else 0, 2)),
        ConversionFunnelStage(stage="Site Visits", count=site_visits,
                             percentage=round((site_visits / page_views * 100) if page_views > 0 else 0, 2)),
        ConversionFunnelStage(stage="Conversions", count=conversions,
                             percentage=round((conversions / page_views * 100) if page_views > 0 else 0, 2))
    ]

    # Conversion metrics
    conversion_metrics = [
        ConversionMetric(
            metric_name="View to Lead Rate",
            rate=round(view_to_lead_rate, 2),
            change=round(view_to_lead_change, 2)
        ),
        ConversionMetric(
            metric_name="Lead to Site Visit",
            rate=round(lead_to_visit_rate, 2),
            change=round(lead_to_visit_change, 2)
        ),
        ConversionMetric(
            metric_name="Site Visit to Booking",
            rate=round(visit_to_booking_rate, 2),
            change=0.0  # No historical comparison available yet
        )
    ]

    # Lead quality
    lead_quality = LeadQualityDistribution(
        hot=hot_leads,
        warm=warm_leads,
        cold=cold_leads
    )

    # Project performance
    project_performance = sorted(project_stats.values(), key=lambda x: x.leads, reverse=True)

    return AnalyticsDashboard(
        period_start=period_start,
        period_end=period_end,
        period_type=period_type,
        overview=overview,
        weekly_performance=weekly_performance,
        top_locations=top_locations,
        traffic_sources=traffic_sources,
        device_breakdown=device_breakdown,
        geographic_distribution=geographic_distribution,
        conversion_funnel=conversion_funnel,
        conversion_metrics=conversion_metrics,
        lead_quality=lead_quality,
        project_performance=project_performance
    )
