from typing import List, Optional, Any, Union
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import Field, BaseModel, field_validator
from app.utils.parsers import parse_price_string
from beanie import Document, Indexed

class PricePoint(BaseModel):
    year: int
    value: float
    reason: Optional[str] = None
    reason_kn: Optional[str] = None

    @field_validator('value', mode='before')
    @classmethod
    def parse_value(cls, v: Any) -> float:
        return parse_price_string(v)

class PredictionPoint(BaseModel):
    year: int
    value1: float # e.g. City Prediction
    value2: float # e.g. State Prediction
    reason: Optional[str] = None
    reason_kn: Optional[str] = None

    @field_validator('value1', 'value2', mode='before')
    @classmethod
    def parse_values(cls, v: Any) -> float:
        return parse_price_string(v)

class PoliticalAgenda(BaseModel):
    mla: str
    mla_kn: Optional[str] = None
    mp: str
    mp_kn: Optional[str] = None

class City(Document):
    id: UUID = Field(default_factory=uuid4)
    name: str = Indexed(unique=True) 
    name_kn: Optional[str] = None
    slug: str = Indexed(unique=True) 
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

    @field_validator('avg_appreciation_start_value', 'avg_appreciation_end_value', 
                     'avg_commercial_plot_price', 'avg_residential_plot_price', mode='before')
    @classmethod
    def validate_prices(cls, v: Any) -> float:
        return parse_price_string(v)
    avg_rental_2bhk: Optional[str] = None # e.g. "₹9,000 – ₹13,000"
    economic_output: Optional[str] = None # e.g. "₹10,000 – ₹12,000 Crores"
    population: Optional[str] = None # e.g. "1.40 Lakhs"
    appreciation_potential_5yr: Optional[str] = None # e.g. "35% – 45%"
    
    # Other Descriptions
    feature_description: Optional[str] = None # One-liner highlights
    feature_description_kn: Optional[str] = None
    city_description: Optional[str] = None # Deep full city overview
    city_description_kn: Optional[str] = None

    # Chart Data - Historical
    price_growth_history: List[PricePoint] = [] 
    
    # Chart Data - Future Prediction (Next 5 Years)
    price_prediction: List[PredictionPoint] = [] 
    
    # Locations
    top_developed_projects: List[UUID] = []
    
    # Politics & Policy
    political_infrastructure_agenda: PoliticalAgenda = Field(default_factory=lambda: PoliticalAgenda(mla="", mp=""))
    key_policies: List[str] = []
    key_policies_kn: List[str] = []

    # System fields
    landmarks_id_list: List[UUID] = [] 
    top_landmarks_to_invest: List[UUID] = []
    upcoming_projects_list: List[str] = [] # Manual string list
    upcoming_projects_list_kn: List[str] = []
    
    # Market Intelligence Text Lists
    amenities: List[str] = []
    amenities_kn: List[str] = []
    market_upcoming_projects: List[str] = []
    market_upcoming_projects_kn: List[str] = []
    
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "cities"
        indexes = ["slug", "name"]
