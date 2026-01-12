from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User, UserRole
from app.models.webhook import WebhookSubscription
from app.schemas.webhook import WebhookCreate, WebhookResponse
from app.utils.cache_invalidation import invalidate_webhook_cache

router = APIRouter()

@router.post("/", response_model=WebhookResponse)
async def create_webhook(
    webhook_in: WebhookCreate,
    current_user: User = Depends(deps.get_current_user), # Any user can be a developer logically? 
    # For now assuming current_user corresponds to developer.
    # We really need a User -> Developer mapping. 
    # For this task, we will verify if User has DEVELOPER role, but we need the Developer ID.
    # Hack: We will assume the user ID *IS* the developer ID or we look it up.
    # Given previous tasks, we didn't firmly link User->Developer.
    # Let's require the user to have DEVELOPER role.
) -> Any:
    """
    Register a webhook.
    """
    if current_user.role not in [UserRole.DEVELOPER, UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")

    # TODO: In a real app, look up the Developer profile associated with this User.
    # For this demo, we'll store the User ID as the Developer ID or passed in?
    # Actually, developer_projects.py assumed we filter by developer_id but usually implicit.
    # Let's use current_user.id as the developer_id key for subscriptions, 
    # implying the User *IS* the Developer entity owner.
    
    webhook = WebhookSubscription(
        developer_id=current_user.id,
        url=str(webhook_in.url),
        events=webhook_in.events,
        secret_token=webhook_in.secret_token
    )
    await webhook.insert()

    # Invalidate webhook cache
    await invalidate_webhook_cache(current_user.id)

    return webhook

@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    List my webhooks.
    """
    webhooks = await WebhookSubscription.find(WebhookSubscription.developer_id == current_user.id).to_list()
    return webhooks

@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    webhook = await WebhookSubscription.get(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    if webhook.developer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your webhook")
    
    await webhook.delete()

    # Invalidate webhook cache
    await invalidate_webhook_cache(current_user.id)

    return {"message": "Deleted"}
