from typing import Any, List, Dict, Optional, Tuple
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from pydantic import BaseModel
from app.api import deps
from app.models.landmark import Landmark
from app.models.market_intelligence import MarketIntelligence
from app.schemas.market_intelligence import (
    MarketCityListItem,
    MarketAreaSummary,
    MarketIntelligenceDetailPublic,
    MarketIntelligenceAreaDetailPublic,
    BoxContentSection,
    AreaBoxContentSection,
    ParentCityRef,
    UpcomingDevelopmentItem,
    AreaDevelopedLayoutPublic,
    AreaComparisonHintPublic,
)
from app.models.review import Review, ReviewEntityType
from app.models.project import Project, ProjectStatus
from app.core.config import settings
from datetime import datetime
import httpx
import logging
from app.utils.cache import cache_public_data
from app.utils.json_sanitize import sanitize_json, sanitize_map_landmarks, sanitize_str
from app.utils.media import public_image_url

logger = logging.getLogger(__name__)

router = APIRouter()


def lat_lng_from_landmark(landmark: Landmark) -> Tuple[Optional[float], Optional[float]]:
    """Prefer explicit latitude/longitude; else GeoJSON Point coordinates [lng, lat]."""
    if landmark.latitude is not None and landmark.longitude is not None:
        return landmark.latitude, landmark.longitude
    loc = landmark.location
    if loc and loc.coordinates and len(loc.coordinates) >= 2:
        return loc.coordinates[1], loc.coordinates[0]
    return None, None


async def _area_summaries_for_city(city_landmark_id: UUID) -> List[MarketAreaSummary]:
    rows: List[MarketAreaSummary] = []
    intelligence_list = await MarketIntelligence.find(
        MarketIntelligence.parent_landmark_id == city_landmark_id
    ).to_list()
    for intel in intelligence_list:
        lm = await Landmark.get(intel.landmark_id)
        if not lm:
            continue
        lat, lng = lat_lng_from_landmark(lm)
        ov = sanitize_str(intel.overview)
        short = ov[:150] + "..." if len(ov) > 150 else ov
        rows.append(
            MarketAreaSummary(
                landmark_id=intel.landmark_id,
                parent_landmark_id=intel.parent_landmark_id or city_landmark_id,
                name=sanitize_str(lm.name),
                city=sanitize_str(lm.city),
                overview=short,
                appreciation_potential=sanitize_str(intel.appreciation_potential_5yr),
                latitude=lat,
                longitude=lng,
                image_url=public_image_url(getattr(lm, "image_url", None)),
            )
        )
    return rows

def _sanitize_amenities(amenities: Any) -> List[Dict[str, Any]]:
    # logger.debug(f"Sanitizing amenities: {amenities}")
    if not amenities:
        return []
    
    # If it's a string, try to parse it as JSON or treat as single item list
    # raise Exception(f"DEBUG: amenities type is {type(amenities)} value {amenities}")
    items = []
    if isinstance(amenities, str):
        try:
            import json
            parsed = json.loads(amenities)
            items = parsed if isinstance(parsed, list) else [str(parsed)]
        except:
            items = [amenities]
    elif isinstance(amenities, list):
        items = amenities
    else:
        items = []

    out = []
    for a in items:
        if isinstance(a, str):
            out.append({"name": sanitize_str(a), "icon_url": "/icons/star.svg"})
        elif isinstance(a, dict):
            # Ensure it has icon_url key
            res = dict(a)
            if not res.get("icon_url"):
                res["icon_url"] = "/icons/star.svg"
            out.append(res)
    
    return out


