from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import Field, BaseModel
from beanie import Document, Indexed

class PricePoint(BaseModel):
    year: int
    value: float

class PredictionPoint(BaseModel):
    year: int
    value1: float # e.g. City Prediction
    value2: float # e.g. State Prediction

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
    avg_appreciation_start_value: float = 0 
    avg_appreciation_end_value: float = 0 
    avg_commercial_plot_price: float = 0
    avg_residential_plot_price: float = 0
    residential_rent_2bhk_description: str = "" 
    
    # NEW FIELDS: Population, Yield, and Descriptions
    population_urban: Optional[str] = None # e.g. "13.6M"
    rental_yield: Optional[str] = None # e.g. "3.2%"
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
    upcoming_projects_list: List[UUID] = [] 
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "cities"
        indexes = ["slug", "name"]
