from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from enum import Enum
from beanie import Document
from pydantic import Field

class VisitStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class VisitBooking(Document):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    project_id: UUID
    scheduled_time: datetime
    pickup_location: Optional[str] = None
    visitor_name: str
    visitor_phone: str
    status: VisitStatus = VisitStatus.SCHEDULED
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "visit_bookings"
