from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.models.landmark import Landmark
from app.models.project import Project, ProjectStatus
from app.schemas.landmark import LandmarkSummary, UpcomingProjectSummary
from app.utils.json_sanitize import sanitize_str
from app.utils.media import public_image_url
from beanie.operators import In

router = APIRouter()


class LandmarkPublicResponse(BaseModel):
    id: UUID
    name: str
    city: Optional[str] = None
    zone: Optional[str] = None
    description: Optional[str] = None
    hero_desc: Optional[str] = None
    image_url: Optional[str] = None
    images: List[str] = []
    avg_plot_price: str = ""
    avg_apartment_price: str = ""
    avg_price_per_sqft: str = ""
    residential_rent_2bhk: str = ""
    rental_yield: str = ""
    price_trend: Optional[str] = None
    price_trend_3m: Optional[str] = None
    risk_profile: str = "moderate"
    price_growth: List[Dict[str, Any]] = []
    price_prediction: List[Dict[str, Any]] = []
    total_projects: int = 0
    active_layouts_count: int = 0
    rera_projects_count: int = 0
    upcoming_project_ids: List[UUID] = []
    upcoming_projects_list: List[Dict[str, Any]] = []
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


async def _get_upcoming_projects(landmark_id: UUID, manual_project_ids: List[UUID]) -> List[Dict[str, Any]]:
    """Fetch upcoming projects by IDs and also projects linked to this landmark."""
    # 1. Fetch projects where Project.landmark_id == landmark_id
    # Public view only shows NOT HIDDEN projects
    projects = await Project.find(
        Project.landmark_id == landmark_id,
        Project.is_hidden == False
    ).to_list()
    
    # 2. Add manually specified projects if they aren't already in the list
    if manual_project_ids:
        existing_ids = {p.id for p in projects}
        remaining_ids = [pid for pid in manual_project_ids if pid not in existing_ids]
        if remaining_ids:
            additional_projects = await Project.find(
                In(Project.id, remaining_ids),
                Project.is_hidden == False
            ).to_list()
            projects.extend(additional_projects)
            
    return [
        {
            "id": str(p.id),
            "name": sanitize_str(p.name),
            "slug": sanitize_str(p.slug),
            "min_price": p.min_price,
            "max_price": p.max_price,
            "property_type": getattr(p, "property_type", None),
            "status": getattr(p, "status", None),
            "gallery_images": [public_image_url(img) for img in p.gallery_images] if p.gallery_images else [],
        }
        for p in projects
    ]



@router.get("/", response_model=List[LandmarkPublicResponse])
async def list_public_landmarks(
    city_id: Optional[UUID] = Query(None, description="Filter by city ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> Any:
    """
    List all landmarks for public access.
    Returns simplified landmark data with key metrics.
    """
    query = {}
    if city_id:
        query["city_id"] = city_id

    landmarks = await Landmark.find(query).skip(skip).limit(limit).to_list()

    results = []
    for lm in landmarks:
        upcoming_projects = await _get_upcoming_projects(lm.id, lm.upcoming_project_ids or [])
        results.append(
            LandmarkPublicResponse(
                id=lm.id,
                name=sanitize_str(lm.name),
                city=sanitize_str(lm.city) if lm.city else None,
                zone=sanitize_str(lm.zone) if lm.zone else None,
                description=sanitize_str(lm.description) if lm.description else None,
                hero_desc=sanitize_str(lm.hero_desc) if lm.hero_desc else None,
                image_url=public_image_url(getattr(lm, "image_url", None)),
                images=lm.images or [],
                avg_plot_price=str(lm.avg_plot_price) if lm.avg_plot_price else "",
                avg_apartment_price=str(lm.avg_apartment_price) if lm.avg_apartment_price else "",
                avg_price_per_sqft=str(lm.avg_price_per_sqft) if lm.avg_price_per_sqft else "",
                residential_rent_2bhk=lm.residential_rent_2bhk or "",
                rental_yield=lm.rental_yield or "",
                price_trend=lm.price_trend,
                price_trend_3m=lm.price_trend_3m,
                risk_profile=getattr(lm, "risk_profile", "moderate"),
                price_growth=[pg.model_dump() for pg in lm.price_growth] if lm.price_growth else [],
                price_prediction=[pp.model_dump() for pp in lm.price_prediction] if lm.price_prediction else [],
                total_projects=lm.total_projects or 0,
                active_layouts_count=lm.active_layouts_count or 0,
                rera_projects_count=lm.rera_projects_count or 0,
                upcoming_project_ids=lm.upcoming_project_ids or [],
                upcoming_projects_list=upcoming_projects,
                latitude=lm.latitude,
                longitude=lm.longitude,
                location=lm.location.model_dump() if lm.location else None,
            )
        )
    return results


@router.get("/{landmark_id}", response_model=LandmarkPublicResponse)
async def get_public_landmark(landmark_id: UUID) -> Any:
    """
    Get detailed landmark information for public access.
    """
    landmark = await Landmark.get(landmark_id)
    if not landmark:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Landmark not found"
        )

    upcoming_projects = await _get_upcoming_projects(landmark.id, landmark.upcoming_project_ids or [])

    return LandmarkPublicResponse(
        id=landmark.id,
        name=sanitize_str(landmark.name),
        city=sanitize_str(landmark.city) if landmark.city else None,
        zone=sanitize_str(landmark.zone) if landmark.zone else None,
        description=sanitize_str(landmark.description) if landmark.description else None,
        hero_desc=sanitize_str(landmark.hero_desc) if landmark.hero_desc else None,
        image_url=public_image_url(getattr(landmark, "image_url", None)),
        images=landmark.images or [],
        avg_plot_price=str(landmark.avg_plot_price) if landmark.avg_plot_price else "",
        avg_apartment_price=str(landmark.avg_apartment_price) if landmark.avg_apartment_price else "",
        avg_price_per_sqft=str(landmark.avg_price_per_sqft) if landmark.avg_price_per_sqft else "",
        residential_rent_2bhk=landmark.residential_rent_2bhk or "",
        rental_yield=landmark.rental_yield or "",
        price_trend=landmark.price_trend,
        price_trend_3m=landmark.price_trend_3m,
        risk_profile=getattr(landmark, "risk_profile", "moderate"),
        price_growth=[pg.model_dump() for pg in landmark.price_growth] if landmark.price_growth else [],
        price_prediction=[pp.model_dump() for pp in landmark.price_prediction] if landmark.price_prediction else [],
        total_projects=landmark.total_projects or 0,
        active_layouts_count=landmark.active_layouts_count or 0,
        rera_projects_count=landmark.rera_projects_count or 0,
        upcoming_project_ids=landmark.upcoming_project_ids or [],
        upcoming_projects_list=upcoming_projects,
        latitude=landmark.latitude,
        longitude=landmark.longitude,
        location=landmark.location.model_dump() if landmark.location else None,
    )

