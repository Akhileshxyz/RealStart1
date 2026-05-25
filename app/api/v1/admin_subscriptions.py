from typing import Any, List, Dict, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from app.api import deps
from app.models.user import User, UserRole
from app.models.developer import Developer
from app.models.project import Project, ProjectStatus
from app.models.subscription import SubscriptionPlan, DeveloperSubscription, SubscriptionStatus
from app.schemas.subscription import (
    SubscriptionPlanCreate, 
    SubscriptionPlanResponse, 
    SubscriptionResponse,
    SubscriptionStatsResponse,
    DetailedSubscriptionResponse,
    ProjectUsageResponse
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

@router.put("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def update_plan(
    plan_id: str,
    plan_update: SubscriptionPlanCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update an existing subscription plan.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Find the plan
    from uuid import UUID
    try:
        plan_uuid = UUID(plan_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid plan ID format")
    
    plan = await SubscriptionPlan.get(plan_uuid)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Update plan fields
    plan.name = plan_update.name
    plan.duration_days = plan_update.duration_days
    plan.price = plan_update.price
    plan.features = plan_update.features
    plan.is_active = plan_update.is_active
    
    await plan.save()
    return plan

@router.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Permanently delete a subscription plan (if no active subscriptions use it).
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Find the plan
    from uuid import UUID
    try:
        plan_uuid = UUID(plan_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid plan ID format")
    
    plan = await SubscriptionPlan.get(plan_uuid)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Check if any active subscriptions are using this plan
    active_subs_count = await DeveloperSubscription.find({
        "plan_id": plan_uuid,
        "status": SubscriptionStatus.ACTIVE
    }).count()
    
    if active_subs_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete plan. {active_subs_count} active subscription(s) are using this plan."
        )
    
    # Hard delete the plan
    await plan.delete()
    
    return {"message": "Plan permanently deleted", "plan_id": str(plan_id)}

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
    from app.services.subscription_service import SubscriptionService
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

        projects_used = 0
        projects_limit = 0
        if user:
            limits = await SubscriptionService.get_current_limits(user.id)
            projects_limit = limits.get("max_projects", 1)
            projects_used = await Project.find(
                Project.developer_id == user.id,
                Project.status != ProjectStatus.DELETED,
                Project.status != ProjectStatus.REJECTED
            ).count()
        
        results.append(DetailedSubscriptionResponse(
            id=sub.id,
            developer_id=user.developer_id if user else None,
            developer_name=developer.name if developer else "Unknown Developer",
            developer_email=user.email if user else None,
            plan_name=plan.name if plan else "Unknown Plan",
            plan_price=plan.price if plan else 0.0,
            start_date=sub.start_date,
            end_date=sub.end_date,
            days_left=max(0, days_left) if sub.status == SubscriptionStatus.ACTIVE else 0,
            status=sub.status,
            auto_renewal=sub.auto_renewal,
            created_at=sub.created_at,
            projects_used=projects_used,
            projects_limit=projects_limit,
        ))
    
    # Sort by end_date (most recent first)
    results.sort(key=lambda x: x.end_date, reverse=True)
    
    return {
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "data": results
    }

@router.get("/by-developer/{developer_id}", response_model=Optional[DetailedSubscriptionResponse])
async def get_developer_subscription(
    developer_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get the active subscription for a developer by developer UUID.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = await User.find_one(User.developer_id == developer_id)
    if not user:
        return None

    sub = await DeveloperSubscription.find_one(
        DeveloperSubscription.developer_id == user.id,
        DeveloperSubscription.status == SubscriptionStatus.ACTIVE,
    )
    if not sub:
        return None

    developer = await Developer.get(developer_id)
    plan = await SubscriptionPlan.get(sub.plan_id)

    now = datetime.now(timezone.utc)
    end_date_aware = sub.end_date.replace(tzinfo=timezone.utc) if sub.end_date.tzinfo is None else sub.end_date
    days_left = (end_date_aware - now).days

    from app.services.subscription_service import SubscriptionService
    limits = await SubscriptionService.get_current_limits(user.id)
    projects_limit = limits.get("max_projects", 1)
    projects_used = await Project.find(
        Project.developer_id == user.id,
        Project.status != ProjectStatus.DELETED,
        Project.status != ProjectStatus.REJECTED
    ).count()

    return DetailedSubscriptionResponse(
        id=sub.id,
        developer_id=developer_id,
        developer_name=developer.name if developer else "Unknown",
        developer_email=user.email if user else None,
        plan_name=plan.name if plan else "Unknown Plan",
        plan_price=plan.price if plan else 0.0,
        start_date=sub.start_date,
        end_date=sub.end_date,
        days_left=max(0, days_left),
        status=sub.status,
        auto_renewal=sub.auto_renewal,
        created_at=sub.created_at,
        projects_used=projects_used,
        projects_limit=projects_limit,
    )


@router.put("/change-plan", response_model=SubscriptionResponse)
async def change_subscription_plan(
    developer_id: UUID = Body(...),
    new_plan_id: UUID = Body(...),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Admin: Change/upgrade a developer's subscription plan by developer UUID.
    Finds the User linked to this Developer, then creates or updates the subscription.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Find the User linked to this Developer, or create one
    developer = await Developer.get(developer_id)
    if not developer:
        raise HTTPException(status_code=404, detail="Developer not found")

    user = await User.find_one(User.developer_id == developer_id)
    if not user:
        user = User(
            email=developer.contact_email or f"{developer_id}@placeholder.dev",
            hashed_password="",
            full_name=developer.name or "Developer",
            role=UserRole.DEVELOPER,
            developer_id=developer_id,
            is_active=True,
        )
        await user.insert()

    plan = await SubscriptionPlan.get(new_plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if not plan.is_active:
        raise HTTPException(status_code=400, detail="Selected plan is not active")

    now = datetime.now(timezone.utc)
    end_date = now + timedelta(days=plan.duration_days)

    # Find existing active subscription or create new one
    sub = await DeveloperSubscription.find_one(
        DeveloperSubscription.developer_id == user.id,
        DeveloperSubscription.status == SubscriptionStatus.ACTIVE,
    )

    if sub:
        sub.plan_id = new_plan_id
        sub.start_date = now
        sub.end_date = end_date
        sub.updated_at = now
    else:
        sub = DeveloperSubscription(
            developer_id=user.id,
            plan_id=new_plan_id,
            start_date=now,
            end_date=end_date,
            status=SubscriptionStatus.ACTIVE,
        )

    await sub.save()

    resp = SubscriptionResponse.model_validate(sub)
    resp.plan_name = plan.name
    return resp


# --- Enhanced Admin APIs ---

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

@router.get("/project-usage/{developer_id}", response_model=ProjectUsageResponse)
async def get_developer_project_usage(
    developer_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get project usage stats for a developer by developer UUID.
    Returns projects_used, projects_limit, and whether they can create more.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")

    developer = await Developer.get(developer_id)
    if not developer:
        raise HTTPException(status_code=404, detail="Developer not found")

    user = await User.find_one(User.developer_id == developer_id)
    if not user:
        return ProjectUsageResponse(
            developer_id=developer_id,
            developer_name=developer.name or "Unknown",
            projects_used=0,
            projects_limit=0,
            plan_name="No Plan",
            can_create_more=False
        )

    from app.services.subscription_service import SubscriptionService
    limits = await SubscriptionService.get_current_limits(user.id)
    projects_limit = limits.get("max_projects", 1)
    projects_used = await Project.find(
        Project.developer_id == user.id,
        Project.status != ProjectStatus.DELETED,
        Project.status != ProjectStatus.REJECTED
    ).count()

    sub = await SubscriptionService.get_active_subscription(user.id)
    plan_name = "Free Tier"
    plan = await SubscriptionPlan.get(sub.plan_id) if sub else None
    if plan:
        plan_name = plan.name

    return ProjectUsageResponse(
        developer_id=developer_id,
        developer_name=developer.name or "Unknown",
        projects_used=projects_used,
        projects_limit=projects_limit,
        plan_name=plan_name,
        can_create_more=projects_used < projects_limit
    )


@router.post("/send-renewal-reminders")
async def send_renewal_reminders(
    days_threshold: int = Query(7, ge=1, le=30, description="Send reminders for subscriptions expiring within N days"),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Send renewal reminder emails to developers whose subscriptions are expiring soon.
    
    Args:
        days_threshold: Number of days before expiry to send reminders (default: 7, max: 30)
    
    Returns:
        Summary of sent reminders including success/failure counts
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    from app.services.email_service import email_service
    
    now = datetime.now(timezone.utc)
    threshold_date = now + timedelta(days=days_threshold)
    
    # Find active subscriptions expiring within the threshold
    expiring_subs = await DeveloperSubscription.find({
        "status": SubscriptionStatus.ACTIVE,
        "end_date": {"$gt": now, "$lte": threshold_date}
    }).to_list()
    
    if not expiring_subs:
        return {
            "message": "No subscriptions found expiring within the specified period",
            "days_threshold": days_threshold,
            "total_found": 0,
            "emails_sent": 0,
            "emails_failed": 0,
            "reminders": []
        }
    
    # Get all plans for pricing info
    plans = await SubscriptionPlan.find_all().to_list()
    plan_map = {p.id: p for p in plans}
    
    sent_count = 0
    failed_count = 0
    reminders = []
    
    for sub in expiring_subs:
        try:
            # Get developer and user info
            developer = await Developer.get(sub.developer_id)
            user = await User.find_one({"developer_id": sub.developer_id})
            plan = plan_map.get(sub.plan_id)
            
            if not user or not user.email:
                failed_count += 1
                reminders.append({
                    "developer_id": str(sub.developer_id),
                    "developer_name": developer.name if developer else "Unknown",
                    "status": "failed",
                    "reason": "No email address found"
                })
                continue
            
            if not plan:
                failed_count += 1
                reminders.append({
                    "developer_id": str(sub.developer_id),
                    "developer_name": developer.name if developer else "Unknown",
                    "status": "failed",
                    "reason": "Plan not found"
                })
                continue
            
            # Calculate days left
            end_date_aware = sub.end_date.replace(tzinfo=timezone.utc) if sub.end_date.tzinfo is None else sub.end_date
            days_left = (end_date_aware - now).days
            
            # Get email template
            html_content, text_content = email_service.get_renewal_reminder_template(
                developer_name=developer.name if developer else user.full_name,
                plan_name=plan.name,
                end_date=sub.end_date.strftime("%B %d, %Y"),
                days_left=days_left,
                plan_price=plan.price
            )
            
            # Send email
            success = await email_service.send_email(
                to_email=user.email,
                subject=f"Subscription Renewal Reminder - {days_left} Days Left",
                html_content=html_content,
                text_content=text_content
            )
            
            if success:
                sent_count += 1
                reminders.append({
                    "developer_id": str(sub.developer_id),
                    "developer_name": developer.name if developer else user.full_name,
                    "email": user.email,
                    "plan_name": plan.name,
                    "days_left": days_left,
                    "end_date": sub.end_date.isoformat(),
                    "status": "sent"
                })
            else:
                failed_count += 1
                reminders.append({
                    "developer_id": str(sub.developer_id),
                    "developer_name": developer.name if developer else user.full_name,
                    "email": user.email,
                    "status": "failed",
                    "reason": "Email sending failed"
                })
                
        except Exception as e:
            failed_count += 1
            reminders.append({
                "developer_id": str(sub.developer_id),
                "status": "failed",
                "reason": str(e)
            })
    
    return {
        "message": f"Renewal reminders processed for subscriptions expiring within {days_threshold} days",
        "days_threshold": days_threshold,
        "total_found": len(expiring_subs),
        "emails_sent": sent_count,
        "emails_failed": failed_count,
        "reminders": reminders
    }
