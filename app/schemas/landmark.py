from typing import Optional, Dict, Any, List, Union
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.landmark import RiskProfile

class LandmarkSelection(BaseModel):
    """Minimal schema for populating multi-select dropdowns"""
    id: UUID
    name: str
    city_id: Optional[UUID] = None
    zone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class LandmarkBulkDelete(BaseModel):
    landmark_ids: List[UUID]

class LandmarkPricePointSchema(BaseModel):
    year: int
    value: Union[float, str] = 0
    reason: str = ""

    @field_validator("value", mode="before")
    @classmethod
    def ensure_string_value(cls, v):
        if v is None:
            return ""
        if isinstance(v, (int, float)):
            return str(v)
        return v

    @field_validator("reason", mode="before")
    @classmethod
    def default_reason(cls, v):
        if v is None:
            return ""
        return v

class LandmarkPredictionPointSchema(BaseModel):
    year: int
    value: Union[float, str] = 0
    reason: str = ""

    @field_validator("value", mode="before")
    @classmethod
    def ensure_string_value(cls, v):
        if v is None:
            return ""
        if isinstance(v, (int, float)):
            return str(v)
        return v

    @field_validator("reason", mode="before")
    @classmethod
    def default_reason(cls, v):
        if v is None:
            return ""
        return v

class GeoJSONLocationSchema(BaseModel):
    type: str = "Point"
    coordinates: List[float] # [longitude, latitude]

class LandmarkSummary(BaseModel):
    """Reference summary for nested lists"""
    id: UUID
    name: str
    city_id: UUID
    images: List[str] = []
    avg_plot_price: float = 0
    location: Optional[GeoJSONLocationSchema] = None
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class UpcomingProjectSummary(BaseModel):
    id: UUID
    name: str
    slug: str
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    gallery_images: List[str] = []
    property_type: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)

class LandmarkBase(BaseModel):
    name: str
    city_id: UUID
    hero_desc: Optional[str] = None
    description: Optional[str] = None
    location: Optional[GeoJSONLocationSchema] = None
    zone: Optional[str] = None
    
    images: List[str] = []
    
    # Financial Stats
    avg_plot_price: Union[float, str] = 0
    avg_apartment_price: Union[float, str] = 0
    avg_price_per_sqft: Union[float, str] = 0
    residential_rent_2bhk: str = ""
    rental_yield: str = ""
    risk_profile: RiskProfile = RiskProfile.MODERATE

    @field_validator("avg_plot_price", "avg_apartment_price", "avg_price_per_sqft", mode="before")
    @classmethod
    def parse_price_string(cls, v: Any) -> str:
        if isinstance(v, str):
            return v
        return str(v) if v is not None else ""
    
    price_trend: Optional[str] = None
    price_trend_3m: Optional[str] = None
    
    # Chart Data
    price_growth: List[LandmarkPricePointSchema] = []
    price_prediction: List[LandmarkPredictionPointSchema] = []

    # Project Stats
    total_projects: int = 0
    active_layouts_count: int = 0
    rera_projects_count: int = 0
    
    # Relationships (Detailed for Response)
    nearby_landmarks: List[LandmarkSummary] = []
    upcoming_projects_list: List[UpcomingProjectSummary] = []
    nearby_projects: List[UpcomingProjectSummary] = []
    nearby_amenities: Optional[Union[List[str], Dict[str, Any]]] = None

    # Relationship IDs (For Input/Storage)
    nearby_landmarks_ids: List[UUID] = []
    upcoming_project_ids: List[UUID] = []
    nearby_project_ids: List[UUID] = []

class LandmarkCreate(LandmarkBase):
    pass

class LandmarkUpdate(BaseModel):
    name: Optional[str] = None
    city_id: Optional[UUID] = None
    hero_desc: Optional[str] = None
    description: Optional[str] = None
    location: Optional[GeoJSONLocationSchema] = None
    zone: Optional[str] = None
    images: Optional[List[str]] = None
    
    avg_plot_price: Optional[Union[float, str]] = None
    avg_apartment_price: Optional[Union[float, str]] = None
    avg_price_per_sqft: Optional[Union[float, str]] = None
    residential_rent_2bhk: Optional[str] = None
    rental_yield: Optional[str] = None
    risk_profile: Optional[RiskProfile] = None
    
    price_trend: Optional[str] = None
    price_trend_3m: Optional[str] = None
    
    price_growth: Optional[List[LandmarkPricePointSchema]] = None
    price_prediction: Optional[List[LandmarkPredictionPointSchema]] = None

    total_projects: Optional[int] = None
    active_layouts_count: Optional[int] = None
    rera_projects_count: Optional[int] = None
    
    nearby_landmarks_ids: Optional[List[UUID]] = None
    upcoming_project_ids: Optional[List[UUID]] = None
    nearby_project_ids: Optional[List[UUID]] = None
    nearby_amenities: Optional[Union[List[str], Dict[str, Any]]] = None

    # Re-use validator for Update too
    @field_validator("avg_plot_price", "avg_apartment_price", "avg_price_per_sqft", mode="before")
    @classmethod
    def parse_price_string(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, str):
            return v
        return str(v)

class LandmarkResponse(LandmarkBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaginatedLandmarkResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: List[LandmarkResponse]
    unique_cities: List[UUID]
