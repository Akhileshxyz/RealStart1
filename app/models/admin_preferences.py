from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from beanie import Document
from pydantic import Field

class AdminNotificationPreferences(Document):
    """Admin notification preferences"""
    id: UUID = Field(default_factory=uuid4)
    admin_id: UUID  # Links to User.id
    
    # Notification settings
    email_notifications: bool = True
    subscription_reminders: bool = True
    new_developer_alerts: bool = True
    payment_alerts: bool = True
    system_updates: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "admin_notification_preferences"
