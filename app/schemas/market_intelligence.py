from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class MarketHistoryItem(BaseModel):
    year: int
    price: float
    reason: str

class MarketPredictionItem(BaseModel):
    year: int
    price: float
    reason: str

class PoliticalAgenda(BaseModel):
    mla: str
    mp: str
    governance: str
    focus: List[str]

class InvestmentLandmark(BaseModel):
    name: str
    residential: float
    commercial: float
    rental: str
    growth: float

class MapLandmark(BaseModel):
    name: str
    price: float
    growth: float

class MarketIntelligenceBase(BaseModel):
    landmark_id: UUID
    overview: str
    avg_commercial_plot_price: float
    avg_residential_plot_price: float
    avg_rental_2bhk: float
    economic_output: str
    population: str
    appreciation_potential_5yr: str
    growth_history: List[MarketHistoryItem]
    growth_prediction: List[MarketPredictionItem]
    political_agenda: PoliticalAgenda
    amenities: List[str]
    upcoming_projects: List[str]
    investment_landmarks: List[InvestmentLandmark]
    map_landmarks: List[MapLandmark]

class MarketIntelligenceCreate(MarketIntelligenceBase):
    pass

class MarketIntelligenceUpdate(BaseModel):
    overview: Optional[str] = None
    avg_commercial_plot_price: Optional[float] = None
    avg_residential_plot_price: Optional[float] = None
    avg_rental_2bhk: Optional[float] = None
    economic_output: Optional[str] = None
    population: Optional[str] = None
    appreciation_potential_5yr: Optional[str] = None
    growth_history: Optional[List[MarketHistoryItem]] = None
    growth_prediction: Optional[List[MarketPredictionItem]] = None
    political_agenda: Optional[PoliticalAgenda] = None
    amenities: Optional[List[str]] = None
    upcoming_projects: Optional[List[str]] = None
    investment_landmarks: Optional[List[InvestmentLandmark]] = None
    map_landmarks: Optional[List[MapLandmark]] = None

class MarketIntelligenceSummary(BaseModel):
    landmark_id: UUID
    name: str
    city: str
    overview: str
    appreciation_potential: str

class MarketIntelligenceResponse(MarketIntelligenceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
