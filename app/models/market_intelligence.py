from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Dict, Any, List
from beanie import Document
from pydantic import Field

class MarketIntelligence(Document):
    id: UUID = Field(default_factory=uuid4)
    landmark_id: UUID  # Reference to the City/Locality Landmark
    parent_landmark_id: Optional[UUID] = None # Reference to Parent City (if this is an area)
    location_type: str = Field(default="city") # "city" or "area"
    
    overview: str
    
    # Box Content / Stats
    avg_commercial_plot_price: float
    avg_residential_plot_price: float
    avg_rental_2bhk: float
    economic_output: str
    population: str
    appreciation_potential_5yr: str
    
    # Growth History (Last 5 Years)
    growth_history: List[Dict[str, Any]]  # [{"year": 2020, "price": 14, "reason": "..."}]
    
    # Growth Prediction (Next 5 Years)
    growth_prediction: List[Dict[str, Any]] # [{"year": 2026, "price": 27, "reason": "..."}]
    
    # Political & Infrastructure Agenda
    political_agenda: Dict[str, Any] # {"mla": "...", "mp": "...", "governance": "...", "focus": ["..."]}
    
    # Key Amenities
    amenities: List[str]
    
    # Upcoming Development Projects
    upcoming_projects: List[str]
    
    # Top Investment Landmarks
    investment_landmarks: List[Dict[str, Any]] # [{"name": "...", "residential": 28, "commercial": 38, "rental": 12, "growth": 40}]
    
    # Major Landmarks for Map
    map_landmarks: List[Dict[str, Any]] # [{"name": "...", "price": 38, "growth": 32}]
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "market_intelligence"
        indexes = [
            "landmark_id",
            "parent_landmark_id"
        ]
