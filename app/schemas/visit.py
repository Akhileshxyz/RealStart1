from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.models.visit import VisitStatus

class VisitBookingCreate(BaseModel):
    project_id: UUID
    scheduled_time: datetime
    pickup_location: Optional[str] = None
    visitor_name: Optional[str] = None
    visitor_phone: Optional[str] = None

class VisitBookingResponse(BaseModel):
    id: UUID
    user_id: UUID
    project_id: UUID
    scheduled_time: datetime
    pickup_location: Optional[str] = None
    visitor_name: str
    visitor_phone: str
    status: VisitStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
