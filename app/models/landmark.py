from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Dict, Any, List, Union
from beanie import Document
from pydantic import BaseModel, Field

class GeoJSONLocation(BaseModel):
    type: str = "Point"
    coordinates: List[float] # [longitude, latitude]

class Landmark(Document):
    id: UUID = Field(default_factory=uuid4)
    name: str
    city: str
    zone: Optional[str] = None
    
    # GeoJSON Location (Mandatory for map features)
    location: GeoJSONLocation 
    # Structure: {"type": "Point", "coordinates": [longitude, latitude]}
    
    # Legacy/Display helpers (optional, can be derived)
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Market Data
    avg_price_per_sqft: Optional[float] = None
    median_price: Optional[float] = None
    growth_forecast_5yr: Optional[float] = None # Percentage 
    price_trend: Optional[str] = None  # "rising", "stable", "falling"
    price_trend_3m: Optional[str] = None # e.g. "+5.2%"
    
    total_projects: Optional[int] = 0
    active_layouts_count: Optional[int] = 0
    rera_projects_count: Optional[int] = 0

    # Additional metadata
    description: Optional[str] = None
    nearby_amenities: Optional[Union[List[str], Dict[str, Any]]] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "landmarks"
        indexes = [
            [("location", "2dsphere")],
            "city",
            "name"
        ]
