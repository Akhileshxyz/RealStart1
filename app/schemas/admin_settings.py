from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from datetime import datetime

# Profile Update Schemas
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        
# Notification Preferences
class NotificationPreferences(BaseModel):
    email_notifications: bool = True
    subscription_reminders: bool = True
    new_developer_alerts: bool = True
    payment_alerts: bool = True
    system_updates: bool = True
    
    class Config:
        from_attributes = True

class NotificationPreferencesUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    subscription_reminders: Optional[bool] = None
    new_developer_alerts: Optional[bool] = None
    payment_alerts: Optional[bool] = None
    system_updates: Optional[bool] = None

# User Settings Response
class UserSettingsResponse(BaseModel):
    profile: UserProfileResponse
    notifications: NotificationPreferences
    
    class Config:
        from_attributes = True