def _detail_public(
    intel: MarketIntelligence,
    landmark: Landmark,
    areas: Optional[List[MarketAreaSummary]] = None,
    parent_city: Optional[ParentCityRef] = None,
) -> MarketIntelligenceDetailPublic:
    lat, lng = lat_lng_from_landmark(landmark)
    box = BoxContentSection(
        avg_commercial_plot_price=float(intel.avg_commercial_plot_price),
        avg_residential_plot_price=float(intel.avg_residential_plot_price),
        avg_rental_2bhk=float(intel.avg_rental_2bhk),
        avg_rental_yield=getattr(intel, 'avg_rental_yield', None),
        economic_output=sanitize_str(intel.economic_output),
        population=sanitize_str(intel.population),
        appreciation_potential_5yr=sanitize_str(intel.appreciation_potential_5yr),
    )
    overview = sanitize_str(intel.overview)
    return MarketIntelligenceDetailPublic(
        id=intel.id,
        landmark_id=intel.landmark_id,
        parent_landmark_id=intel.parent_landmark_id,
        parent_city=parent_city,
        location_type=sanitize_str(intel.location_type),
        name=sanitize_str(landmark.name),
        city=sanitize_str(landmark.city),
        latitude=lat,
        longitude=lng,
        report_download_url=getattr(intel, 'report_download_url', None),
        expert_contact_id=getattr(intel, 'expert_contact_id', None),
        image_url=public_image_url(getattr(landmark, "image_url", None)),
        market_overview=overview,
        box_content=box,
        growth_history=sanitize_json(intel.growth_history) or [],
        growth_prediction=sanitize_json(intel.growth_prediction) or [],
        political_agenda=sanitize_json(intel.political_agenda) or {},
        amenities=_sanitize_amenities(sanitize_json(intel.amenities) or []),
        upcoming_projects=sanitize_json(intel.upcoming_projects) or [],
        investment_landmarks=sanitize_json(intel.investment_landmarks) or [],
        map_landmarks=sanitize_map_landmarks(intel.map_landmarks),
        created_at=intel.created_at,
        updated_at=intel.updated_at,
        areas=areas,
    )


def _upcoming_strings_to_items(lines: List[Any]) -> List[UpcomingDevelopmentItem]:
    out: List[UpcomingDevelopmentItem] = []
    for raw in lines:
        s = sanitize_str(raw)
        if not s:
            continue
        if " - " in s:
            a, b = s.split(" - ", 1)
            out.append(UpcomingDevelopmentItem(title=a.strip(), detail=b.strip()))
        else:
            out.append(UpcomingDevelopmentItem(title=s, detail=None))
    return out


async def _area_top_developed_layouts(landmark_id: UUID) -> List[AreaDevelopedLayoutPublic]:
    projects = await Project.find(
        Project.landmark_id == landmark_id,
        Project.status == ProjectStatus.APPROVED,
        Project.is_hidden == False,
    ).limit(15).to_list()
    cards: List[AreaDevelopedLayoutPublic] = []
    for p in projects:
        cover = p.gallery_images[0] if p.gallery_images else None
        badge = None
        if p.approval_type is not None:
            badge = getattr(p.approval_type, "value", str(p.approval_type))
        loc = (p.address or p.landmark or "").strip()
        cards.append(
            AreaDevelopedLayoutPublic(
                project_id=p.id,
                name=sanitize_str(p.name),
                slug=sanitize_str(p.slug),
                cover_image=cover,
                min_price=p.min_price,
                max_price=p.max_price,
                approval_badge=badge,
                location_hint=sanitize_str(loc) if loc else None,
            )
        )
    return cards


