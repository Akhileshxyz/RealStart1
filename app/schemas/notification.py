from datetime import datetime
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel
from app.models.notification import NotificationType

class NotificationResponse(BaseModel):
    id: UUID
    title: str
    body: str
    type: NotificationType
    is_read: bool
    action_url: Optional[str]
    created_at: datetime
    
class PaginatedNotificationResponse(BaseModel):
    items: List[NotificationResponse]
    total: int
    page: int
    size: int
    pages: int
