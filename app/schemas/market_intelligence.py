from typing import Optional, List, Dict, Any, Literal
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
    image_url: Optional[str] = Field(
        None,
        description="Locality thumbnail/hero; site-relative /uploads/... or absolute URL.",
    )


class BoxContentSection(BaseModel):
    """Stats grid on city/area detail (format currency/units in the app)."""
    avg_commercial_plot_price: float = Field(
        ...,
        description="Avg commercial land/plot — UI grid ‘commercial’ column.",
    )
    avg_residential_plot_price: float = Field(
        ...,
        description="Avg residential land/plot — UI grid ‘residential’ column.",
    )
    avg_rental_2bhk: float = Field(
        ...,
        description="Typical 2BHK monthly rent — UI rent column.",
    )
    economic_output: str = Field(
        ...,
        description="Economic / investment narrative (e.g. city-scale output) — optional extra stat row.",
    )
    population: str = Field(
        ...,
        description="Population or footfall line — optional extra stat row.",
    )
    appreciation_potential_5yr: str = Field(
        ...,
        description="5-year appreciation headline — UI growth / appreciation tile.",
    )


class AreaBoxContentSection(BaseModel):
    """Four stat cards for area MI screen only (no economic_output / population)."""
    avg_commercial_plot_price: float
    avg_residential_plot_price: float
    avg_rental_2bhk: float
    appreciation_potential_5yr: str


class ParentCityRef(BaseModel):
    """When `location_type` is `area`, links back to the parent city landmark."""
    landmark_id: UUID
    name: str
    city: str
    image_url: Optional[str] = None


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
    image_url: Optional[str] = None


class MarketIntelligenceDetailPublic(BaseModel):
    """
    Payload for `GET /api/v1/locality/market-intelligence/{landmark_id}` (city or area detail screen).

    UI mapping (RealStart market intelligence page):
    - Header / title: `name`, `city`
    - Map pins & tooltips: `map_landmarks` (name, price, growth, optional lat/lng, landmark_id)
    - Welcome + intro copy: `market_overview`
    - Key stats grid: `box_content`
    - “Last 5 years” chart: `growth_history` (year, price, reason)
    - “Next 5 years” chart: `growth_prediction`
    - Political & infrastructure: `political_agenda` (e.g. mla, mp, governance, focus[])
    - Key amenities row: `amenities`
    - Upcoming developments list: `upcoming_projects`
    - “Top landmarks / micro-markets to invest”: `investment_landmarks`
    - City only — sub-area chips / “More details” targets: `areas` (each row has landmark_id for area detail route)

    Not in this resource: featured project cards (“Top developed layouts”) — use projects/inventory APIs.
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
    image_url: Optional[str] = Field(
        None,
        description="Locality image from landmark.image_url.",
    )
    market_overview: str = Field(..., description="Primary long-form intro for the page.")
    box_content: BoxContentSection
    growth_history: List[Dict[str, Any]] = Field(
        ...,
        description="Series for the ‘Last 5 years’ price chart; items use year, price, reason.",
    )
    growth_prediction: List[Dict[str, Any]] = Field(
        ...,
        description="Series for the ‘Next 5 years’ forecast chart.",
    )
    political_agenda: Dict[str, Any] = Field(
        ...,
        description="Bullets for political & infrastructure agenda (structure: mla, mp, governance, focus).",
    )
    amenities: List[str] = Field(
        ...,
        description="Key amenities labels for icon row (hospital, schools, etc.).",
    )
    upcoming_projects: List[str] = Field(
        ...,
        description="Upcoming development / infra project lines.",
    )
    investment_landmarks: List[Dict[str, Any]] = Field(
        ...,
        description="Sub-locality / micro-market investment rows (name, residential, commercial, rental, growth).",
    )
    map_landmarks: List[Dict[str, Any]] = Field(
        ...,
        description="Pins on the map: name, price, growth, optional latitude, longitude, landmark_id.",
    )
    created_at: datetime
    updated_at: datetime
    areas: Optional[List[MarketAreaSummary]] = Field(
        None,
        description="Present for city rows when include_areas=true: sub-areas for tabs / drill-down.",
    )


class UpcomingDevelopmentItem(BaseModel):
    """Single row in ‘Upcoming developments’ (title + optional subtitle)."""
    title: str
    detail: Optional[str] = None


class AreaDevelopedLayoutPublic(BaseModel):
    """Card in ‘Top developed layouts near [landmark]’ horizontal list."""
    project_id: UUID
    name: str
    slug: str
    cover_image: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    approval_badge: Optional[str] = None
    location_hint: Optional[str] = None


class AreaComparisonHintPublic(BaseModel):
    """‘Compare this landmark market’ strip — benchmark vs parent city."""
    current_label: str = Field(..., description="Usually the area / landmark display name.")
    price_per_sqft_hint: Optional[float] = Field(
        None,
        description="From landmark.avg_price_per_sqft when set; else null.",
    )
    parent_city_landmark_id: Optional[UUID] = Field(
        None,
        description="Use for city benchmark / compare dropdown.",
    )


class MarketIntelligenceAreaDetailPublic(BaseModel):
    """
    **Only** for `GET /api/v1/locality/market-intelligence/areas/{landmark_id}` — area Market Intelligence screen.

    UI mapping:
    - Welcome + context: `name`, optional `zone` (e.g. “Manyata Tech Park surroundings”)
    - About: `market_overview`
    - Four stat cards: `box_content` (commercial, residential, rent, appreciation — no economic/population)
    - Top developed layouts carousel: `top_developed_layouts` (approved projects on this landmark)
    - Last / next 5 years charts: `growth_history`, `growth_prediction`
    - Key amenities: `amenities`
    - Top spots list: `top_spots_to_invest` (same source as investment_landmarks)
    - Upcoming: `upcoming_developments` (title + detail lines)
    - Compare strip: `comparison`
    """
    id: UUID
    landmark_id: UUID
    parent_landmark_id: Optional[UUID] = None
    parent_city: Optional[ParentCityRef] = None
    location_type: Literal["area"] = "area"
    name: str
    city: str
    zone: Optional[str] = Field(None, description="Subheading under welcome — from landmark.zone.")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = Field(
        None,
        description="Area/locality thumbnail from landmark.image_url.",
    )
    market_overview: str = Field(..., description="‘About this landmark market’ body copy.")
    box_content: AreaBoxContentSection
    growth_history: List[Dict[str, Any]]
    growth_prediction: List[Dict[str, Any]]
    amenities: List[str]
    upcoming_developments: List[UpcomingDevelopmentItem]
    top_spots_to_invest: List[Dict[str, Any]] = Field(
        ...,
        description="Nearby micro-markets (name, residential, commercial, rental, growth, etc.).",
    )
    top_developed_layouts: List[AreaDevelopedLayoutPublic]
    comparison: AreaComparisonHintPublic
    created_at: datetime
    updated_at: datetime


class MarketIntelligenceResponse(MarketIntelligenceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
