from typing import Any, List, Dict, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from app.api import deps
from app.models.landmark import Landmark
from app.core.config import settings
from datetime import datetime
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

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

# --- 2. Canonical Details API ---

@router.get("/{landmark_id}", response_model=Any)
async def get_locality_details(landmark_id: UUID) -> Any:
    """
    Master API for static locality details.
    """
    landmark = await Landmark.get(landmark_id)
    if not landmark:
        raise HTTPException(status_code=404, detail="Landmark not found")
        
    return {
        "id": landmark.id,
        "name": landmark.name,
        "city": landmark.city,
        "zone": landmark.zone,
        "description": landmark.description,
        "location": landmark.location,
        "rating": 4.5, # Mock
        "review_count": 120, # Mock
        "about_text": f"A prime residential area in {landmark.city} with great connectivity."
    }

# --- 3. Sub-APIs ---

@router.get("/transactions", response_model=Any)
async def get_registry_transactions(landmark_id: UUID) -> Any:
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
async def get_price_insights(landmark_id: UUID) -> Any:
    """
    Mock price insights.
    """
    landmark = await Landmark.get(landmark_id)
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
async def get_market_trends(landmark_id: UUID) -> Any:
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

@router.get("/societies", response_model=Any)
async def get_linked_societies(landmark_id: UUID) -> Any:
    """
    Fetch linked projects/societies.
    """
    # Assuming Project model has logic to link to landmark or simply mock for now
    # Ideally: await Project.find({"landmark_id": landmark_id}).to_list()
    return [
        {"name": "Green Valley", "type": "Layout", "status": "Ready to Move", "min_price": "45L"},
        {"name": "Prestige Heights", "type": "Apartment", "status": "Under Construction", "min_price": "90L"}
    ]

# --- 4. Combined Dashboard API ---

@router.get("/graphs/dashboard", response_model=Any)
async def get_locality_graph_dashboard(landmark_id: UUID) -> Any:
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
