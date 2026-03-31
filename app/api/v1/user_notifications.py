import math
from typing import Optional, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel

from app.api import deps
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import PaginatedNotificationResponse, NotificationResponse
from app.core.redis_client import redis_client

router = APIRouter()

class MarkReadRequest(BaseModel):
    is_read: bool = True

@router.get("/users/me/notifications", response_model=PaginatedNotificationResponse)
async def get_my_notifications(
    current_user: User = Depends(deps.get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    unread_only: bool = Query(False, description="Filter only unread notifications")
) -> Any:
    """
    Get paginated notifications for the authenticated user.
    """
    skip = (page - 1) * size
    
    # Build query
    query = {"user_id": current_user.id}
    if unread_only:
        query["is_read"] = False
        
    # Get total count
    total = await Notification.find(query).count()
    
    # Calculate total pages
    pages = math.ceil(total / size) if total > 0 else 0
    
    # Fetch paginated items, ordered by newest first
    items = await Notification.find(query).sort(-Notification.created_at).skip(skip).limit(size).to_list()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }

@router.patch("/users/me/notifications/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: str,
    update_data: MarkReadRequest,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Mark a notification as read or unread.
    """
    notification = await Notification.get(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
        
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this notification"
        )
        
    notification.is_read = update_data.is_read
    await notification.save()
    
    return notification

@router.post("/users/me/notifications/mark-all-read")
async def mark_all_read(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Mark all notifications as read for the current user.
    """
    await Notification.find({"user_id": current_user.id, "is_read": False}).update({"$set": {"is_read": True}})
    
    return {"message": "All notifications marked as read"}
