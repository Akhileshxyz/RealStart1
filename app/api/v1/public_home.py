"""
Public Homepage APIs
====================
1. GET /api/v1/public/featured-cities   → Market Cities for CitySelector / CityOverviewSection
2. GET /api/v1/public/featured-projects → Featured Projects for homepage & Top Projects page
3. GET /api/v1/public/blogs             → Latest / filtered Blogs for BlogSection & /blogs page
"""
from typing import Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from uuid import UUID

from app.models.project import Project, ProjectStatus
from app.models.blog import Blog
from app.models.city import City
from app.models.landmark import Landmark
from beanie.operators import In
from app.schemas.city import (
    CityResponse, 
    CityPublicDetailsResponse, 
    LandmarkRichResponse, 
    LandmarkRichResponse, 
    LandmarkFullPublicResponse
)
from app.schemas.landmark import LandmarkSummary, LandmarkResponse
from app.schemas.landmark_compare import (
    LandmarkCompareResponse, 
    PriceSnapshot, 
    LocationTraits, 
    ComparisonLocation, 
    HistoricalGrowthChart, 
    GrowthDataset, 
    ComparisonConclusion
)
from app.models.market_intelligence import MarketIntelligence
from app.core.redis_client import redis_client
from app.core.config import settings
from app.services.project_service import get_all_projects_for_geospatial
import logging
import math


logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Response schemas (inline – lightweight, purpose-built for the homepage)
# ---------------------------------------------------------------------------

class CityStats(BaseModel):
    avg_price_display: str        # e.g. "₹4,850"
    growth_display: str           # e.g. "+68%"
    projects_count: int
    yield_display: str            # e.g. "3.2%"

class FeaturedCityResponse(BaseModel):
    id: UUID
    name: str
    image: Optional[str] = None

class FeaturedCitiesEnvelope(BaseModel):
    status: str = "success"
    results: int
    data: List[FeaturedCityResponse]



class FeaturedProjectCard(BaseModel):
    id: UUID
    name: str
    slug: str
    location_name: Optional[str] = None   # city field
    price_display: Optional[str] = None   # formatted min_price/sqft
    price_value: Optional[int] = None     # raw min_price integer
    thumbnail_url: Optional[str] = None   # first gallery image

class FeaturedProjectsEnvelope(BaseModel):
    status: str = "success"
    results: int
    data: List[FeaturedProjectCard]

class BlogTheme(BaseModel):
    bg: str = "#1a2230"
    accent: str = "#94a3b8"

class BlogCard(BaseModel):
    id: str
    title: str
    description: str
    date_formatted: str           # "08/04/2025 04:30 PM"
    category: str
    tag: Optional[str] = None
    theme: BlogTheme
    image_url: Optional[str] = None

class BlogsEnvelope(BaseModel):
    status: str = "success"
    results: int
    data: List[BlogCard]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_price(value: Optional[float]) -> Optional[str]:
    """Format a raw price-per-sqft float → '₹4,850'."""
    if value is None:
        return None
    return f"₹{int(value):,}"

def _format_datetime(dt: Optional[datetime]) -> str:
    if dt is None:
        return ""
    return dt.strftime("%d/%m/%Y %I:%M %p")

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Haversine formula to calculate distance between two points on Earth.
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return float('inf')

    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ---------------------------------------------------------------------------
# 1. Featured Cities  →  GET /api/v1/public/featured-cities
# ---------------------------------------------------------------------------

@router.get(
    "/featured-cities",
    response_model=FeaturedCitiesEnvelope,
    tags=["Public - Home"],
    summary="Market Cities for CitySelector / CityOverviewSection",
)
async def list_featured_cities(
    limit: int = Query(10, ge=1, le=50),
) -> Any:
    """
    Returns featured cities from the cities collection.
    Real-time data (No Cache).
    """
    cities = await City.find(City.is_active == True).limit(limit).to_list()

    data: List[FeaturedCityResponse] = [
        FeaturedCityResponse(
            id=city.id,
            name=city.name,
            image=city.images[0] if city.images else None
        )
        for city in cities
    ]

    return {
        "status": "success",
        "results": len(data),
        "data": [d.model_dump() for d in data],
    }

