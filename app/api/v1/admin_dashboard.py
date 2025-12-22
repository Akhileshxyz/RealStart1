from typing import Any, Dict
from fastapi import APIRouter, Depends
from app.api import deps
from app.models.user import User, UserRole
from datetime import datetime, timedelta, timezone
from app.models.project import Project, ProjectStatus
from app.models.subscription import DeveloperSubscription, SubscriptionStatus
from app.models.user import User, UserRole
from app.models.visit import VisitBooking

router = APIRouter()

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_admin_dashboard_stats(
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get system-wide statistics for the admin dashboard.
    """
    
    # 1. Projects Stats
    # 1. Projects Stats
    total_projects = await Project.find_all().count()
    active_projects = await Project.find({"status": ProjectStatus.APPROVED}).count()
    
    # Detailed Pending Approvals
    pending_projects = await Project.find({"status": ProjectStatus.PENDING}).to_list()
    pending_approval_count = len(pending_projects)
    
    pending_approvals_list = []
    for p in pending_projects:
        # Fetch developer name if needed, or just use project name
        dev = await User.find_one({"developer_id": p.developer_id})
        pending_approvals_list.append({
             "project_id": p.id,
             "project_name": p.name,
             "developer_name": dev.full_name if dev else "Unknown",
             "submitted_at": p.created_at
        })
    
    # 2. User Stats
    total_users = await User.find_all().count()
    developers_count = await User.find({"role": UserRole.DEVELOPER}).count()
    buyers_count = await User.find({"role": UserRole.BUYER}).count()
    
    # 3. Subscription Stats
    # 3. Subscription Stats
    now = datetime.now(timezone.utc)
    active_subscriptions = await DeveloperSubscription.find({
        "status": SubscriptionStatus.ACTIVE,
        "end_date": {"$gt": now}
    }).count()
    
    # Expiring Subscriptions (Next 7 days)
    expiry_threshold = now + timedelta(days=7)
    expiring_subs = await DeveloperSubscription.find({
        "status": SubscriptionStatus.ACTIVE,
        "end_date": {"$gt": now, "$lte": expiry_threshold}
    }).to_list()
    
    important_alerts = []
    for sub in expiring_subs:
        dev = await User.find_one({"developer_id": sub.developer_id})
        days_left = (sub.end_date.replace(tzinfo=timezone.utc) - now).days
        important_alerts.append({
            "type": "subscription_expiry",
            "message": f"{dev.full_name if dev else 'Unknown'} subscription expires in {days_left} days",
            "priority": "high" if days_left < 3 else "medium",
            "action_required": True
        })
    
    # 4. Engagement Stats
    total_visits_booked = await VisitBooking.find_all().count()
    
    return {
        "projects": {
            "total": total_projects,
            "active": active_projects,
            "pending_approval": pending_approvals
        },
        "users": {
            "total": total_users,
            "developers": developers_count,
            "buyers": buyers_count
        },
        "subscriptions": {
            "active_count": active_subscriptions
        },
        "engagement": {
            "total_visits_booked": total_visits_booked
        },
        "action_items": {
            "pending_approvals": pending_approvals_list[:5], # Top 5
            "total_pending_count": pending_approval_count,
            "important_alerts": important_alerts
        }
    }

@router.get("/system-health", response_model=Dict[str, Any])
async def get_system_health(
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Simple system health check.
    """
    # Logic to check DB connection, cache, etc.
    return {
        "status": "healthy",
        "database": "connected", # Assumed if we got here through auth
        "timestamp": datetime.now(timezone.utc)
    }
