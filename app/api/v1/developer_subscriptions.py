from datetime import datetime, timedelta
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.models.user import User, UserRole
from app.models.subscription import SubscriptionPlan, DeveloperSubscription, SubscriptionStatus
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse, SubscriptionPlanResponse, SubscriptionOrderResponse, SubscriptionVerifyRequest
from app.core.config import settings
import razorpay

router = APIRouter()

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

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

@router.post("/orders", response_model=SubscriptionOrderResponse)
async def create_subscription_order(
    purchase_in: SubscriptionCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create a Razorpay Order for subscription.
    """
    if current_user.role != UserRole.DEVELOPER:
        raise HTTPException(status_code=403, detail="Not authorized")

    plan = await SubscriptionPlan.get(purchase_in.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    amount_in_paise = int(plan.price * 100)
    currency = "INR"

    try:
        # Create Razorpay Order
        order_data = {
            "amount": amount_in_paise,
            "currency": currency,
            "receipt": f"sub_{current_user.id}_{datetime.utcnow().timestamp()}",
            "notes": {
                "developer_id": str(current_user.id),
                "plan_id": str(plan.id)
            }
        }
        order = razorpay_client.order.create(data=order_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Razorpay Error: {str(e)}")

    # Create Pending Subscription
    # We don't set start/end date yet, only on verification
    sub = DeveloperSubscription(
        developer_id=current_user.id,
        plan_id=plan.id,
        start_date=datetime.utcnow(), # Placeholder
        end_date=datetime.utcnow(),   # Placeholder
        status=SubscriptionStatus.PENDING,
        razorpay_order_id=order['id']
    )
    await sub.insert()

    return SubscriptionOrderResponse(
        order_id=order['id'],
        amount=plan.price,
        currency=currency,
        key_id=settings.RAZORPAY_KEY_ID
    )

@router.post("/verify", response_model=SubscriptionResponse)
async def verify_payment(
    verify_in: SubscriptionVerifyRequest,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Verify payment signature and activate subscription.
    """
    if current_user.role != UserRole.DEVELOPER:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Verify Signature
    try:
        params_dict = {
            'razorpay_order_id': verify_in.razorpay_order_id,
            'razorpay_payment_id': verify_in.razorpay_payment_id,
            'razorpay_signature': verify_in.razorpay_signature
        }
        razorpay_client.utility.verify_payment_signature(params_dict)
    except razorpay.errors.SignatureVerificationError:
         raise HTTPException(status_code=400, detail="Payment verification failed")
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Verification Error: {str(e)}")

    # Find pending subscription
    sub = await DeveloperSubscription.find_one(
        DeveloperSubscription.razorpay_order_id == verify_in.razorpay_order_id
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription order not found")

    if sub.status == SubscriptionStatus.ACTIVE:
         # Already active (idempotency check)
         pass # Just return it
    else:
        # Activate
        plan = await SubscriptionPlan.get(sub.plan_id)
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=plan.duration_days)

        # Deactivate previous active subscriptions
        existing = await DeveloperSubscription.find(
            DeveloperSubscription.developer_id == sub.developer_id,
            DeveloperSubscription.status == SubscriptionStatus.ACTIVE
        ).to_list()
        for ex in existing:
            ex.status = SubscriptionStatus.CANCELLED
            await ex.save()
        
        sub.start_date = start_date
        sub.end_date = end_date
        sub.status = SubscriptionStatus.ACTIVE
        sub.razorpay_payment_id = verify_in.razorpay_payment_id
        sub.razorpay_signature = verify_in.razorpay_signature
        sub.updated_at = datetime.utcnow()
        await sub.save()

    plan = await SubscriptionPlan.get(sub.plan_id)
    return SubscriptionResponse(
        id=sub.id,
        developer_id=sub.developer_id,
        plan_id=sub.plan_id,
        start_date=sub.start_date,
        end_date=sub.end_date,
        status=sub.status,
        plan_name=plan.name
    )
