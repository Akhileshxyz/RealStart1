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

    @field_validator('value', mode='before')
    @classmethod
    def parse_value(cls, v: Any) -> Any:
        return v

class PredictionPoint(BaseModel):
    year: int
    value1: float # e.g. City Prediction
    value2: float # e.g. State Prediction
    reason: Optional[str] = None

    @field_validator('value1', 'value2', mode='before')
    @classmethod
    def parse_values(cls, v: Any) -> Any:
        return v

class PoliticalAgenda(BaseModel):
    mla: str
    mp: str

class City(Document):
    id: UUID = Field(default_factory=uuid4)
    name: str = Indexed(unique=True) 
    slug: str = Indexed(unique=True) 
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    images: List[str] = [] 
    city_report_pdf: Optional[str] = None 
    
    # Financial/Price Stats
    avg_appreciation_start_value: Union[float, str] = 0
    avg_appreciation_end_value: Union[float, str] = 0
    # Consolidated Market Intelligence Fields (The 6 Boxes)
    avg_commercial_plot_price: Union[float, str] = 0
    avg_residential_plot_price: Union[float, str] = 0
    avg_rental_2bhk: Optional[str] = None # e.g. "₹9,000 – ₹13,000"
    economic_output: Optional[str] = None # e.g. "₹10,000 – ₹12,000 Crores"
    population: Optional[str] = None # e.g. "1.40 Lakhs"
    appreciation_potential_5yr: Optional[str] = None # e.g. "35% – 45%"
    
    # Other Descriptions
    feature_description: Optional[str] = None # One-liner highlights
    city_description: Optional[str] = None # Deep full city overview

    # Chart Data - Historical
    price_growth_history: List[PricePoint] = [] 
    
    # Chart Data - Future Prediction (Next 5 Years)
    price_prediction: List[PredictionPoint] = [] 
    
    # Locations
    top_developed_projects: List[UUID] = []
    
    # Politics & Policy
    political_infrastructure_agenda: PoliticalAgenda = Field(default_factory=lambda: PoliticalAgenda(mla="", mp=""))
    key_policies: List[str] = []

    # System fields
    landmarks_id_list: List[UUID] = [] 
    top_landmarks_to_invest: List[UUID] = []
    upcoming_projects_list: List[str] = [] # Manual string list
    
    # Market Intelligence Text Lists
    amenities: List[str] = []
    market_upcoming_projects: List[str] = []
    
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "cities"
        indexes = ["slug", "name"]
