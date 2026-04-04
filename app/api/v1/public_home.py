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
from app.schemas.city import CityResponse, CityPublicDetailsResponse, LandmarkRichResponse
import logging


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
                image_url=lm.image_url,
                location=lm.location.model_dump() if lm.location else None,
                amenities=amenities
            ))

    # Construct complete response
    response_data = CityPublicDetailsResponse.model_validate(city.model_dump())
    response_data.landmarks = landmarks
    
    return response_data

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
