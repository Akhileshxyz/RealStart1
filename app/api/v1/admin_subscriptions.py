from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User, UserRole
from app.models.subscription import SubscriptionPlan, DeveloperSubscription
from app.schemas.subscription import SubscriptionPlanCreate, SubscriptionPlanResponse, SubscriptionResponse

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
