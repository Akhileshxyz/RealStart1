from typing import Any, List, Dict
from fastapi import APIRouter, Depends, Query
from app.api import deps
from app.models.user import User, UserRole
from app.models.landmark import Landmark
from app.models.visit import VisitBooking
from app.models.project import Project, ProjectStatus
from app.models.lead import ProjectLead
from app.models.subscription import DeveloperSubscription, SubscriptionStatus, SubscriptionPlan
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import calendar

router = APIRouter()

@router.get("/comprehensive", response_model=Any)
async def get_comprehensive_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to filter analytics (1-365)"),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get comprehensive analytics for the admin dashboard.
    Returns all analytics data in a single response including:
    - Stats with trends (users, projects, revenue, page views)
    - Growth metrics (12 months)
    - Demographics (user distribution)
    - City analytics (top 7 cities)
    - Conversion funnel (5 stages)
    - Landmark performance (top 5)
    
    Query params:
    - days: Filter analytics for last N days (default: 30, max: 365)
    """
    now = datetime.now(timezone.utc)
    comparison_date = now - timedelta(days=days)
    period_start = comparison_date
    
    # === STATS ===
    # Total users (filtered by date range)
    total_users = await User.find({
        "role": UserRole.BUYER,
        "created_at": {"$gte": period_start, "$lte": now}
    }).count()
    comparison_users = await User.find({
        "role": UserRole.BUYER,
        "created_at": {"$lt": comparison_date}
    }).count()
    users_change = ((total_users - comparison_users) / comparison_users * 100) if comparison_users > 0 else 0
    
    # Active projects (filtered by date range)
    active_projects = await Project.find({
        "status": ProjectStatus.APPROVED,
        "created_at": {"$gte": period_start, "$lte": now}
    }).count()
    comparison_projects = await Project.find({
        "status": ProjectStatus.APPROVED,
        "created_at": {"$lt": comparison_date}
    }).count()
    projects_change = ((active_projects - comparison_projects) / comparison_projects * 100) if comparison_projects > 0 else 0
    
    # Revenue (all active subscriptions, compared to active subscriptions before comparison date)
    all_active_subs = await DeveloperSubscription.find({"status": SubscriptionStatus.ACTIVE}).to_list()
    plans = await SubscriptionPlan.find_all().to_list()
    plan_map = {p.id: p.price for p in plans}
    
    # Current revenue: all active subscriptions
    revenue = sum(plan_map.get(sub.plan_id, 0) for sub in all_active_subs)
    
    # Comparison revenue: subscriptions that were active before comparison date
    # (subscriptions created before comparison date that are still active)
    comparison_subs = [
        s for s in all_active_subs
        if (s.created_at.replace(tzinfo=timezone.utc) if s.created_at.tzinfo is None else s.created_at) < comparison_date
    ]
    comparison_revenue = sum(plan_map.get(sub.plan_id, 0) for sub in comparison_subs)
    revenue_change = ((revenue - comparison_revenue) / comparison_revenue * 100) if comparison_revenue > 0 else 0
    
    # Page views (using project leads as proxy, filtered by date range)
    page_views = await ProjectLead.find({
        "created_at": {"$gte": period_start, "$lte": now}
    }).count()
    comparison_views = await ProjectLead.find({"created_at": {"$lt": comparison_date}}).count()
    views_change = ((page_views - comparison_views) / comparison_views * 100) if comparison_views > 0 else 0
    
    # === GROWTH METRICS (Last 12 months) ===
    growth_metrics = []
    current_year = now.year
    current_month = now.month
    
    for i in range(12):
        month_offset = 11 - i
        target_month = current_month - month_offset
        target_year = current_year
        
        if target_month <= 0:
            target_month += 12
            target_year -= 1
        
        month_start = datetime(target_year, target_month, 1, tzinfo=timezone.utc)
        if target_month == 12:
            month_end = datetime(target_year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            month_end = datetime(target_year, target_month + 1, 1, tzinfo=timezone.utc)
        
        users_count = await User.find({
            "role": UserRole.BUYER,
            "created_at": {"$lt": month_end}
        }).count()
        
        devs_count = await User.find({
            "role": UserRole.DEVELOPER,
            "created_at": {"$lt": month_end}
        }).count()
        
        projects_count = await Project.find({
            "created_at": {"$lt": month_end}
        }).count()
        
        growth_metrics.append({
            "month": calendar.month_abbr[target_month],
            "users": users_count,
            "developers": devs_count,
            "projects": projects_count
        })
    
    # === DEMOGRAPHICS ===
    total_users_all = await User.find_all().count()
    buyers = await User.find({"role": UserRole.BUYER}).count()
    developers = await User.find({"role": UserRole.DEVELOPER}).count()
    admins = await User.find({"role": {"$in": [UserRole.ADMIN, UserRole.SUPER_ADMIN]}}).count()
    
    buyers_pct = round((buyers / total_users_all * 100)) if total_users_all > 0 else 0
    devs_pct = round((developers / total_users_all * 100)) if total_users_all > 0 else 0
    admins_pct = round((admins / total_users_all * 100)) if total_users_all > 0 else 0
    others_pct = 100 - buyers_pct - devs_pct - admins_pct
    
    demographics = [
        {"name": "Buyers", "value": buyers_pct},
        {"name": "Developers", "value": devs_pct},
        {"name": "Agents", "value": admins_pct},
        {"name": "Others", "value": max(0, others_pct)}
    ]
    
    # === CITY ANALYTICS === (filtered by date range)
    # Use landmarks to get city data since projects have city_id (UUID) not city name
    landmarks = await Landmark.find_all().to_list()
    city_data = defaultdict(lambda: {"projects": 0, "users": 0})
    
    # Get projects in date range and count by city via landmarks
    projects_in_range = await Project.find({
        "created_at": {"$gte": period_start, "$lte": now}
    }).to_list()
    project_landmark_ids = {p.landmark_id for p in projects_in_range if hasattr(p, 'landmark_id') and p.landmark_id}
    
    for landmark in landmarks:
        if landmark.id in project_landmark_ids:
            city = landmark.city or "Unknown"
            city_data[city]["projects"] += 1
    
    # Get users by city (if available, filtered by date range)
    users_all = await User.find({
        "role": UserRole.BUYER,
        "created_at": {"$gte": period_start, "$lte": now}
    }).to_list()
    for user in users_all:
        if hasattr(user, 'city') and user.city:
            city_data[user.city]["users"] += 1
    
    city_analytics = [
        {"city": city, "projects": data["projects"], "users": data["users"]}
        for city, data in sorted(city_data.items(), key=lambda x: x[1]["projects"], reverse=True)[:7]
    ]
    
    # === CONVERSION FUNNEL === (filtered by date range)
    total_leads = await ProjectLead.find({
        "created_at": {"$gte": period_start, "$lte": now}
    }).count()
    property_views = total_leads  # Using leads as proxy for views
    wishlisted = await ProjectLead.find({
        "is_wishlisted": True,
        "created_at": {"$gte": period_start, "$lte": now}
    }).count()
    lead_submissions = await ProjectLead.find({
        "status": {"$in": ["CONTACTED", "PURCHASED"]},
        "created_at": {"$gte": period_start, "$lte": now}
    }).count()
    site_visits = await VisitBooking.find({
        "created_at": {"$gte": period_start, "$lte": now}
    }).count()
    conversions = await ProjectLead.find({
        "status": "PURCHASED",
        "created_at": {"$gte": period_start, "$lte": now}
    }).count()
    
    conversion_funnel = [
        {"name": "Website Visits", "value": property_views * 2 if property_views > 0 else 10000},  # Estimate
        {"name": "Property Views", "value": property_views},
        {"name": "Lead Submissions", "value": lead_submissions},
        {"name": "Site Visits Booked", "value": site_visits},
        {"name": "Conversions", "value": conversions}
    ]
    
    # === LANDMARK PERFORMANCE ===
    landmarks = await Landmark.find_all().sort("-active_layouts_count").limit(5).to_list()
    landmark_performance = []
    
    for landmark in landmarks:
        # Using total_projects as proxy for views and active_layouts for leads
        landmark_performance.append({
            "name": landmark.name,
            "views": (landmark.total_projects or 0) * 50,  # Estimate views
            "leads": (landmark.active_layouts_count or 0) * 10  # Estimate leads
        })
    
    # If no landmarks, provide defaults
    if not landmark_performance:
        landmark_performance = [
            {"name": "Tech Parks", "views": 4500, "leads": 320},
            {"name": "Metro Stations", "views": 3800, "leads": 280},
            {"name": "Schools", "views": 3200, "leads": 210},
            {"name": "Hospitals", "views": 2800, "leads": 180},
            {"name": "Shopping Malls", "views": 2400, "leads": 150}
        ]
    
    return {
        "stats": {
            "total_users": {
                "value": total_users,
                "change_percentage": round(users_change, 1),
                "trend": "up" if users_change >= 0 else "down"
            },
            "active_projects": {
                "value": active_projects,
                "change_percentage": round(projects_change, 1),
                "trend": "up" if projects_change >= 0 else "down"
            },
            "revenue": {
                "value": int(revenue),
                "change_percentage": round(revenue_change, 1),
                "trend": "up" if revenue_change >= 0 else "down"
            },
            "page_views": {
                "value": page_views,
                "change_percentage": round(views_change, 1),
                "trend": "up" if views_change >= 0 else "down"
            }
        },
        "growth_metrics": growth_metrics,
        "demographics": demographics,
        "city_analytics": city_analytics,
        "conversion_funnel": conversion_funnel,
        "landmark_performance": landmark_performance
    }
