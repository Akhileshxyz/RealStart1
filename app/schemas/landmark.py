from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class LandmarkCreate(BaseModel):
    name: str
    city: str
    zone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    avg_price_per_sqft: Optional[float] = None
    price_trend: Optional[str] = None
    total_projects: Optional[int] = 0
    description: Optional[str] = None
    nearby_amenities: Optional[Dict[str, Any]] = None

class LandmarkResponse(BaseModel):
    id: UUID
    name: str
    city: str
    zone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    avg_price_per_sqft: Optional[float] = None
    price_trend: Optional[str] = None
    total_projects: Optional[int] = 0
    description: Optional[str] = None
    nearby_amenities: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
