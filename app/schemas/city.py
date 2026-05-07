from typing import List, Optional, Union, Any, Dict
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.landmark import UpcomingHighlightSchema

class PricePointSchema(BaseModel):
    year: int
    value: float
    reason: Optional[str] = None
    reason_kn: Optional[str] = None

class PredictionPointSchema(BaseModel):
    year: int
    value1: float
    value2: float
    reason: Optional[str] = None
    reason_kn: Optional[str] = None

class PoliticalAgendaSchema(BaseModel):
    mla: str
    mla_kn: Optional[str] = None
    mp: str
    mp_kn: Optional[str] = None

class LandmarkRichResponse(BaseModel):
    """Detailed Landmark info for summary view in city details"""
    id: UUID
    name: str
    name_kn: Optional[str] = None
    image_url: Optional[str] = None
    location: Optional[Any] = None # GeoJSON coordinates
    amenities: Optional[List[str]] = [] # nearby_amenities
    amenities_kn: Optional[List[str]] = []
    
    avg_plot_price: Optional[Union[float, str]] = 0
    avg_commercial_plot_price: Optional[Union[float, str]] = 0
    avg_price_per_sqft: Optional[Union[float, str]] = 0
    residential_rent_2bhk: Optional[str] = ""
    rental_yield: Optional[str] = "" 
    upcoming_projects_list: Optional[List[UpcomingHighlightSchema]] = []
    nearby_landmarks_list: Optional[List[UpcomingHighlightSchema]] = []
    risk_profile: Optional[str] = "moderate"

    class Config:
        from_attributes = True
        populate_by_name = True

class LandmarkFullPublicResponse(BaseModel):
    """Full Landmark details for Market Intelligence view"""
    id: UUID
    name: str
    city: str
    zone: Optional[str] = None
    location: Optional[Any] = None
    
    # Market Data
    avg_price_per_sqft: Optional[Union[float, str]] = None
    median_price: Optional[float] = None
    growth_forecast_5yr: Optional[float] = None # Percentage 
    price_trend: Optional[str] = None  # "rising", "stable", "falling"
    price_trend_3m: Optional[str] = None # e.g. "+5.2%"
    
    total_projects: Optional[int] = 0
    active_layouts_count: Optional[int] = 0
    rera_projects_count: Optional[int] = 0

    # Meta
    description: Optional[str] = None
    amenities: Optional[Union[List[str], Dict[str, Any]]] = Field(None, alias="nearby_amenities")
    image_url: Optional[str] = None

    class Config:
        populate_by_name = True
        from_attributes = True

class CityBase(BaseModel):
    name: str
    name_kn: Optional[str] = None
    slug: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    images: List[str] = []
    city_report_pdf: Optional[str] = None
    city_gif: Optional[str] = None
    
    # Financial/Price Stats
    avg_appreciation_start_value: float = 0
    avg_appreciation_end_value: float = 0
    
    # Consolidated Market Intelligence Fields (The 6 Boxes)
    avg_commercial_plot_price: float = 0
    avg_residential_plot_price: float = 0
    avg_rental_2bhk: Optional[str] = None
    economic_output: Optional[str] = None
    population: Optional[str] = None
    appreciation_potential_5yr: Optional[str] = None
    
    # Descriptions
    feature_description: Optional[str] = None
    feature_description_kn: Optional[str] = None
    city_description: Optional[str] = None
    city_description_kn: Optional[str] = None

    # Chart Data - Historical
    price_growth_history: List[PricePointSchema] = []
    
    # Chart Data - Future Prediction
    price_prediction: List[PredictionPointSchema] = [] 

    # Locations
    top_developed_projects: List[UUID] = []
    
    # Politics & Policy
    political_infrastructure_agenda: PoliticalAgendaSchema = Field(default_factory=lambda: PoliticalAgendaSchema(mla="", mp=""))
    key_policies: List[str] = []
    key_policies_kn: List[str] = []

    # Extra
    landmarks_id_list: List[UUID] = []
    top_landmarks_to_invest: List[UUID] = []
    upcoming_projects_list: List[str] = []
    upcoming_projects_list_kn: List[str] = []
    
    # Market Intelligence Text Lists
    amenities: List[str] = []
    amenities_kn: List[str] = []
    market_upcoming_projects: List[str] = []
    market_upcoming_projects_kn: List[str] = []
    
    is_active: bool = True

class CityCreate(CityBase):
    pass

class CityUpdate(BaseModel):
    name: Optional[str] = None
    name_kn: Optional[str] = None
    slug: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    images: Optional[List[str]] = None
    city_report_pdf: Optional[str] = None
    city_gif: Optional[str] = None
    
    avg_appreciation_start_value: Optional[float] = None
    avg_appreciation_end_value: Optional[float] = None
    avg_commercial_plot_price: Optional[float] = None
    avg_residential_plot_price: Optional[float] = None
    avg_rental_2bhk: Optional[str] = None
    economic_output: Optional[str] = None
    population: Optional[str] = None
    appreciation_potential_5yr: Optional[str] = None
    feature_description: Optional[str] = None
    feature_description_kn: Optional[str] = None
    city_description: Optional[str] = None
    city_description_kn: Optional[str] = None
    
    price_growth_history: Optional[List[PricePointSchema]] = None
    price_prediction: Optional[List[PredictionPointSchema]] = None

    top_developed_projects: Optional[List[UUID]] = None
    political_infrastructure_agenda: Optional[PoliticalAgendaSchema] = None
    key_policies: Optional[List[str]] = None
    key_policies_kn: Optional[List[str]] = None
    
    landmarks_id_list: Optional[List[UUID]] = None
    top_landmarks_to_invest: Optional[List[UUID]] = None
    upcoming_projects_list: Optional[List[str]] = None
    upcoming_projects_list_kn: Optional[List[str]] = None
    
    # Market Intelligence Text Lists
    amenities: Optional[List[str]] = None
    amenities_kn: Optional[List[str]] = None
    market_upcoming_projects: Optional[List[str]] = None
    market_upcoming_projects_kn: Optional[List[str]] = None
    
    is_active: Optional[bool] = None

class CityResponse(CityBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CityPublicDetailsResponse(CityBase):
    """City details with RESOLVED objects for public view"""
    id: UUID
    landmarks: List[LandmarkRichResponse] = []
    top_landmarks_to_invest: List[Any] = []
    top_developed_projects: List[Any] = [] # Resolved project objects
    upcoming_projects_list: List[str] = [] # Manual upcoming projects list
    
    # Intelligence Data (Merged from MarketIntelligence)
    investment_landmarks: List[Any] = []
    map_landmarks: List[Any] = []
    city_gif: Optional[str] = None
    
    # Hide the raw ID list in the public details API
    landmarks_id_list: Optional[List[UUID]] = Field(None, exclude=True)
    # The raw top_developed_projects from CityBase will be overridden by the List[Any] above in response model, 
    # but to be safe and clean, we can exclude the raw UUID list if needed. 
    # Actually, CityBase has top_developed_projects: List[UUID]. 
    # We want to return list of objects under the same key.

