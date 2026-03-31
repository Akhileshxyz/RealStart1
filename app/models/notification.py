from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from enum import Enum
from beanie import Document
from pydantic import Field


class NotificationType(str, Enum):
    SYSTEM = "SYSTEM"           # General platform announcements
    PROPERTY = "PROPERTY"       # Property/project updates (e.g. price change, new listing)
    VISIT = "VISIT"             # Visit booking confirmations, reminders
    WISHLIST = "WISHLIST"       # Price drop on wishlisted property
    LEGAL = "LEGAL"             # Legal request updates
    ACCOUNT = "ACCOUNT"         # Account-related (password change, email update, etc.)
    PROMO = "PROMO"             # Promotional offers


class Notification(Document):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID                          # Target user
    title: str
    body: str
    type: NotificationType = NotificationType.SYSTEM
    is_read: bool = False
    action_url: Optional[str] = None       # Deep link / URL for the notification action
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "notifications"
