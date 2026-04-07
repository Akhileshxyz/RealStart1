from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List, Dict, Any
from enum import Enum
from beanie import Document
from pydantic import Field

class EventType(str, Enum):
    HEARING = "HEARING"
    MEETING = "MEETING"
    CALL = "CALL"
    DEADLINE = "DEADLINE"
    TASK = "TASK"
    CONSULTATION = "CONSULTATION"
    OTHER = "OTHER"

class LawyerLeadStatus(str, Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    CONVERTED = "CONVERTED"
    LOST = "LOST"
    COMPLETED = "COMPLETED"

class LawyerPaymentStatus(str, Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"
    REFUNDED = "REFUNDED"

class LawyerProfile(Document):
    id: UUID = Field(default_factory=uuid4)
    user_id: Optional[UUID] = None # Linked registered user id
    
    # Profile Info
    name: str = "Advocate"
    bar_council_id: Optional[str] = None
    specialization: List[str] = []
    experience_years: int = 0
    cities: List[str] = []
    office_address: Optional[str] = None
    bio: Optional[str] = None
    
    # Availability/Consultation Settings
    fee: float = 999.0
    working_days: List[Dict[str, Any]] = []
    working_hours: Dict[str, str] = {}
    
    # Public Metrics
    rating: float = 4.5
    review_count: int = 0
    image_url: Optional[str] = None
    
    # Preferences & Metadata
    notification_preferences: Dict[str, bool] = {}
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "lawyers"

class LawyerLead(Document):
    id: UUID = Field(default_factory=uuid4)
    lawyer_id: UUID
    user_id: UUID
    project_id: Optional[UUID] = None
    client_name: str
    client_phone: str
    client_email: Optional[str] = None
    status: LawyerLeadStatus = LawyerLeadStatus.NEW
    payment_status: LawyerPaymentStatus = LawyerPaymentStatus.UNPAID
    service_type: Optional[str] = None
    service_fee: Optional[float] = 0.0
    priority: str = "MEDIUM"
    project_name: Optional[str] = None
    client_city: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "lawyer_leads"

class LawyerSubscription(Document):
    id: UUID = Field(default_factory=uuid4)
    lawyer_id: UUID
    plan_id: str
    status: str = "active"
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "lawyer_subscriptions"

class LawyerEvent(Document):
    id: UUID = Field(default_factory=uuid4)
    lawyer_id: UUID
    title: str
    description: Optional[str] = None
    event_type: EventType = EventType.OTHER
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    client_name: Optional[str] = None
    client_id: Optional[UUID] = None
    is_completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "lawyer_events"
