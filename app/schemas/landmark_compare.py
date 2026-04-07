from typing import List, Optional, Dict
from uuid import UUID
from pydantic import BaseModel

class PriceSnapshot(BaseModel):
    residential_land: str
    commercial_land: str
    rental_rent: str
    appreciation_5yr: str

class LocationTraits(BaseModel):
    rental: str
    growth: str
    family: str
    traffic: str
    social: str

class ComparisonLocation(BaseModel):
    id: UUID
    name: str
    zone: Optional[str] = None
    image_url: Optional[str] = None
    price_snapshot: PriceSnapshot
    traits: LocationTraits

class GrowthDataset(BaseModel):
    label: str
    data: List[float]

class HistoricalGrowthChart(BaseModel):
    labels: List[str]
    datasets: List[GrowthDataset]

class ComparisonConclusion(BaseModel):
    best_for_investors: str
    best_for_end_users: str
    guidance_investor: str
    guidance_end_user: str

from app.schemas.landmark import LandmarkSummary

class LandmarkCompareResponse(BaseModel):
    base_location: ComparisonLocation
    target_location: ComparisonLocation
    historical_growth_chart: HistoricalGrowthChart
    conclusion: ComparisonConclusion
    nearby_landmarks: List[LandmarkSummary] = []

