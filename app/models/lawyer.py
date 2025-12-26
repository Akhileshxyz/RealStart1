from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from typing import List, Optional, Dict, Any
from beanie import Document
from pydantic import Field

class LawyerLeadStatus(str, Enum):
    NEW = "NEW"
    FOLLOW_UP = "FOLLOW_UP"
    SOLVED = "SOLVED"

class LawyerPaymentStatus(str, Enum):
    PAID = "PAID"
    UNPAID = "UNPAID"
    REFUNDED = "REFUNDED"

class LawyerProfile(Document):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    bio: Optional[str] = None
    specialization: List[str] = Field(default_factory=list)
    bar_council_id: Optional[str] = None
    experience_years: int = 0
    profile_picture_url: Optional[str] = None
    
    is_online: bool = False
    
    rating: float = 0.0
    review_count: int = 0
    
    cities: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "lawyer_profiles"

class LawyerLead(Document):
    id: UUID = Field(default_factory=uuid4)
    lawyer_id: UUID
    client_name: str
    client_phone: str
    property_id: Optional[UUID] = None
    inquiry_date: datetime = Field(default_factory=datetime.utcnow)
    
    status: LawyerLeadStatus = LawyerLeadStatus.NEW
    payment_status: LawyerPaymentStatus = LawyerPaymentStatus.UNPAID
    
    notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "lawyer_leads"

class LawyerSubscriptionPlan(str, Enum):
    BASIC = "BASIC"
    PRO = "PRO"
    PREMIUM = "PREMIUM"

class LawyerSubscription(Document):
    id: UUID = Field(default_factory=uuid4)
    lawyer_id: UUID
    plan_name: LawyerSubscriptionPlan = LawyerSubscriptionPlan.BASIC
    
    start_date: datetime
    end_date: datetime
    
    is_active: bool = True
    
    # Simple permissions dict, e.g., {"can_verify_docs": True, "lead_limit": 10}
    features: Dict[str, Any] = {}
    
    payment_details: Optional[Dict[str, Any]] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "lawyer_subscriptions"
