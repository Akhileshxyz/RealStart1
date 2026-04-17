from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Dict, Any, List, Union
from beanie import Document, PydanticObjectId
from pydantic import Field, field_validator
from app.utils.parsers import parse_price_string

class MarketIntelligence(Document):
    id: Union[UUID, PydanticObjectId] = Field(default_factory=uuid4)
    landmark_id: Optional[UUID] = None  # Reference to the City/Locality Landmark
    parent_landmark_id: Optional[UUID] = None # Reference to Parent City (if this is an area)
    location_type: str = Field(default="city") # "city" or "area"
    
    overview: Optional[str] = None
    
    # Box Content / Stats
    avg_commercial_plot_price: float = 0
    avg_residential_plot_price: float = 0

    @field_validator('avg_commercial_plot_price', 'avg_residential_plot_price', mode='before')
    @classmethod
    def parse_prices(cls, v: Any) -> float:
        return parse_price_string(v)
    avg_rental_2bhk: str = ""
    avg_rental_yield: Optional[str] = None
    economic_output: str = ""
    population: str = ""
    appreciation_potential_5yr: str = ""

    @field_validator('avg_rental_2bhk', mode='before')
    @classmethod
    def parse_rental(cls, v: Any) -> str:
        if v is None:
            return ""
        if isinstance(v, (int, float)):
            return str(v)
        return str(v)
    
    # Growth History (Last 5 Years)
    growth_history: List[Any]  # List[Dict[str, Any]] but Any to prevent Beanie fetch crash on legacy data
    
    # Growth Prediction (Next 5 Years)
    growth_prediction: List[Any] # List[Dict[str, Any]] but Any to prevent Beanie fetch crash on legacy data
    
    # Political & Infrastructure Agenda
    political_agenda: Dict[str, Any] = Field(default_factory=dict)
    
    # Key Amenities
    amenities: List[Any]  # List[Dict[str, Any]] but Any to prevent Beanie fetch crash on legacy data
    
    # Upcoming Development Projects
    upcoming_projects: List[str] = []
    
    # Top Investment Landmarks
    investment_landmarks: List[Any] # List[Dict[str, Any]] but Any to prevent Beanie fetch crash on legacy data
    
    # Major Landmarks for Map
    map_landmarks: List[Any] # List[Dict[str, Any]] but Any to prevent Beanie fetch crash on legacy data
    
    report_download_url: Optional[str] = None
    expert_contact_id: Optional[UUID] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "market_intelligence"
        indexes = [
            "landmark_id",
            "parent_landmark_id"
        ]
