from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.models.lead import LeadStatus

class LeadUpdate(BaseModel):
    status: Optional[LeadStatus] = None
    developer_notes: Optional[str] = None

class LeadResponse(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    status: LeadStatus
    last_viewed_at: datetime
    view_count: int
    
    # Augmented Data
    user_full_name: Optional[str] = None
    user_email: Optional[str] = None
    user_phone: Optional[str] = None
    
    developer_notes: Optional[str] = None

    class Config:
        from_attributes = True
