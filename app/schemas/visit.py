from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class TimeSlot(BaseModel):
    time: str
    available: bool

class DateAvailability(BaseModel):
    date: str
    slots: List[TimeSlot]

class ProjectMiniDetail(BaseModel):
    id: UUID
    title: str
    location_name: str
    price_display: str
    hero_image: Optional[str] = None

class ProjectAvailabilityResponse(BaseModel):
    project_id: UUID
    project: ProjectMiniDetail
    timezone: str = "Asia/Kolkata"
    availability: List[DateAvailability]
    visit_types: List[str] = ["virtual", "in_person"]
    cab_available: bool = True

class VisitBookingRequest(BaseModel):
    project_id: UUID
    date: str = Field(..., example="2026-04-10")
    time: str = Field(..., example="10:00")
    visit_type: str = Field(..., example="in_person")
    cab_required: bool = False
    name: str
    mobile: str

# Schemas for existing user_portal.py logic
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
    status: str
    created_at: datetime

class VisitListItem(BaseModel):
    project: ProjectMiniDetail
    visit_date: str
    visit_time: str
    visit_type: str
    cab_required: bool
    status: str
    booked_at: datetime
