from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from app.api import deps
from app.models.user import User, UserRole
from app.models.developer import Developer
from app.models.subscription import SubscriptionPlan, DeveloperSubscription, SubscriptionStatus
from app.schemas.subscription import (
    SubscriptionPlanCreate, 
    SubscriptionPlanResponse, 
    SubscriptionResponse,
    SubscriptionStatsResponse,
    DetailedSubscriptionResponse
)
from datetime import datetime, timedelta, timezone

router = APIRouter()

@router.post("/plans", response_model=SubscriptionPlanResponse)
async def create_plan(
    plan_in: SubscriptionPlanCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new subscription plan.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    plan = SubscriptionPlan(**plan_in.model_dump())
    await plan.insert()
    return plan

@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def list_plans(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    List all subscription plans.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    plans = await SubscriptionPlan.find_all().to_list()
    return plans

@router.get("/subscriptions")
async def list_developer_subscriptions(
    status: Optional[SubscriptionStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return (1-100)"),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get detailed subscription information with pagination:
    - Developer name and email
    - Plan name and price
    - Start date, end date, and days left
    - Status (ACTIVE, EXPIRED, CANCELLED, PENDING)
    - Auto renewal setting
    
    Returns paginated results with total count.
    Optional filter by status.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Build query
    query = {}
    if status:
        query["status"] = status
    
    # Get total count
    total_count = await DeveloperSubscription.find(query).count() if query else await DeveloperSubscription.count()
    
    # Get subscriptions with pagination
    subs = await DeveloperSubscription.find(query).skip(skip).limit(limit).to_list() if query else await DeveloperSubscription.find_all().skip(skip).limit(limit).to_list()
    
    # Get all plans
    plans = await SubscriptionPlan.find_all().to_list()
    plan_map = {p.id: p for p in plans}
    
    # Build detailed response
    now = datetime.now(timezone.utc)
    results = []
    
    for sub in subs:
        # Get developer information
        developer = await Developer.get(sub.developer_id)
        
        # Get user information for email
        user = await User.find_one({"developer_id": sub.developer_id})
        
        # Get plan information
        plan = plan_map.get(sub.plan_id)
        
        # Calculate days left
        end_date_aware = sub.end_date.replace(tzinfo=timezone.utc) if sub.end_date.tzinfo is None else sub.end_date
        days_left = (end_date_aware - now).days
        
        results.append(DetailedSubscriptionResponse(
            id=sub.id,
            developer_name=developer.name if developer else "Unknown Developer",
            developer_email=user.email if user else None,
            plan_name=plan.name if plan else "Unknown Plan",
            plan_price=plan.price if plan else 0.0,
            start_date=sub.start_date,
            end_date=sub.end_date,
            days_left=max(0, days_left) if sub.status == SubscriptionStatus.ACTIVE else 0,
            status=sub.status,
            auto_renewal=sub.auto_renewal,
            created_at=sub.created_at
        ))
    
    # Sort by end_date (most recent first)
    results.sort(key=lambda x: x.end_date, reverse=True)
    
    return {
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "data": results
    }

# --- Automation & Analytics ---

@router.get("/notifications/expiry", response_model=List[Any])
async def get_expiring_subscriptions(
    days: int = 7,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get list of subscriptions expiring in the next N days.
    Useful for auto-renewal notifications.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    now = datetime.now(timezone.utc)
    target_date = now + timedelta(days=days)
    
    # Mongo query to find active subs ending between now and target_date
    subs = await DeveloperSubscription.find({
        "status": SubscriptionStatus.ACTIVE,
        "end_date": {"$gt": now, "$lte": target_date}
    }).to_list()
    
    # Hydrate with developer details
    results = []
    for sub in subs:
        dev_user = await User.find_one({"developer_id": sub.developer_id})
        plan = await SubscriptionPlan.get(sub.plan_id)
        results.append({
            "subscription_id": sub.id,
            "developer_name": dev_user.full_name if dev_user else "Unknown",
            "developer_email": dev_user.email if dev_user else "Unknown",
            "plan_name": plan.name if plan else "Unknown",
            "end_date": sub.end_date,
            "days_left": (sub.end_date.replace(tzinfo=timezone.utc) - now).days
        })
        
    return results

@router.get("/analytics/revenue", response_model=Dict[str, Any])
async def get_subscription_revenue(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Calculate total revenue and churn metrics.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    all_subs = await DeveloperSubscription.find_all().to_list()
    
    # Prefetch active plans for price
    plans = await SubscriptionPlan.find_all().to_list()
    plan_price_map = {p.id: p.price for p in plans}
    
    total_revenue = 0.0
    active_count = 0
    expired_count = 0
    cancelled_count = 0
    
    for sub in all_subs:
        price = plan_price_map.get(sub.plan_id, 0.0)
        # Assuming paid if status is ACTIVE/EXPIRED (simplification)
        if sub.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.EXPIRED]:
             total_revenue += price
             
        if sub.status == SubscriptionStatus.ACTIVE:
            active_count += 1
        elif sub.status == SubscriptionStatus.EXPIRED:
            expired_count += 1
        elif sub.status == SubscriptionStatus.CANCELLED:
            cancelled_count += 1
            
    return {
        "total_revenue": total_revenue,
        "active_subscriptions": active_count,
        "expired_subscriptions": expired_count,
        "cancelled_subscriptions": cancelled_count,
        "churn_rate": (cancelled_count / (active_count + cancelled_count)) * 100 if (active_count + cancelled_count) > 0 else 0
    }

# --- New Enhanced Admin APIs ---

@router.get("/stats", response_model=SubscriptionStatsResponse)
async def get_subscription_stats(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get comprehensive subscription statistics:
    - Total Active subscriptions
    - Expiring Soon (within 7 days)
    - Expired subscriptions
    - Monthly Revenue
    - Total Revenue
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    now = datetime.now(timezone.utc)
    seven_days_later = now + timedelta(days=7)
    
    # Get all subscriptions
    all_subs = await DeveloperSubscription.find_all().to_list()
    
    # Get all plans to calculate revenue
    plans = await SubscriptionPlan.find_all().to_list()
    plan_price_map = {p.id: p.price for p in plans}
    
    # Calculate stats
    total_active = 0
    expiring_soon = 0
    expired = 0
    total_revenue = 0.0
    monthly_revenue = 0.0
    
    # Get start of current month
    current_month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    
    for sub in all_subs:
        price = plan_price_map.get(sub.plan_id, 0.0)
        
        # Count active subscriptions
        if sub.status == SubscriptionStatus.ACTIVE:
            total_active += 1
            total_revenue += price
            
            # Check if expiring soon (within 7 days)
            end_date_aware = sub.end_date.replace(tzinfo=timezone.utc) if sub.end_date.tzinfo is None else sub.end_date
            if end_date_aware <= seven_days_later:
                expiring_soon += 1
        
        # Count expired subscriptions
        elif sub.status == SubscriptionStatus.EXPIRED:
            expired += 1
            total_revenue += price
        
        # Calculate monthly revenue (subscriptions started this month)
        start_date_aware = sub.start_date.replace(tzinfo=timezone.utc) if sub.start_date.tzinfo is None else sub.start_date
        if start_date_aware >= current_month_start and sub.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.EXPIRED]:
            monthly_revenue += price
    
    return SubscriptionStatsResponse(
        total_active=total_active,
        expiring_soon=expiring_soon,
        expired=expired,
        monthly_revenue=monthly_revenue,
        total_revenue=total_revenue,
        total_subscriptions=len(all_subs)
    )
