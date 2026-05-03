from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Dict, Any, List, Union
from enum import Enum
import re
from app.utils.parsers import parse_price_string
from beanie import Document, Indexed
from pydantic import BaseModel, Field, field_validator, model_validator

class RiskProfile(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"

class GeoJSONLocation(BaseModel):
    type: str = "Point"
    coordinates: Optional[List[float]] = None  # [longitude, latitude]

class LandmarkPricePoint(BaseModel):
    year: int
    value: Union[float, str] = 0
    reason: str = ""
    reason_kn: Optional[str] = None

    @field_validator("value", mode="before")
    @classmethod
    def ensure_string_value(cls, v):
        if v is None:
            return ""
        if isinstance(v, (int, float)):
            return str(v)
        return v

class UpcomingHighlight(BaseModel):
    title: str
    title_kn: Optional[str] = None
    description: Optional[str] = None
    description_kn: Optional[str] = None
    icon_url: Optional[str] = None

    @field_validator("title", mode="before")
    @classmethod
    def handle_legacy_string(cls, v, info):
        # If the whole input to UpcomingHighlight is a string, 
        # Pydantic calls the validator for each field. 
        # But wait, 'mode="before"' on a field only works if the input is a dict.
        # To handle the case where the whole item is a string, we need a model_validator.
        return v

    @model_validator(mode="before")
    @classmethod
    def validate_whole_model(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"title": data}
        return data


class LandmarkPredictionPoint(BaseModel):
    year: int
    value: Union[float, str] = 0
    reason: str = ""
    reason_kn: Optional[str] = None

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

class Landmark(Document):
    id: UUID = Field(default_factory=uuid4)
    name: str = Indexed()
    name_kn: Optional[str] = None
    city_id: UUID = Indexed()
    hero_desc: Optional[str] = None
    hero_desc_kn: Optional[str] = None
    description: Optional[str] = None
    description_kn: Optional[str] = None
    city: Optional[str] = None
    
    # Location
    location: Optional[GeoJSONLocation] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    zone: Optional[str] = None
    
    # Media
    images: List[str] = [] # Array of image paths
    image_url: Optional[str] = None
    
    # Financial/Market Data
    avg_plot_price: Union[float, str] = 0
    avg_apartment_price: Union[float, str] = 0
    avg_price_per_sqft: Union[float, str] = 0
    residential_rent_2bhk: str = ""
    rental_yield: str = "" # e.g. "4.5%"
    risk_profile: RiskProfile = RiskProfile.MODERATE

    
    price_trend: Optional[str] = None  # "rising", "stable", "falling"
    price_trend_3m: Optional[str] = None # e.g. "+5.2%"
    
    # Chart Data (City-Style)
    price_growth: List[LandmarkPricePoint] = []
    price_prediction: List[LandmarkPredictionPoint] = []

    # Project Stats
    total_projects: int = 0
    active_layouts_count: int = 0
    rera_projects_count: int = 0
    
    # Related Entities
    nearby_landmarks_ids: List[UUID] = []
    upcoming_project_ids: List[UUID] = []
    nearby_project_ids: List[UUID] = []
    nearby_amenities: Optional[Union[List[str], Dict[str, Any]]] = None
    nearby_amenities_kn: Optional[List[str]] = []
    amenities: List[str] = []
    amenities_kn: List[str] = []
    upcoming_projects_list: List[UpcomingHighlight] = []
    nearby_landmarks_list: List[UpcomingHighlight] = []

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "landmarks"
        indexes = [
            [("location", "2dsphere")],
            "city_id",
            "name"
        ]

class LandmarkSave(Document):
    id: UUID = Field(default_factory=uuid4)
    landmark_id: UUID
    user_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "landmarks_saves"
        indexes = [
            "landmark_id",
            "user_id",
            [("landmark_id", 1), ("user_id", 1)]  # Unique per user-landmark pair
        ]
