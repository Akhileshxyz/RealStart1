from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from datetime import datetime

class TeamMemberInvite(BaseModel):
    email: EmailStr
    role: str
    permissions: List[str] = []

class TeamMemberUpdate(BaseModel):
    role: Optional[str] = None
    permissions: Optional[List[str]] = None

class TeamMemberResponse(BaseModel):
    id: UUID
    developer_id: UUID
    user_id: UUID
    role: str
    permissions: List[str]
    invited_at: datetime
    is_active: bool
    
    # Augmented User Info
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    
    class Config:
        from_attributes = True

class StaffTaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "MEDIUM" # LOW, MEDIUM, HIGH, URGENT
    due_date: Optional[datetime] = None
    related_client_id: Optional[UUID] = None

class StaffTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None # PENDING, IN_PROGRESS, COMPLETED
    priority: Optional[str] = None
    due_date: Optional[datetime] = None

class StaffTaskResponse(BaseModel):
    id: UUID
    assigned_to: UUID
    assigned_by: UUID
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    due_date: Optional[datetime] = None
    related_client_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
