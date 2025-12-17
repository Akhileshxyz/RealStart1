from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Dict, Any
from enum import Enum
from beanie import Document
from pydantic import Field

class SubscriptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"

class SubscriptionPlan(Document):
    id: UUID = Field(default_factory=uuid4)
    name: str # "Quarterly", "Annual"
    duration_days: int
    price: float
    features: Dict[str, Any] = {} # e.g. {"max_projects": 5, "team_access": True}
    is_active: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "subscription_plans"

class DeveloperSubscription(Document):
    id: UUID = Field(default_factory=uuid4)
    developer_id: UUID
    plan_id: UUID
    
    start_date: datetime
    end_date: datetime
    
    status: SubscriptionStatus = SubscriptionStatus.PENDING
    payment_details: Optional[Dict[str, Any]] = None # Transaction ID etc.
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "developer_subscriptions"
