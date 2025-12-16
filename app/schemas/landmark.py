from typing import Optional, Dict, Any, List, Union
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, field_validator
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
    nearby_amenities: Optional[Union[List[str], Dict[str, Any]]] = None

    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        if v is not None and (v < -90 or v > 90):
            raise ValueError('Latitude must be between -90 and 90 degrees')
        return v

    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        if v is not None and (v < -180 or v > 180):
            raise ValueError('Longitude must be between -180 and 180 degrees')
        return v

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
    nearby_amenities: Optional[Union[List[str], Dict[str, Any]]] = None

    nearby_projects: List[ProjectResponse] = []
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
