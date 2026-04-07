from datetime import datetime
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, Field

class LawyerResponse(BaseModel):
    id: UUID
    name: str
    specialization: str
    experience: str
    rating: float
    review_count: int
    image_url: Optional[str]
    fee: float

class LawyerEnvelope(BaseModel):
    status: str = "success"
    data: LawyerResponse

class TimeSlot(BaseModel):
    time: str
    available: bool

class DateAvailability(BaseModel):
    date: str
    slots: List[TimeSlot]

class AvailabilityEnvelope(BaseModel):
    status: str = "success"
    data: List[DateAvailability]

class ConsultationCreate(BaseModel):
    lawyer_id: UUID
    project_id: UUID
    date: str
    time: str
    mode: str

class BookingConfirmation(BaseModel):
    booking_id: str
    payment_portal_url: str
    amount: float

class BookingEnvelope(BaseModel):
    status: str = "success"
    data: BookingConfirmation

class ConsultationHistoryItem(BaseModel):
    id: str
    lawyer_name: str
    date: str
    time: str
    mode: str
    status: str

class HistoryEnvelope(BaseModel):
    status: str = "success"
    data: List[ConsultationHistoryItem]
