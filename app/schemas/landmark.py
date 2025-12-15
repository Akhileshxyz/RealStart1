from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.schemas.project import ProjectResponse

class LandmarkCreate(BaseModel):
    name: str
    city: str
    zone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    avg_price_per_sqft: Optional[float] = None
    median_price: Optional[float] = None
    growth_forecast_5yr: Optional[float] = None 
    price_trend: Optional[str] = None
    price_trend_3m: Optional[str] = None
    
    total_projects: Optional[int] = 0
    active_layouts_count: Optional[int] = 0
    rera_projects_count: Optional[int] = 0
    
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
    median_price: Optional[float] = None
    growth_forecast_5yr: Optional[float] = None 
    price_trend: Optional[str] = None
    price_trend_3m: Optional[str] = None
    
    total_projects: Optional[int] = 0
    active_layouts_count: Optional[int] = 0
    rera_projects_count: Optional[int] = 0
    
    description: Optional[str] = None
    nearby_amenities: Optional[Dict[str, Any]] = None
    
    nearby_projects: List[ProjectResponse] = []
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