@router.get("/cities/{slug}", response_model=CityPublicDetailsResponse, tags=["Public - Home"])
async def get_city_by_slug(slug: str) -> Any:
    """
    Returns full city details (stats, pricing, infrastructure) based on slug.
    Now includes detailed landmarks.
    """
    city = await City.find_one(City.slug == slug)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    # Fetch detailed landmarks
    landmarks = []
    if city.landmarks_id_list:
        db_landmarks = await Landmark.find(In(Landmark.id, city.landmarks_id_list)).to_list()
        for lm in db_landmarks:
            # Handle amenities (nearby_amenities can be list or dict)
            amenities = []
            if isinstance(lm.nearby_amenities, list):
                amenities = lm.nearby_amenities[:3] # Limit to 2-3
            elif isinstance(lm.nearby_amenities, dict):
                # Flatten dict values if it's categorized
                for val in lm.nearby_amenities.values():
                    if isinstance(val, list):
                        amenities.extend(val)
                amenities = amenities[:3]

            landmarks.append(LandmarkRichResponse(
                id=lm.id,
                name=lm.name,
                image_url=lm.images[0] if lm.images else None,
                location=lm.location.model_dump() if lm.location else None,
                amenities=amenities
            ))

    # Fetch detailed projects
    resolved_projects = []
    if city.top_developed_projects:
        db_projects = await Project.find(In(Project.id, city.top_developed_projects)).to_list()
        for p in db_projects:
            resolved_projects.append(FeaturedProjectCard(
                id=p.id,
                name=p.name,
                slug=p.slug,
                location_name=p.city,
                price_display=_format_price(p.min_price),
                price_value=int(p.min_price) if p.min_price else None,
                thumbnail_url=p.gallery_images[0] if p.gallery_images else None,
            ))

    # Fetch upcoming projects
    resolved_upcoming = []
    if city.upcoming_projects_list:
        db_upcoming = await Project.find(In(Project.id, city.upcoming_projects_list)).to_list()
        for p in db_upcoming:
            resolved_upcoming.append(FeaturedProjectCard(
                id=p.id,
                name=p.name,
                slug=p.slug,
                location_name=p.city,
                price_display=_format_price(p.min_price),
                price_value=int(p.min_price) if p.min_price else None,
                thumbnail_url=p.gallery_images[0] if p.gallery_images else None,
            ))

    # Construct complete response
    response_data = CityPublicDetailsResponse.model_validate(city.model_dump())
    response_data.landmarks = landmarks
    response_data.top_developed_projects = resolved_projects
    response_data.upcoming_projects_list = resolved_upcoming
    
    # Fetch Market Intelligence for deeper insights (Maps, Investment Landmarks)
    # We find the main city landmark first
    city_landmark = await Landmark.find_one(Landmark.name == city.name, Landmark.city_id == city.id)
    if city_landmark:
        intel = await MarketIntelligence.find_one(MarketIntelligence.landmark_id == city_landmark.id)
        if intel:
            response_data.investment_landmarks = intel.investment_landmarks
            response_data.map_landmarks = intel.map_landmarks
    
    return response_data

@router.get(
    "/landmarks",
    response_model=Any,
    tags=["Public - Home"],
    summary="Get Detailed Landmark data or List all Landmarks"
)
async def get_landmarks(
    landmark_id: Optional[UUID] = Query(None, description="The unique ID of the landmark for detailed view"),
    city: Optional[str] = Query(None, description="Filter by city name for list view")
) -> Any:
    """
    Polymorphic endpoint:
    1. If `landmark_id` is provided: Returns full details for Market Intelligence.
    2. If `landmark_id` is NOT provided: Returns a list of landmarks (Summary View).
    """
    if landmark_id:
        # DETAIL VIEW
        landmark = await Landmark.get(landmark_id)
        if not landmark:
            raise HTTPException(status_code=404, detail="Landmark not found")
        
        # Extract landmark coords
        lm_lat, lm_lon = None, None
        if landmark.location and landmark.location.coordinates:
            lm_lon, lm_lat = landmark.location.coordinates
            
        # Fetch all projects from cache
        projects = await get_all_projects_for_geospatial(use_cache=True)
        
        nearby = []
        for proj in projects:
            dist = calculate_distance(lm_lat, lm_lon, proj.latitude, proj.longitude)
            if dist <= 30.0:  # 30 km radius
                nearby.append((dist, proj))
                
        # Sort by distance
        nearby.sort(key=lambda x: x[0])
        
        # Extract projects
        data = landmark.model_dump()
        
        # 1. Resolve Nearby Projects
        # Priority 1: Explicitly curated list from Admin
        # Priority 2: Geospatial fallback (nearest 5 within 30km)
        nearby_projects = []
        if landmark.nearby_project_ids:
            from app.models.project import Project
            fetched_nearby_projs = await Project.find(In(Project.id, landmark.nearby_project_ids)).to_list()
            nearby_projects = [p.model_dump() for p in fetched_nearby_projs]
        
        if not nearby_projects:
            nearby_projects = [item[1].model_dump() for item in nearby[:5]]
            
        data["nearby_projects"] = nearby_projects

        # 2. Resolve Upcoming Projects (Explicit ID list)
        upcoming_projects = []
        if landmark.upcoming_project_ids:
            from app.models.project import Project
            fetched_upcoming = await Project.find(In(Project.id, landmark.upcoming_project_ids)).to_list()
            upcoming_projects = [p.model_dump() for p in fetched_upcoming]
        data["upcoming_projects_list"] = upcoming_projects

        # 3. Resolve Nearby Landmarks (Explicit ID list)
        nearby_landmarks = []
        if landmark.nearby_landmarks_ids:
            fetched_nearby = await Landmark.find(In(Landmark.id, landmark.nearby_landmarks_ids)).to_list()
            nearby_landmarks = [l.model_dump() for l in fetched_nearby]
        data["nearby_landmarks"] = nearby_landmarks
        
        # Validate and return
        landmark_response = LandmarkResponse.model_validate(data)
        return landmark_response

    else:
        # LIST VIEW
        # Try cache first
        if city:
            cache_key = redis_client.make_key("public", "landmarks", "city", city, "summary")
        else:
            cache_key = redis_client.make_key("public", "landmarks", "all", "summary")

        cached = await redis_client.get(cache_key)
        if cached:
            return [LandmarkSummary(**l) for l in cached]

        # Cache miss - query database with projection
        if city:
            landmarks = await Landmark.find(Landmark.city == city).project(LandmarkSummary).to_list()
        else:
            landmarks = await Landmark.find_all().project(LandmarkSummary).to_list()

        # Cache results
        if landmarks:
            landmarks_dict = [l.model_dump() for l in landmarks]
            ttl = getattr(settings, 'REDIS_CACHE_TTL_LANDMARKS', 21600)
            await redis_client.set(cache_key, landmarks_dict, ttl)

        return landmarks

