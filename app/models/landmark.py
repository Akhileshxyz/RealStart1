from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Dict, Any
from beanie import Document
from pydantic import Field

class Landmark(Document):
    id: UUID = Field(default_factory=uuid4)
    name: str
    city: str
    zone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Market Data
    avg_price_per_sqft: Optional[float] = None
    price_trend: Optional[str] = None  # "rising", "stable", "falling"
    total_projects: Optional[int] = 0

    # Additional metadata
    description: Optional[str] = None
    nearby_amenities: Optional[Dict[str, Any]] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "landmarks"