async def build_market_intelligence_area_detail(
    intelligence: MarketIntelligence,
    landmark: Landmark,
    parent_city: Optional[ParentCityRef],
) -> MarketIntelligenceAreaDetailPublic:
    """Response shape for GET .../market-intelligence/areas/{landmark_id} only."""
    lat, lng = lat_lng_from_landmark(landmark)
    overview = sanitize_str(intelligence.overview)
    area_box = AreaBoxContentSection(
        avg_commercial_plot_price=float(intelligence.avg_commercial_plot_price),
        avg_residential_plot_price=float(intelligence.avg_residential_plot_price),
        avg_rental_2bhk=float(intelligence.avg_rental_2bhk),
        avg_rental_yield=getattr(intelligence, 'avg_rental_yield', None),
        appreciation_potential_5yr=sanitize_str(intelligence.appreciation_potential_5yr),
    )
    upcoming_raw = sanitize_json(intelligence.upcoming_projects) or []
    upcoming_list = upcoming_raw if isinstance(upcoming_raw, list) else []
    upcoming_items = _upcoming_strings_to_items(upcoming_list)

    layouts = await _area_top_developed_layouts(landmark.id)
    comparison = AreaComparisonHintPublic(
        current_label=sanitize_str(landmark.name),
        price_per_sqft_hint=landmark.avg_price_per_sqft,
        parent_city_landmark_id=intelligence.parent_landmark_id,
    )
    z = landmark.zone
    zone_val = sanitize_str(z) if z else None
    if zone_val == "":
        zone_val = None

    return MarketIntelligenceAreaDetailPublic(
        id=intelligence.id,
        landmark_id=intelligence.landmark_id,
        parent_landmark_id=intelligence.parent_landmark_id,
        parent_city=parent_city,
        name=sanitize_str(landmark.name),
        city=sanitize_str(landmark.city),
        zone=zone_val,
        latitude=lat,
        longitude=lng,
        report_download_url=getattr(intelligence, 'report_download_url', None),
        expert_contact_id=getattr(intelligence, 'expert_contact_id', None),
        image_url=public_image_url(getattr(landmark, "image_url", None)),
        market_overview=overview,
        box_content=area_box,
        growth_history=sanitize_json(intelligence.growth_history) or [],
        growth_prediction=sanitize_json(intelligence.growth_prediction) or [],
        amenities=_sanitize_amenities(sanitize_json(intelligence.amenities) or []),
        upcoming_developments=upcoming_items,
        top_spots_to_invest=sanitize_json(intelligence.investment_landmarks) or [],
        top_developed_layouts=layouts,
        comparison=comparison,
        created_at=intelligence.created_at,
        updated_at=intelligence.updated_at,
    )


# --- Schemas ---

class LocationResolveRequest(BaseModel):
    place_name: str
    latitude: float
    longitude: float

class LocationResolveResponse(BaseModel):
    landmark_id: UUID
    name: str
    city: str
    message: str

class ReviewCreate(BaseModel):
    entity_id: UUID
    rating: float
    content: str
    entity_type: ReviewEntityType = ReviewEntityType.LANDMARK

# --- Mappls Helper ---
async def get_mappls_token():
    """Exchange Client ID/Secret for Access Token"""
    if not settings.MAPPLS_CLIENT_ID or not settings.MAPPLS_CLIENT_SECRET:
        return None
        
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                settings.MAPPLS_AUTH_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": settings.MAPPLS_CLIENT_ID,
                    "client_secret": settings.MAPPLS_CLIENT_SECRET
                }
            )
            data = resp.json()
            return data.get("access_token")
        except Exception as e:
            logger.error(f"Failed to get Mappls token: {e}")
            return None

async def reverse_geocode_mappls(lat: float, lng: float) -> Dict[str, Any]:
    """Call Mappls Reverse Geocoding API"""
    token = await get_mappls_token()
    if not token:
        return None
        
    url = f"{settings.MAPPLS_BASE_URL}/places/reverse?lat={lat}&lng={lng}"
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                # Assuming standard Mappls response structure (usually 'places' list)
                places = data.get("places", [])
                if places:
                    return places[0] # Return best match
        except Exception as e:
            logger.error(f"Mappls Reverse Geo failed: {e}")
            return None
    return None

async def forward_geocode_mappls(query: str) -> Optional[Dict[str, Any]]:
    """Call Mappls AutoComplete/Geocoding API to get lat/lng from address"""
    token = await get_mappls_token()
    if not token or not query:
        return None
        
    # Use Atlas Search/Auto-suggest API
    url = f"{settings.MAPPLS_BASE_URL}/atlas/all?query={query}"
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                # Returns list of suggested places
                suggested_locations = data.get("suggestedLocations", [])
                if suggested_locations:
                    best_match = suggested_locations[0]
                    # Atlas API returns 'latitude' and 'longitude' directly usually
                    # Or sometimes 'eLoc' which needs another call. 
                    # Assuming basic response has lat/lng or similar
                    return {
                        "latitude": best_match.get("latitude"),
                        "longitude": best_match.get("longitude"),
                        "formatted_address": best_match.get("placeName") or best_match.get("placeAddress")
                    }
        except Exception as e:
            logger.error(f"Mappls Forward Geo failed: {e}")
            return None
    return None