@router.get(
    "/landmarks/compare",
    response_model=LandmarkCompareResponse,
    tags=["Public - Home"],
    summary="Compare two landmarks for market intelligence"
)
async def compare_landmarks(
    base_id: UUID = Query(..., description="The ID of the base landmark"),
    target_id: UUID = Query(..., description="The ID of the target landmark to compare against")
) -> Any:
    """
    Compares two landmarks across various dimensions: price snapshots, traits, 
    historical growth, and provides a data-driven investment/end-user conclusion.
    """
    base_lm = await Landmark.get(base_id)
    target_lm = await Landmark.get(target_id)
    
    if not base_lm or not target_lm:
        raise HTTPException(status_code=404, detail="One or both landmarks not found")

    # Fetch Market Intelligence for deeper data
    base_mi = await MarketIntelligence.find_one(MarketIntelligence.landmark_id == base_id)
    target_mi = await MarketIntelligence.find_one(MarketIntelligence.landmark_id == target_id)

    def generate_location_data(lm: Landmark, mi: Optional[MarketIntelligence]):
        # Traits Logic (Derived from stats)
        rental_val = lm.rental_yield.replace("%", "").strip() if lm.rental_yield else "0"
        try:
            rental_yield_float = float(rental_val)
        except ValueError:
            rental_yield_float = 0.0

        traits = LocationTraits(
            rental="High" if rental_yield_float > 4.5 else "Moderate",
            growth="Aggressive" if lm.price_trend == "rising" else "Stable",
            family="Superior" if len(lm.nearby_amenities or []) > 5 else "Moderate",
            traffic="Moderate", # Default for now
            social="Excellent" if len(lm.nearby_amenities or []) > 3 else "Good"
        )

        # Price Snapshot Logic
        res_price = mi.avg_residential_plot_price if mi else lm.avg_plot_price
        comm_price = mi.avg_commercial_plot_price if mi else lm.avg_plot_price * 1.5
        appreciation = mi.appreciation_potential_5yr if mi else "+35%"
        
        # Formatting values: e.g. "₹8,500 - ₹12,000"
        price_snapshot = PriceSnapshot(
            residential_land=f"₹{int(res_price):,} - ₹{int(res_price * 1.3):,}",
            commercial_land=f"₹{int(comm_price):,} - ₹{int(comm_price * 1.2):,}",
            rental_rent=lm.residential_rent_2bhk or "₹15,000 - ₹20,000",
            appreciation_5yr=appreciation
        )

        return ComparisonLocation(
            id=lm.id,
            name=lm.name,
            zone=lm.zone or "Central",
            image_url=lm.images[0] if lm.images else None,
            price_snapshot=price_snapshot,
            traits=traits
        )

    base_location = generate_location_data(base_lm, base_mi)
    target_location = generate_location_data(target_lm, target_mi)

    # Chart Processing
    # Combining labels (years)
    base_growth = {p.year: p.value for p in base_lm.price_growth}
    target_growth = {p.year: p.value for p in target_lm.price_growth}
    
    all_years = sorted(list(set(base_growth.keys()) | set(target_growth.keys())))
    if not all_years:
        all_years = [datetime.now().year - i for i in range(5, -1, -1)]
        all_years = [str(y) for y in all_years]
    else:
        all_years = [str(y) for y in all_years]

    base_data = [base_growth.get(int(y), 0) for y in all_years]
    target_data = [target_growth.get(int(y), 0) for y in all_years]

    historical_growth_chart = HistoricalGrowthChart(
        labels=all_years,
        datasets=[
            GrowthDataset(label=base_lm.name, data=base_data),
            GrowthDataset(label=target_lm.name, data=target_data)
        ]
    )

    # Conclusion Logic
    # 1. Best for investors: Higher appreciation value
    try:
        base_appr = float(base_location.price_snapshot.appreciation_5yr.replace("+", "").replace("%", ""))
        target_appr = float(target_location.price_snapshot.appreciation_5yr.replace("+", "").replace("%", ""))
    except ValueError:
        base_appr = target_appr = 0

    best_inv = base_lm.name if base_appr >= target_appr else target_lm.name
    best_end = base_lm.name if base_location.traits.family == "Superior" or base_location.traits.social == "Excellent" else target_lm.name

    conclusion = ComparisonConclusion(
        best_for_investors=best_inv,
        best_for_end_users=best_end,
        guidance_investor=f"Higher appreciation potential of {max(base_appr, target_appr)}% in {best_inv} makes it preferred for capital gains.",
        guidance_end_user=f"{best_end} offers superior social infrastructure and established rental market for families."
    )

    # Fetch Nearby Landmarks for the Base ID (to match detailed view behavior)
    nearby_landmarks = []
    if base_lm.nearby_landmarks_ids:
        fetched_nearby = await Landmark.find(In(Landmark.id, base_lm.nearby_landmarks_ids)).to_list()
        nearby_landmarks = [l.model_dump() for l in fetched_nearby]

    return {
        "base_location": base_location,
        "target_location": target_location,
        "historical_growth_chart": historical_growth_chart,
        "conclusion": conclusion,
        "nearby_landmarks": nearby_landmarks
    }

