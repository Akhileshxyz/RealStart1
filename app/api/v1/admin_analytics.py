from typing import Any, List, Dict
from fastapi import APIRouter, Depends
from app.api import deps
from app.models.user import User, UserRole
from app.models.landmark import Landmark
from app.models.visit import VisitBooking
from app.models.project import Project
from app.models.lead import ProjectLead
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/cities", response_model=Any)
async def get_city_analytics(
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get analytics by city (aggregated from Landmarks).
    Returns number of landmarks and active layouts per city.
    """
    # Since we don't have a City model, we aggregate via Landmarks
    landmarks = await Landmark.find_all().to_list()
    
    city_stats = {}
    for landmark in landmarks:
        city = landmark.city or "Unknown"
        if city not in city_stats:
            city_stats[city] = {
                "city": city,
                "landmarks_count": 0,
                "total_projects": 0,
                "active_layouts": 0
            }
        city_stats[city]["landmarks_count"] += 1
        city_stats[city]["total_projects"] += (landmark.total_projects or 0)
        city_stats[city]["active_layouts"] += (landmark.active_layouts_count or 0)
    
    return list(city_stats.values())

@router.get("/landmarks", response_model=Any)
async def get_landmark_analytics(
    limit: int = 10,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get top performing landmarks based on active layouts and total projects.
    """
    landmarks = await Landmark.find_all().sort("-active_layouts_count").limit(limit).to_list()
    return landmarks

@router.get("/growth", response_model=Any)
async def get_growth_metrics(
    days: int = 30,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get growth analytics for Users and Developers over the last N days.
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Simple aggregation: Count users created after start_date
    new_users = await User.find({"created_at": {"$gte": start_date}, "role": UserRole.BUYER}).count()
    new_developers = await User.find({"created_at": {"$gte": start_date}, "role": UserRole.DEVELOPER}).count()
    
    total_users = await User.find({"role": UserRole.BUYER}).count()
    total_developers = await User.find({"role": UserRole.DEVELOPER}).count()

    return {
        "period_days": days,
        "new_users": new_users,
        "new_developers": new_developers,
        "total_users": total_users,
        "total_developers": total_developers
    }

@router.get("/site-visits-by-location", response_model=Any)
async def get_site_visits_analytics(
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get site visit bookings count. 
    (Future: breakdown by city/landmark requires joining with Project)
    """
    total_visits = await VisitBooking.find_all().count()
    # Placeholder for more detailed breakdown
    return {
        "total_visits": total_visits
    }

@router.get("/demographics", response_model=Any)
async def get_user_demographics(
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get user demographics analytics (Age, Gender distribution).
    """
    users = await User.find({"role": UserRole.BUYER}).to_list()
    
    age_distribution = {"18-24": 0, "25-34": 0, "35-44": 0, "45-54": 0, "55+": 0, "unknown": 0}
    gender_distribution = {}
    engagement_distribution = {"HIGH": 0, "MID": 0, "LOW": 0}
    
    for user in users:
        # Age
        if user.age:
            if user.age < 25: age_distribution["18-24"] += 1
            elif user.age < 35: age_distribution["25-34"] += 1
            elif user.age < 45: age_distribution["35-44"] += 1
            elif user.age < 55: age_distribution["45-54"] += 1
            else: age_distribution["55+"] += 1
        else:
            age_distribution["unknown"] += 1
            
        # Gender
        g = user.gender.value if user.gender else "UNKNOWN"
        gender_distribution[g] = gender_distribution.get(g, 0) + 1
        
        # Engagement
        engagement_distribution[user.engagement_level] += 1
        
    return {
        "age_distribution": age_distribution,
        "gender_distribution": gender_distribution,
        "engagement_scores": engagement_distribution
    }
    return {
        "age_distribution": age_distribution,
        "gender_distribution": gender_distribution,
        "engagement_scores": engagement_distribution
    }

@router.get("/funnel", response_model=Any)
async def get_funnel_analytics(
    days: int = 30,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get user conversion funnel analytics.
    Stages: Impressions (Views) -> Wishlisted -> Contacted/Lead -> Visit Booked -> Legal Request
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Filter leads created/updated in the last N days (approx for activity)
    # Using 'updated_at' to capture recent interactions on older leads too
    active_leads = await ProjectLead.find({"updated_at": {"$gte": start_date}}).to_list()
    
    total_views = 0 # Top of funnel (users who viewed a project)
    wishlisted = 0
    contacted = 0
    visit_booked = 0
    legal_requested = 0
    
    for lead in active_leads:
        total_views += 1
        if lead.is_wishlisted:
            wishlisted += 1
        if lead.status in ["CONTACTED", "PURCHASED"]: # Or check if contact fields populated
            contacted += 1
        if lead.visit_booked_at:
            visit_booked += 1
        if lead.is_legal_requested:
            legal_requested += 1
            
    # Calculate conversion rates relative to Total Views
    def rate(count, total):
        return round((count / total) * 100, 2) if total > 0 else 0
        
    return {
        "period_days": days,
        "stages": {
            "views": total_views,
            "wishlisted": wishlisted,
            "contacted": contacted,
            "visit_booked": visit_booked,
            "legal_requested": legal_requested
        },
        "rates": {
            "view_to_wishlist": rate(wishlisted, total_views),
            "view_to_contact": rate(contacted, total_views),
            "view_to_visit": rate(visit_booked, total_views),
            "view_to_legal": rate(legal_requested, total_views)
        }
    }