# --- 1. Resolver API ---

@router.post("/resolve", response_model=LocationResolveResponse)
async def resolve_location(
    data: LocationResolveRequest
) -> Any:
    """
    Step 1: Resolve Mappls coordinates/place to a backend Landmark ID.
    Logic: Find nearest existing landmark or return a 'found' one.
    For this implementation, we try to match by name or return a mock if not found (or create one).
    """
    # 1. Try to find by name first (exact match)
    landmark = await Landmark.find_one({"name": data.place_name})
    
    # 2. If not found, try geospatial lookup (nearest point)
    # Note: Requires 2dsphere index to work effectively.
    if not landmark:
        # Pymongo/Beanie geo query
        landmark = await Landmark.find_one({
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [data.longitude, data.latitude]
                    },
                    "$maxDistance": 2000 # 2km radius
                }
            }
        })

    if landmark:
        return {
            "landmark_id": landmark.id,
            "name": landmark.name,
            "city": landmark.city,
            "message": "Resolved to existing landmark"
        }
    else:
        # Use Mappls Real Data if available
        mappls_data = await reverse_geocode_mappls(data.latitude, data.longitude)
        
        city_name = "Bangalore"
        zone_name = None
        
        if mappls_data:
            # Extract real info from Mappls
            # Note: Mapping depends on exact Mappls response keys (city, district, locality)
            # This is a safe approximation based on standard responses
            address = mappls_data.get("address", {}) # or flattened keys
            city_name = mappls_data.get("city") or mappls_data.get("district") or "Bangalore"
            zone_name = mappls_data.get("subDistrict")
            # If place name wasn't provided well, update it
            if not data.place_name or data.place_name == "Selected Location":
                data.place_name = mappls_data.get("formatted_address", "New Location")

        new_landmark = Landmark(
            name=data.place_name,
            city=city_name,
            zone=zone_name,
            location={"type": "Point", "coordinates": [data.longitude, data.latitude]},
            latitude=data.latitude,
            longitude=data.longitude,
            description="Auto-generated from map selection"
        )
        await new_landmark.save()
        
        return {
            "landmark_id": new_landmark.id,
            "name": new_landmark.name,
            "city": new_landmark.city,
            "message": "Created new landmark (Mappls Enriched)" if mappls_data else "Created new landmark (Fallback)"
        }

# --- 2. Market Intelligence API ---

@router.get("/market-intelligence", response_model=List[MarketCityListItem])
@cache_public_data(ttl=settings.REDIS_CACHE_TTL_LANDMARKS)
async def list_market_intelligence_public() -> Any:
    """
    Cities with market intelligence first (note: city-level block).
    Optional lat/lng from landmark when present for map center.
    """
    intelligence_list = await MarketIntelligence.find(MarketIntelligence.location_type == "city").to_list()
    enriched: List[MarketCityListItem] = []
    for intel in intelligence_list:
        landmark = await Landmark.get(intel.landmark_id)
        if not landmark:
            continue
        lat, lng = lat_lng_from_landmark(landmark)
        ov_full = sanitize_str(intel.overview)
        ov = ov_full[:150] + "..." if len(ov_full) > 150 else ov_full
        enriched.append(
            MarketCityListItem(
                landmark_id=intel.landmark_id,
                name=sanitize_str(landmark.name),
                city=sanitize_str(landmark.city),
                overview=ov,
                appreciation_potential=sanitize_str(intel.appreciation_potential_5yr),
                latitude=lat,
                longitude=lng,
                image_url=public_image_url(getattr(landmark, "image_url", None)),
            )
        )
    return enriched

