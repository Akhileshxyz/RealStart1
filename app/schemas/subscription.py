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
    payment_method_id: Optional[str] = None 

class SubscriptionOrderResponse(BaseModel):
    order_id: str
    amount: float
    currency: str = "INR"
    key_id: str

class SubscriptionVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

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
