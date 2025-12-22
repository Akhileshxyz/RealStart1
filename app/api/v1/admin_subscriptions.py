from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User, UserRole
from app.models.subscription import SubscriptionPlan, DeveloperSubscription, SubscriptionStatus
from app.schemas.subscription import SubscriptionPlanCreate, SubscriptionPlanResponse, SubscriptionResponse
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

@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def list_developer_subscriptions(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    View all developer subscriptions.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    subs = await DeveloperSubscription.find_all().to_list()
    
    response = []
    for sub in subs:
        plan = await SubscriptionPlan.get(sub.plan_id)
        resp = SubscriptionResponse(
            id=sub.id,
            developer_id=sub.developer_id,
            plan_id=sub.plan_id,
            start_date=sub.start_date,
            end_date=sub.end_date,
            status=sub.status,
            plan_name=plan.name if plan else "Unknown"
        )
        response.append(resp)
        
    return response

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