@router.get("/market-intelligence/{landmark_id}", response_model=MarketIntelligenceDetailPublic)
@cache_public_data(ttl=settings.REDIS_CACHE_TTL_LANDMARKS)
async def get_market_intelligence_public(
    landmark_id: UUID,
    include_areas: bool = Query(
        True,
        description="When true and this row is a city, include sub-area summaries (names + optional lat/lng).",
    ),
) -> Any:
    """
    City or area detail aligned with note sections: overview, box_content, history, prediction, agenda, amenities, projects, investment landmarks, map_landmarks.
    For cities, set include_areas=false to omit the embedded area list (saves payload size).
    """
    intelligence = await MarketIntelligence.find_one(
        MarketIntelligence.landmark_id == landmark_id
    )
    if not intelligence:
        raise HTTPException(
            status_code=404,
            detail="Market intelligence not found for this locality",
        )
    landmark = await Landmark.get(landmark_id)
    if not landmark:
        raise HTTPException(status_code=404, detail="Landmark not found")

    areas: Optional[List[MarketAreaSummary]] = None
    if include_areas and intelligence.location_type == "city":
        areas = await _area_summaries_for_city(landmark_id)

    parent_city: Optional[ParentCityRef] = None
    if intelligence.location_type == "area" and intelligence.parent_landmark_id:
        pl = await Landmark.get(intelligence.parent_landmark_id)
        if pl:
            parent_city = ParentCityRef(
                landmark_id=pl.id,
                name=sanitize_str(pl.name),
                city=sanitize_str(pl.city),
                image_url=public_image_url(getattr(pl, "image_url", None)),
            )

    return _detail_public(
        intelligence, landmark, areas=areas, parent_city=parent_city
    )


@router.get(
    "/market-intelligence/areas/{landmark_id}",
    response_model=MarketIntelligenceAreaDetailPublic,
)
@cache_public_data(ttl=settings.REDIS_CACHE_TTL_LANDMARKS)
async def get_market_intelligence_area_detail_public(landmark_id: UUID) -> Any:
    """
    Area Market Intelligence screen only: welcome + zone, about, stat grid, layouts carousel,
    charts, amenities, top spots, upcoming (title/detail), compare hint. Not the same shape as city GET.
    """
    intelligence = await MarketIntelligence.find_one(
        MarketIntelligence.landmark_id == landmark_id
    )
    if not intelligence:
        raise HTTPException(
            status_code=404,
            detail="Market intelligence not found for this locality",
        )
    if intelligence.location_type != "area":
        raise HTTPException(
            status_code=404,
            detail="Not an area market intelligence record; use GET /market-intelligence/{landmark_id} for city detail",
        )
    landmark = await Landmark.get(landmark_id)
    if not landmark:
        raise HTTPException(status_code=404, detail="Landmark not found")

    parent_city: Optional[ParentCityRef] = None
    if intelligence.parent_landmark_id:
        pl = await Landmark.get(intelligence.parent_landmark_id)
        if pl:
            parent_city = ParentCityRef(
                landmark_id=pl.id,
                name=sanitize_str(pl.name),
                city=sanitize_str(pl.city),
                image_url=public_image_url(getattr(pl, "image_url", None)),
            )

    return await build_market_intelligence_area_detail(
        intelligence, landmark, parent_city
    )


# --- 3. Canonical Details API ---

@router.get("/{landmark_id}", response_model=Any)
@cache_public_data(ttl=settings.REDIS_CACHE_TTL_LANDMARKS)
async def get_locality_details(landmark_id: UUID) -> Any:
    """
    Master API for static locality details.
    """
    landmark = await Landmark.get(landmark_id)
    if not landmark:
        raise HTTPException(status_code=404, detail="Landmark not found")
    
    # Calculate avg rating
    reviews = await Review.find(
        Review.entity_id == landmark_id,
        Review.entity_type == ReviewEntityType.LANDMARK
    ).to_list()
    
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0.0
    
    return {
        "id": landmark.id,
        "name": landmark.name,
        "city": landmark.city,
        "zone": landmark.zone,
        "description": landmark.description,
        "location": landmark.location,
        "image_url": public_image_url(getattr(landmark, "image_url", None)),
        "rating": round(avg_rating, 1),
        "review_count": len(reviews),
        "about_text": f"A prime residential area in {landmark.city} with great connectivity."
    }

# --- 3. Sub-APIs ---

