from datetime import datetime
from uuid import UUID
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.models.subscription import SubscriptionStatus

# Plan Schemas
class SubscriptionPlanCreate(BaseModel):
    name: str
    duration_days: int
    price: float
    features: Dict[str, Any] = {}
    is_active: bool = True

class SubscriptionPlanResponse(BaseModel):
    id: UUID
    name: str
    duration_days: int
    price: float
    features: Dict[str, Any]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Subscription Schemas
class SubscriptionCreate(BaseModel):
    plan_id: UUID
    payment_method_id: Optional[str] = None # Placeholder for payment gateway token

class SubscriptionResponse(BaseModel):
    id: UUID
    developer_id: UUID
    plan_id: UUID
    start_date: datetime
    end_date: datetime
    status: SubscriptionStatus
    plan_name: Optional[str] = None # Augmented
    
    class Config:
        from_attributes = True
