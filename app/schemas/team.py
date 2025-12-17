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