@router.get("/transactions", response_model=Any)
@cache_public_data()
async def get_registry_transactions(landmark_id: UUID = Query(...)) -> Any:
    """
    Mock registry transactions.
    """
    # In real world: fetch from Registry/Transaction database
    return {
        "total_registrations": 450,
        "recent_transactions": [
            {"date": "2025-11-15", "price": "1.2 Cr", "property_type": "3 BHK Apartment"},
            {"date": "2025-11-10", "price": "85 L", "property_type": "Plot (1200 sqft)"}
        ]
    }

@router.get("/price-insights", response_model=Any)
@cache_public_data(ttl=settings.REDIS_CACHE_TTL_LANDMARKS)
async def get_price_insights(landmark_id: UUID = Query(...)) -> Any:
    """
    Mock price insights.
    """
    landmark = await Landmark.get(landmark_id)
    if not landmark:
         raise HTTPException(status_code=404, detail="Landmark not found")
         
    base_price = landmark.avg_price_per_sqft or 5500
    
    return {
        "summary": {
            "avg_price_per_sqft": base_price,
            "price_range": f"{base_price-500}-{base_price+500}",
            "year_on_year_growth": "+8.5%"
        },
        "by_bhk": {
            "1 BHK": {"min": "45L", "max": "55L", "avg": "50L"},
            "2 BHK": {"min": "75L", "max": "90L", "avg": "82L"},
            "3 BHK": {"min": "1.1Cr", "max": "1.5Cr", "avg": "1.3Cr"}
        }
    }

@router.get("/trends", response_model=Any)
@cache_public_data(ttl=settings.REDIS_CACHE_TTL_LANDMARKS)
async def get_market_trends(landmark_id: UUID = Query(...)) -> Any:
    """
    Mock market trends (graphs).
    """
    return {
        "price_trend_5y": [
            {"year": 2021, "price": 4500},
            {"year": 2022, "price": 4800},
            {"year": 2023, "price": 5200},
            {"year": 2024, "price": 5800},
            {"year": 2025, "price": 6200}
        ],
        "supply_demand_ratio": {
            "supply": 60,
            "demand": 85  # High demand
        }
    }

# --- Projects & Properties ---

@router.get("/projects", response_model=List[Any])
@cache_public_data()
async def get_locality_projects(landmark_id: UUID = Query(...)) -> Any:
    """
    Fetch projects linked to this locality.
    """
    projects = await Project.find(
        Project.landmark_id == landmark_id,
        Project.status == ProjectStatus.APPROVED
    ).to_list()
    return projects

@router.get("/societies", response_model=List[Any])
@cache_public_data()
async def get_linked_societies(landmark_id: UUID = Query(...)) -> Any:
    """
    Same as projects but maybe filtered by layout type?
    For now alias to projects.
    """
    projects = await Project.find(
        Project.landmark_id == landmark_id,
        Project.status == ProjectStatus.APPROVED
    ).to_list()
    return projects

@router.get("/properties/buy", response_model=List[Any])
@cache_public_data(ttl=300) # 5 mins for inventory
async def get_properties_buy(landmark_id: UUID = Query(...)) -> Any:
    """
    Mock property listings (Inventory).
    """
    # Assuming inventory logic linked to projects
    return [
        {"id": "inv_1", "title": "2 BHK Premium", "price": "85L", "project_name": "Residency 1"},
        {"id": "inv_2", "title": "3 BHK Luxury", "price": "1.2Cr", "project_name": "Residency 1"},
    ]

@router.get("/properties/rent", response_model=List[Any])
@cache_public_data(ttl=300)
async def get_properties_rent(landmark_id: UUID = Query(...)) -> Any:
    """
    Mock rental listings.
    """
    return []

# --- Reviews ---

@router.post("/reviews", response_model=Any)
async def create_review(
    review_in: ReviewCreate,
    current_user: Any = Depends(deps.get_current_user)
) -> Any:
    """
    Create a review for a locality.
    """
    review = Review(
        entity_id=review_in.entity_id,
        entity_type=review_in.entity_type,
        user_id=current_user.id,
        rating=review_in.rating,
        content=review_in.content
    )
    await review.insert()
    return review

