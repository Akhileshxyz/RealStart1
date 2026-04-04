from typing import List, Optional, Union, Any, Dict
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class PricePointSchema(BaseModel):
    year: int
    value: float

class PredictionPointSchema(BaseModel):
    year: int
    value1: float
    value2: float

class SubAreaSchema(BaseModel):
    name: str
    image: str
    desc: str
    growth: str

class PoliticalAgendaSchema(BaseModel):
    mla: str
    mp: str

class LandmarkRichResponse(BaseModel):
    """Detailed Landmark info for public display"""
    id: UUID
    name: str
    image_url: Optional[str] = None
    location: Optional[Any] = None # GeoJSON coordinates
    amenities: Optional[List[str]] = [] # nearby_amenities

class CityBase(BaseModel):
    name: str
    slug: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    images: List[str] = []
    city_report_pdf: Optional[str] = None
    
    # Financial/Price Stats
    avg_appreciation_start_value: float = 0
    avg_appreciation_end_value: float = 0
    avg_commercial_plot_price: float = 0
    avg_residential_plot_price: float = 0
    residential_rent_2bhk_description: str = ""

    # NEW FIELDS
    population_urban: Optional[str] = None
    rental_yield: Optional[str] = None
    feature_description: Optional[str] = None
    city_description: Optional[str] = None

    # Chart Data - Historical
    price_growth_history: List[PricePointSchema] = []
    
    # Chart Data - Future Prediction
    price_prediction: List[PredictionPointSchema] = [] 

    # Locations
    top_sub_areas: List[SubAreaSchema] = []
    
    # Politics & Policy
    political_infrastructure_agenda: PoliticalAgendaSchema = Field(default_factory=lambda: PoliticalAgendaSchema(mla="", mp=""))
    key_policies: List[str] = []

    # Extra
    landmarks_id_list: List[UUID] = []
    upcoming_projects_list: List[str] = []
    is_active: bool = True

class CityCreate(CityBase):
    pass

class CityUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    images: Optional[List[str]] = None
    city_report_pdf: Optional[str] = None
    
    avg_appreciation_start_value: Optional[float] = None
    avg_appreciation_end_value: Optional[float] = None
    avg_commercial_plot_price: Optional[float] = None
    avg_residential_plot_price: Optional[float] = None
    residential_rent_2bhk_description: Optional[str] = None

    population_urban: Optional[str] = None
    rental_yield: Optional[str] = None
    feature_description: Optional[str] = None
    city_description: Optional[str] = None
    
    price_growth_history: Optional[List[PricePointSchema]] = None
    price_prediction: Optional[List[PredictionPointSchema]] = None

    top_sub_areas: Optional[List[SubAreaSchema]] = None
    political_infrastructure_agenda: Optional[PoliticalAgendaSchema] = None
    key_policies: Optional[List[str]] = None
    
    landmarks_id_list: Optional[List[UUID]] = None
    upcoming_projects_list: Optional[List[str]] = None
    is_active: Optional[bool] = None

class CityResponse(CityBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CityPublicDetailsResponse(CityBase):
    """City details with RESOLVED landmark objects for public view"""
    id: UUID
    landmarks: List[LandmarkRichResponse] = []
    
    # Hide the raw ID list in the public details API
    landmarks_id_list: Optional[List[UUID]] = Field(None, exclude=True)
