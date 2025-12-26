from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

# ========== Transaction Schemas ==========

class PropertyTransactionResponse(BaseModel):
    registry_date: datetime
    society_name: Optional[str] = None
    agreement_price: float
    area_sqft: float
    area_type: str
    price_per_sqft: float
    property_type: str
    bhk: Optional[int] = None
    floor: Optional[int] = None
    purchase_type: str

    class Config:
        from_attributes = True


class TransactionStatsResponse(BaseModel):
    total_transactions: int
    avg_price_sqft: float
    min_price_sqft: float
    max_price_sqft: float
    median_price_sqft: Optional[float] = None


# ========== Society Schemas ==========

class SocietyResponse(BaseModel):
    id: UUID
    name: str
    builder_name: Optional[str] = None
    total_units: Optional[int] = None
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None
    rating: Optional[float] = None
    total_reviews: int
    amenities: List[str] = []
    rera_registered: bool

    class Config:
        from_attributes = True


class SocietyCreate(BaseModel):
    name: str
    landmark_id: Optional[UUID] = None
    locality_name: str
    city: str
    builder_name: Optional[str] = None
    total_units: Optional[int] = None
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None
    amenities: List[str] = []
    latitude: Optional[float] = None
    longitude: Optional[float] = None


# ========== Review Schemas ==========

class LocalityReviewCreate(BaseModel):
    landmark_id: UUID
    overall_rating: float = Field(ge=0, le=5)
    connectivity_rating: Optional[float] = Field(None, ge=0, le=5)
    lifestyle_rating: Optional[float] = Field(None, ge=0, le=5)
    safety_rating: Optional[float] = Field(None, ge=0, le=5)
    greenery_rating: Optional[float] = Field(None, ge=0, le=5)
    environment_rating: Optional[float] = Field(None, ge=0, le=5)
    title: Optional[str] = None
    review_text: Optional[str] = None


class LocalityReviewResponse(BaseModel):
    id: UUID
    landmark_id: UUID
    user_name: Optional[str] = None
    overall_rating: float
    connectivity_rating: Optional[float] = None
    lifestyle_rating: Optional[float] = None
    safety_rating: Optional[float] = None
    greenery_rating: Optional[float] = None
    environment_rating: Optional[float] = None
    title: Optional[str] = None
    review_text: Optional[str] = None
    helpful_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class RatingSummaryResponse(BaseModel):
    overall: float
    connectivity: float
    lifestyle: float
    safety: float
    greenery: float
    environment: float
    total_reviews: int


# ========== Price Insights Schemas ==========

class PriceInsightsSummary(BaseModel):
    avg_price_sqft: float
    yoy_growth: Optional[float] = None
    last_5_year_growth: Optional[float] = None


class PriceByBHKResponse(BaseModel):
    bhk_1: Optional[Dict[str, float]] = None  # {"min": 3500000, "max": 8400000}
    bhk_2: Optional[Dict[str, float]] = None
    bhk_3: Optional[Dict[str, float]] = None
    bhk_4: Optional[Dict[str, float]] = None


class PriceTrendDataPoint(BaseModel):
    period: str  # "2021-Q1" or "2021"
    avg_price_sqft: float
    total_transactions: int


class PriceTrendResponse(BaseModel):
    labels: List[str]
    values: List[float]
    transactions: List[int]


# ========== Demand/Supply Schemas ==========

class DemandOverviewResponse(BaseModel):
    land: int
    apartment: int
    villa: int
    independent_floor: int


class DemandBySocietyResponse(BaseModel):
    society: str
    search_percentage: float
    search_count: int


class SupplyOverviewResponse(BaseModel):
    apartment: int
    land: int
    villa: int
    independent_floor: int


# ========== Locality Overview Schemas ==========

class LocalityHighlightsResponse(BaseModel):
    positives: List[str]
    negatives: List[str]


class LocalityOverviewResponse(BaseModel):
    id: UUID
    name: str
    city: str
    zone: Optional[str] = None
    rating: Optional[float] = None
    total_reviews: int = 0
    avg_price_per_sqft: Optional[float] = None
    growth_forecast_5yr: Optional[float] = None
    price_trend: Optional[str] = None
    total_projects: int = 0
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True


class NearbyAreaResponse(BaseModel):
    name: str
    distance_km: float
    price_sqft: Optional[float] = None
    price_difference_percent: Optional[float] = None


# ========== Graph/Dashboard Schemas ==========

class LocalityDashboardResponse(BaseModel):
    """Complete dashboard data for a locality"""
    overview: LocalityOverviewResponse
    price_insights: PriceInsightsSummary
    recent_transactions: List[PropertyTransactionResponse]
    price_trend: PriceTrendResponse
    demand_overview: DemandOverviewResponse
    supply_overview: SupplyOverviewResponse
    top_societies: List[SocietyResponse]
    rating_summary: RatingSummaryResponse
    nearby_areas: List[NearbyAreaResponse]
