from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from enum import Enum
from beanie import Document
from pydantic import Field

class ConsultationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class LawyerConsultation(Document):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    lawyer_id: UUID
    project_id: UUID
    date: str             # YYYY-MM-DD
    time: str             # "10:30 AM"
    mode: str             # "audio", "video"
    status: ConsultationStatus = ConsultationStatus.PENDING
    
    amount: float = 999.0
    payment_id: Optional[str] = None
    meeting_link: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "lawyer_consultations"