# ---------------------------------------------------------------------------
# 2. Featured Projects  →  GET /api/v1/public/featured-projects
# ---------------------------------------------------------------------------

@router.get(
    "/featured-projects",
    response_model=FeaturedProjectsEnvelope,
    tags=["Public - Home"],
    summary="Featured Projects for homepage & Top Projects page",
)
async def list_featured_projects(
    limit: int = Query(6, ge=1, le=50),
) -> Any:
    """
    Returns APPROVED, non-hidden projects flagged as `is_featured=True`.
    Real-time data (No Cache).
    """
    projects = await Project.find(
        Project.is_featured == True,
        Project.status == ProjectStatus.APPROVED,
        Project.is_hidden == False,
        Project.is_active == True,
    ).limit(limit).to_list()

    data = [
        FeaturedProjectCard(
            id=p.id,
            name=p.name,
            slug=p.slug,
            location_name=p.city,
            price_display=_format_price(p.min_price),
            price_value=int(p.min_price) if p.min_price else None,
            thumbnail_url=p.gallery_images[0] if p.gallery_images else None,
        )
        for p in projects
    ]

    return {
        "status": "success",
        "results": len(data),
        "data": [d.model_dump() for d in data],
    }

# ---------------------------------------------------------------------------
# 3. Blogs  →  GET /api/v1/public/blogs
# ---------------------------------------------------------------------------

@router.get(
    "/blogs",
    response_model=BlogsEnvelope,
    tags=["Public - Home"],
    summary="Latest Blogs for BlogSection & /blogs page",
)
async def list_blogs(
    limit: int = Query(3, ge=1, le=50),
    category: Optional[str] = Query(None, description="Filter by category e.g. 'Commercial'"),
) -> Any:
    """
    Returns published blogs sorted by published_at descending.
    Real-time data (No Cache).
    """
    query = Blog.find(Blog.is_published == True)
    if category:
        query = query.find(Blog.category == category)

    blogs = await query.sort(-Blog.published_at).limit(limit).to_list()

    data = [
        BlogCard(
            id=str(b.id),
            title=b.title,
            description=b.description,
            date_formatted=_format_datetime(b.published_at or b.created_at),
            category=b.category,
            tag=b.tag,
            theme=BlogTheme(
                bg=b.bg_color or "#1a2230",
                accent=b.accent_color or "#94a3b8",
            ),
            image_url=b.image_url,
        )
        for b in blogs
    ]

    return {
        "status": "success",
        "results": len(data),
        "data": [d.model_dump() for d in data],
    }
