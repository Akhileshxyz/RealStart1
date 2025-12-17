from datetime import datetime, timedelta
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.models.user import User, UserRole
from app.models.subscription import SubscriptionPlan, DeveloperSubscription, SubscriptionStatus
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse, SubscriptionPlanResponse

router = APIRouter()

@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def list_available_plans(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    List available subscription plans for purchase.
    """
    plans = await SubscriptionPlan.find(SubscriptionPlan.is_active == True).to_list()
    return plans

@router.get("/current", response_model=Optional[SubscriptionResponse])
async def get_current_subscription(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current active subscription.
    """
    if current_user.role != UserRole.DEVELOPER:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # Find latest active or pending subscription
    sub = await DeveloperSubscription.find_one(
        DeveloperSubscription.developer_id == current_user.id,
        DeveloperSubscription.status == SubscriptionStatus.ACTIVE
    ).sort("-end_date")
    
    if not sub:
        return None
        
    plan = await SubscriptionPlan.get(sub.plan_id)
    return SubscriptionResponse(
        id=sub.id,
        developer_id=sub.developer_id,
        plan_id=sub.plan_id,
        start_date=sub.start_date,
        end_date=sub.end_date,
        status=sub.status,
        plan_name=plan.name if plan else "Unknown"
    )

@router.post("/purchase", response_model=SubscriptionResponse)
async def purchase_subscription(
    purchase_in: SubscriptionCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Purchase a subscription plan.
    (Mock implementation: auto-approves)
    """
    if current_user.role != UserRole.DEVELOPER:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    plan = await SubscriptionPlan.get(purchase_in.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
        
    # Create subscription
    # In real app: Validate payment via payment_method_id
    
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=plan.duration_days)
    
    # Deactivate existing? Or Queue?
    # Simple: Overwrite/Extend.
    # Logic: Set previous active to CANCELLED/EXPIRED if exist?
    existing = await DeveloperSubscription.find(
        DeveloperSubscription.developer_id == current_user.id,
        DeveloperSubscription.status == SubscriptionStatus.ACTIVE
    ).to_list()
    for ex in existing:
        ex.status = SubscriptionStatus.CANCELLED
        await ex.save()
    
    new_sub = DeveloperSubscription(
        developer_id=current_user.id,
        plan_id=plan.id,
        start_date=start_date,
        end_date=end_date,
        status=SubscriptionStatus.ACTIVE,
        payment_details={"method": "mock", "id": purchase_in.payment_method_id}
    )
    await new_sub.insert()
    
    return SubscriptionResponse(
        id=new_sub.id,
        developer_id=new_sub.developer_id,
        plan_id=new_sub.plan_id,
        start_date=new_sub.start_date,
        end_date=new_sub.end_date,
        status=new_sub.status,
        plan_name=plan.name
    )
