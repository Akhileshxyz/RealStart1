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
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    landmark_id: Optional[UUID] = None

class MarketIntelligenceBase(BaseModel):
    landmark_id: UUID
    parent_landmark_id: Optional[UUID] = None
    location_type: str = "city"
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
    parent_landmark_id: Optional[UUID] = None
    location_type: Optional[str] = None
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

class MarketCityListItem(BaseModel):
    """City-level row for GET /market-intelligence (note: city block first)."""
    landmark_id: UUID
    name: str
    city: str
    overview: str
    appreciation_potential: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BoxContentSection(BaseModel):
    """Sections 2.x in note — numeric lakhs + human-readable strings where stored."""
    avg_commercial_plot_price: float
    avg_residential_plot_price: float
    avg_rental_2bhk: float
    economic_output: str
    population: str
    appreciation_potential_5yr: str


class ParentCityRef(BaseModel):
    """When `location_type` is `area`, links back to the parent city landmark."""
    landmark_id: UUID
    name: str
    city: str


class MarketAreaSummary(BaseModel):
    """Sub-areas under a city; lat/lng optional until geocoding API is wired."""
    landmark_id: UUID
    parent_landmark_id: UUID
    name: str
    city: str
    overview: str
    appreciation_potential: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class MarketIntelligenceDetailPublic(BaseModel):
    """
    City or area detail. Maps to note sections:
    - City: overview → box → history → prediction → political & infrastructure → amenities → upcoming → top investment landmarks → map landmarks (+ optional `areas`).
    - Area: same fields; use `investment_landmarks` as “Top spots to invest nearby”; `map_landmarks` often empty; `political_agenda` may be empty; `parent_city` set when area.
    """
    id: UUID
    landmark_id: UUID
    parent_landmark_id: Optional[UUID] = None
    parent_city: Optional[ParentCityRef] = None
    location_type: str
    name: str
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    market_overview: str
    overview: str
    box_content: BoxContentSection
    growth_history: List[Dict[str, Any]]
    growth_prediction: List[Dict[str, Any]]
    political_agenda: Dict[str, Any]
    amenities: List[str]
    upcoming_projects: List[str]
    investment_landmarks: List[Dict[str, Any]]
    map_landmarks: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    areas: Optional[List[MarketAreaSummary]] = None


class MarketIntelligenceResponse(MarketIntelligenceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