@router.get("/reviews/locality", response_model=List[Any])
@cache_public_data()
async def get_locality_reviews(landmark_id: UUID = Query(...)) -> Any:
    """
    Get reviews for a locality.
    """
    reviews = await Review.find(
        Review.entity_id == landmark_id,
        Review.entity_type == ReviewEntityType.LANDMARK
    ).sort("-created_at").to_list()
    return reviews

@router.get("/reviews/ratings-summary", response_model=Any)
@cache_public_data()
async def get_rating_summary(landmark_id: UUID = Query(...)) -> Any:
    """
    Get rating summary.
    """
    reviews = await Review.find(
        Review.entity_id == landmark_id,
        Review.entity_type == ReviewEntityType.LANDMARK
    ).to_list()
    
    total = len(reviews)
    if total == 0:
        return {"avg_rating": 0, "total_reviews": 0, "distribution": {}}
        
    avg = sum(r.rating for r in reviews) / total
    return {
        "avg_rating": round(avg, 1),
        "total_reviews": total,
        "distribution": {
            "5": len([r for r in reviews if r.rating == 5]),
            "4": len([r for r in reviews if r.rating == 4]),
            "3": len([r for r in reviews if r.rating == 3]),
            "2": len([r for r in reviews if r.rating == 2]),
            "1": len([r for r in reviews if r.rating == 1]),
        }
    }

# --- Nearby Areas (Geospatial) ---

@router.get("/nearby-areas", response_model=List[Any])
@cache_public_data(ttl=settings.REDIS_CACHE_TTL_LANDMARKS)
async def get_nearby_areas(landmark_id: UUID = Query(...)) -> Any:
    """
    Get nearby landmarks using geospatial query.
    """
    landmark = await Landmark.get(landmark_id)
    if not landmark or not landmark.location:
        return []
        
    # Find landmarks within 5km
    nearby = await Landmark.find({
        "location": {
            "$near": {
                "$geometry": landmark.location.model_dump(),
                "$maxDistance": 5000 
            }
        },
        "_id": {"$ne": landmark.id} # Exclude self
    }).limit(10).to_list()
    
    return [
        {"id": n.id, "name": n.name, "distance_meters": "Calculated by Aggregation in real app"} 
        for n in nearby
    ]

# --- Demand & Supply ---

@router.get("/demand/overview", response_model=Any)
@cache_public_data(ttl=settings.REDIS_CACHE_TTL_LANDMARKS)
async def get_demand_overview(landmark_id: UUID = Query(...)) -> Any:
    """
    Mock Demand Overview.
    """
    return {
        "search_volume": "High",
        "rank_in_city": 5,
        "most_searched_config": "3 BHK"
    }

@router.get("/supply/overview", response_model=Any)
@cache_public_data(ttl=settings.REDIS_CACHE_TTL_LANDMARKS)
async def get_supply_overview(landmark_id: UUID = Query(...)) -> Any:
    """
    Mock Supply Overview.
    """
    # Could imply count of projects
    projects_count = await Project.find(Project.landmark_id == landmark_id).count()
    return {
        "total_projects": projects_count,
        "inventory_status": "Moving Fast",
        "new_launches": 2
    }

# --- 4. Combined Dashboard API ---

@router.get("/graphs/dashboard", response_model=Any)
@cache_public_data(ttl=settings.REDIS_CACHE_TTL_LANDMARKS)
async def get_locality_graph_dashboard(landmark_id: UUID = Query(...)) -> Any:
    """
    Combined API for reducing frontend calls.
    Aggregates Price Trends, Demand/Supply, and BHK Ratios.
    """
    landmark = await Landmark.get(landmark_id)
    if not landmark:
        raise HTTPException(status_code=404, detail="Landmark not found")
        
    # Aggregate data from internal functions or services
    # For MVP, reconstructing response
    return {
        "landmark_name": landmark.name,
        "price_trend": [
             {"year": 2023, "price": 5200},
             {"year": 2024, "price": 5800},
             {"year": 2025, "price": 6200}
        ],
        "demand_supply_index": 1.4, # >1 means High Demand
        "bhk_distribution": {
            "2 BHK": 45, # percentage
            "3 BHK": 35,
            "Plots": 20
        },
        "investment_score": 8.5 # out of 10
    }

