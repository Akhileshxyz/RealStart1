"""
Public Homepage APIs
====================
1. GET /api/v1/public/featured-cities   → Market Cities for CitySelector / CityOverviewSection
2. GET /api/v1/public/featured-projects → Featured Projects for homepage & Top Projects page
3. GET /api/v1/public/blogs             → Latest / filtered Blogs for BlogSection & /blogs page
"""
from typing import Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Query
from pydantic import BaseModel
from uuid import UUID

from app.models.landmark import Landmark
from app.models.market_intelligence import MarketIntelligence
from app.models.project import Project, ProjectStatus
from app.models.blog import Blog
from app.core.redis_client import redis_client

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
    landmark_id: UUID
    name: str
    image_url: Optional[str] = None
    appreciation_potential: str   # e.g. "+15%"
    stats: CityStats


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
    Returns city-level landmarks joined with their MarketIntelligence record
    to build the homepage CitySelector and CityOverviewSection components.

    Cached for 1 hour (TIER 1).
    """
    cache_key = redis_client.make_key("public", "featured_cities", str(limit))
    cached = await redis_client.get(cache_key)
    if cached:
        return cached

    # Fetch all landmarks that are city-type (have market intelligence records)
    mi_records = await MarketIntelligence.find(
        MarketIntelligence.location_type == "city"
    ).limit(limit).to_list()

    data: List[FeaturedCityResponse] = []

    for mi in mi_records:
        # Pull the landmark for name + image
        landmark = await Landmark.get(mi.landmark_id)
        if not landmark:
            continue

        # Count approved projects linked to this landmark
        projects_count = await Project.find(
            Project.landmark_id == mi.landmark_id,
            Project.status == ProjectStatus.APPROVED,
            Project.is_hidden == False,
        ).count()

        # Build stats - avg_price_per_sqft from Landmark, growth from MI
        avg_price = landmark.avg_price_per_sqft
        growth_5yr = landmark.growth_forecast_5yr  # stored as float e.g. 68.0

        stats = CityStats(
            avg_price_display=f"₹{int(avg_price):,}" if avg_price else "N/A",
            growth_display=f"+{growth_5yr:.0f}%" if growth_5yr else mi.appreciation_potential_5yr,
            projects_count=projects_count,
            yield_display="N/A",  # Not stored yet; extend Landmark model when available
        )

        data.append(FeaturedCityResponse(
            landmark_id=mi.landmark_id,
            name=landmark.name,
            image_url=landmark.image_url,
            appreciation_potential=mi.appreciation_potential_5yr,
            stats=stats,
        ))

    result = {
        "status": "success",
        "results": len(data),
        "data": [d.model_dump() for d in data],
    }

    # Cache 1 hour
    await redis_client.set(cache_key, result, 3600)

    return result


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
    Cached for 30 minutes (TIER 2).
    """
    cache_key = redis_client.make_key("public", "featured_projects", str(limit))
    cached = await redis_client.get(cache_key)
    if cached:
        return cached

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

    result = {
        "status": "success",
        "results": len(data),
        "data": [d.model_dump() for d in data],
    }

    # Cache 30 minutes
    await redis_client.set(cache_key, result, 1800)

    return result


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
    Cached for 15 minutes (TIER 2).
    """
    cache_key = redis_client.make_key("public", "blogs", str(limit), category or "all")
    cached = await redis_client.get(cache_key)
    if cached:
        return cached

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

    result = {
        "status": "success",
        "results": len(data),
        "data": [d.model_dump() for d in data],
    }

    # Cache 15 minutes
    await redis_client.set(cache_key, result, 900)

    return result
