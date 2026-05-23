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
    name_kn: Optional[str] = None
    city: Optional[str] = None
    city_id: Optional[UUID] = None
    zone: Optional[str] = None
    description: Optional[str] = None
    description_kn: Optional[str] = None
    hero_desc: Optional[str] = None
    hero_desc_kn: Optional[str] = None
    image_url: Optional[str] = None
    images: List[str] = []
    avg_plot_price: str = ""
    avg_commercial_plot_price: str = ""
    avg_price_per_sqft: str = ""
    residential_rent_2bhk: str = ""
    rental_yield: str = ""
    price_trend: Optional[str] = None
    price_trend_3m: Optional[str] = None
    risk_profile: str = "moderate"
    landmark_score: Optional[float] = None
    rental_strength: Optional[str] = None
    future_growth: Optional[str] = None
    family_living: Optional[str] = None
    traffic: Optional[str] = None
    social_infra: Optional[str] = None
    appreciation_potential_5yr: Optional[str] = None
    price_growth: List[Dict[str, Any]] = []
    price_prediction: List[Dict[str, Any]] = []
    total_projects: int = 0
    active_layouts_count: int = 0
    rera_projects_count: int = 0
    upcoming_project_ids: List[UUID] = []
    upcoming_projects_list: List[Dict[str, Any]] = [] # Real project entities
    upcoming_developments: List[Dict[str, Any]] = [] # Manual highlights
    nearby_projects: List[Dict[str, Any]] = []
    nearby_landmarks: List[Dict[str, Any]] = []
    top_investment_spots: List[Dict[str, Any]] = [] # Manual highlights
    amenities: List[str] = []
    amenities_kn: List[str] = []
    nearby_amenities: List[Dict[str, Any]] = []
    nearby_amenities_kn: List[str] = []
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: Optional[Dict[str, Any]] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


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



async def _get_nearby_landmarks(landmark_ids: List[UUID]) -> List[Dict[str, Any]]:
    """Fetch basic info for nearby landmarks."""
    if not landmark_ids:
        return []
    landmarks = await Landmark.find(In(Landmark.id, landmark_ids)).to_list()
    return [
        {
            "id": str(lm.id),
            "name": sanitize_str(lm.name),
            "avg_plot_price": str(lm.avg_plot_price) if lm.avg_plot_price else "0",
            "city": sanitize_str(lm.city) if lm.city else None
        }
        for lm in landmarks
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
        query["$or"] = [
            {"city_id": city_id},
            {"city_id": str(city_id)}
        ]

    landmarks = await Landmark.find(query).skip(skip).limit(limit).to_list()

    if not landmarks:
        return []

    results = []
    for lm in landmarks:
        try:
            upcoming_projects = await _get_upcoming_projects(lm.id, lm.upcoming_project_ids or [])
            
            # Fetch real nearby landmarks
            # If explicit nearby_landmarks_ids are provided, use them. 
            # OTHERWISE, fetch other landmarks from the same city.
            if lm.nearby_landmarks_ids:
                real_nearby = await _get_nearby_landmarks(lm.nearby_landmarks_ids)
            elif lm.city_id:
                # Fetch up to 10 other landmarks from the same city
                city_lms = await Landmark.find(
                    Landmark.city_id == lm.city_id,
                    Landmark.id != lm.id
                ).limit(10).to_list()
                real_nearby = [
                    {
                        "id": str(clm.id),
                        "name": sanitize_str(clm.name),
                        "avg_plot_price": str(clm.avg_plot_price) if clm.avg_plot_price else "0",
                        "city": sanitize_str(clm.city) if clm.city else None
                    }
                    for clm in city_lms
                ]
            else:
                real_nearby = []

            manual_nearby = [
                {
                    "is_highlight": True, 
                    "title": uh.title, 
                    "description": uh.description, 
                    "icon_url": uh.icon_url
                } 
                for uh in lm.nearby_landmarks_list
            ] if lm.nearby_landmarks_list else []
            
            item = LandmarkPublicResponse(
                id=lm.id,
                name=lm.name,
                name_kn=lm.name_kn,
                city=sanitize_str(lm.city),
                city_id=lm.city_id,
                zone=sanitize_str(lm.zone),
                description=lm.description,
                description_kn=lm.description_kn,
                hero_desc=lm.hero_desc,
                hero_desc_kn=lm.hero_desc_kn,
                image_url=public_image_url(lm.images[0]) if lm.images else None,
                images=[public_image_url(img) for img in lm.images],
                avg_plot_price=str(lm.avg_plot_price) if lm.avg_plot_price else "0",
                avg_commercial_plot_price=str(lm.avg_commercial_plot_price) if lm.avg_commercial_plot_price else "0",
                avg_price_per_sqft=str(lm.avg_price_per_sqft) if lm.avg_price_per_sqft else "0",
                residential_rent_2bhk=str(lm.residential_rent_2bhk) if lm.residential_rent_2bhk else "0",
                rental_yield=str(lm.rental_yield) if lm.rental_yield else "0",
                price_trend=lm.price_trend,
                price_trend_3m=lm.price_trend_3m,
                risk_profile=lm.risk_profile.value if hasattr(lm.risk_profile, "value") else str(lm.risk_profile),
                price_growth=[pg.model_dump() if hasattr(pg, "model_dump") else pg for pg in (lm.price_growth or [])],
                price_prediction=[pp.model_dump() if hasattr(pp, "model_dump") else pp for pp in (lm.price_prediction or [])],
                total_projects=lm.total_projects or 0,
                active_layouts_count=lm.active_layouts_count or 0,
                rera_projects_count=lm.rera_projects_count or 0,
                upcoming_project_ids=lm.upcoming_project_ids or [],
                upcoming_projects_list=upcoming_projects,
                upcoming_developments=[ud.model_dump() if hasattr(ud, "model_dump") else ud for ud in (lm.upcoming_projects_list or [])],
                nearby_projects=[{"id": str(pid)} for pid in (lm.nearby_project_ids or [])],
                nearby_landmarks=real_nearby,
                top_investment_spots=[uh.model_dump() if hasattr(uh, "model_dump") else uh for uh in (lm.nearby_landmarks_list or [])],
                amenities=lm.amenities or [],
                amenities_kn=lm.amenities_kn or [],
                nearby_amenities=[na.model_dump() if hasattr(na, "model_dump") else na for na in (lm.nearby_amenities or [])],
                nearby_amenities_kn=lm.nearby_amenities_kn or [],
                latitude=lm.latitude,
                longitude=lm.longitude,
                location=lm.location.model_dump() if (lm.location and hasattr(lm.location, "model_dump")) else (lm.location if isinstance(lm.location, dict) else None),
                landmark_score=lm.landmark_score,
                rental_strength=lm.rental_strength,
                future_growth=lm.future_growth,
                family_living=lm.family_living,
                traffic=lm.traffic,
                social_infra=lm.social_infra,
            )
            results.append(item)
        except Exception as e:
            print(f"Error processing landmark {lm.id}: {e}")
            continue
    
    return results or []


@router.get("/compare")
async def get_landmark_comparison(base_id: UUID, target_id: UUID) -> Any:
    """
    Compare two landmarks side-by-side.
    """
    base = await Landmark.get(base_id)
    target = await Landmark.get(target_id)
    
    if not base or not target:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both landmarks not found"
        )

    # Process base
    base_projects = await _get_upcoming_projects(base.id, base.upcoming_project_ids or [])
    # Process target
    target_projects = await _get_upcoming_projects(target.id, target.upcoming_project_ids or [])

    # Helper to map Landmark to Response
    def map_to_response(lm, projects):
        return LandmarkPublicResponse(
            id=lm.id,
            name=lm.name,
            name_kn=lm.name_kn,
            city=sanitize_str(lm.city),
            city_id=lm.city_id,
            zone=sanitize_str(lm.zone),
            description=lm.description,
            description_kn=lm.description_kn,
            hero_desc=lm.hero_desc,
            hero_desc_kn=lm.hero_desc_kn,
            image_url=public_image_url(lm.images[0]) if lm.images else None,
            images=[public_image_url(img) for img in lm.images],
            avg_plot_price=str(lm.avg_plot_price) if lm.avg_plot_price else "0",
            avg_commercial_plot_price=str(lm.avg_commercial_plot_price) if lm.avg_commercial_plot_price else "0",
            avg_price_per_sqft=str(lm.avg_price_per_sqft) if lm.avg_price_per_sqft else "0",
            residential_rent_2bhk=str(lm.residential_rent_2bhk) if lm.residential_rent_2bhk else "0",
            rental_yield=str(lm.rental_yield) if lm.rental_yield else "0",
            price_trend=lm.price_trend,
            price_trend_3m=lm.price_trend_3m,
            risk_profile=lm.risk_profile.value if hasattr(lm.risk_profile, "value") else str(lm.risk_profile),
            price_growth=[pg.model_dump() if hasattr(pg, "model_dump") else pg for pg in (lm.price_growth or [])],
            price_prediction=[pp.model_dump() if hasattr(pp, "model_dump") else pp for pp in (lm.price_prediction or [])],
            total_projects=lm.total_projects or 0,
            active_layouts_count=lm.active_layouts_count or 0,
            rera_projects_count=lm.rera_projects_count or 0,
            upcoming_project_ids=lm.upcoming_project_ids or [],
            upcoming_projects_list=projects,
            upcoming_developments=[ud.model_dump() if hasattr(ud, "model_dump") else ud for ud in (lm.upcoming_projects_list or [])],
            nearby_projects=[{"id": str(pid)} for pid in (lm.nearby_project_ids or [])],
            nearby_landmarks=[], # Simplify comparison view
            top_investment_spots=[uh.model_dump() if hasattr(uh, "model_dump") else uh for uh in (lm.nearby_landmarks_list or [])],
            amenities=lm.amenities or [],
            amenities_kn=lm.amenities_kn or [],
            nearby_amenities=[na.model_dump() if hasattr(na, "model_dump") else na for na in (lm.nearby_amenities or [])],
            nearby_amenities_kn=lm.nearby_amenities_kn or [],
            latitude=lm.latitude,
            longitude=lm.longitude,
            location=lm.location.model_dump() if lm.location else None,
            landmark_score=lm.landmark_score,
            rental_strength=lm.rental_strength,
            future_growth=lm.future_growth,
            family_living=lm.family_living,
            traffic=lm.traffic,
            social_infra=lm.social_infra,
        )

    return {
        "base": map_to_response(base, base_projects),
        "target": map_to_response(target, target_projects)
    }

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
    
    # Fetch real nearby landmarks
    # If explicit nearby_landmarks_ids are provided, use them. 
    # OTHERWISE, fetch other landmarks from the same city.
    if landmark.nearby_landmarks_ids:
        real_nearby = await _get_nearby_landmarks(landmark.nearby_landmarks_ids)
    elif landmark.city_id:
        # Fetch up to 10 other landmarks from the same city
        city_lms = await Landmark.find(
            Landmark.city_id == landmark.city_id,
            Landmark.id != landmark.id
        ).limit(10).to_list()
        real_nearby = [
            {
                "id": str(clm.id),
                "name": sanitize_str(clm.name),
                "avg_plot_price": str(clm.avg_plot_price) if clm.avg_plot_price else "0",
                "city": sanitize_str(clm.city) if clm.city else None
            }
            for clm in city_lms
        ]
    else:
        real_nearby = []

    return LandmarkPublicResponse(
        id=landmark.id,
        name=landmark.name,
        name_kn=landmark.name_kn,
        city=sanitize_str(landmark.city),
        city_id=landmark.city_id,
        zone=sanitize_str(landmark.zone),
        description=landmark.description,
        description_kn=landmark.description_kn,
        hero_desc=landmark.hero_desc,
        hero_desc_kn=landmark.hero_desc_kn,
        image_url=public_image_url(landmark.images[0]) if landmark.images else None,
        images=[public_image_url(img) for img in landmark.images],
        avg_plot_price=str(landmark.avg_plot_price) if landmark.avg_plot_price else "0",
        avg_commercial_plot_price=str(landmark.avg_commercial_plot_price) if landmark.avg_commercial_plot_price else "0",
        avg_price_per_sqft=str(landmark.avg_price_per_sqft) if landmark.avg_price_per_sqft else "0",
        residential_rent_2bhk=str(landmark.residential_rent_2bhk) if landmark.residential_rent_2bhk else "0",
        rental_yield=str(landmark.rental_yield) if landmark.rental_yield else "0",
        price_trend=landmark.price_trend,
        price_trend_3m=landmark.price_trend_3m,
        risk_profile=landmark.risk_profile.value if hasattr(landmark.risk_profile, "value") else str(landmark.risk_profile),
        price_growth=[pg.model_dump() if hasattr(pg, "model_dump") else pg for pg in (landmark.price_growth or [])],
        price_prediction=[pp.model_dump() if hasattr(pp, "model_dump") else pp for pp in (landmark.price_prediction or [])],
        total_projects=landmark.total_projects or 0,
        active_layouts_count=landmark.active_layouts_count or 0,
        rera_projects_count=landmark.rera_projects_count or 0,
        upcoming_project_ids=landmark.upcoming_project_ids or [],
        upcoming_projects_list=upcoming_projects,
        upcoming_developments=[ud.model_dump() if hasattr(ud, "model_dump") else ud for ud in (landmark.upcoming_projects_list or [])],
        nearby_projects=[{"id": str(pid)} for pid in (landmark.nearby_project_ids or [])],
        nearby_landmarks=real_nearby,
        top_investment_spots=[uh.model_dump() if hasattr(uh, "model_dump") else uh for uh in (landmark.nearby_landmarks_list or [])],
        amenities=landmark.amenities or [],
        amenities_kn=landmark.amenities_kn or [],
        nearby_amenities=[na.model_dump() if hasattr(na, "model_dump") else na for na in (landmark.nearby_amenities or [])],
        nearby_amenities_kn=landmark.nearby_amenities_kn or [],
        latitude=landmark.latitude,
        longitude=landmark.longitude,
        location=landmark.location.model_dump() if (landmark.location and hasattr(landmark.location, "model_dump")) else (landmark.location if isinstance(landmark.location, dict) else None),
        landmark_score=landmark.landmark_score,
        rental_strength=landmark.rental_strength,
        future_growth=landmark.future_growth,
        family_living=landmark.family_living,
        traffic=landmark.traffic,
        social_infra=landmark.social_infra,
    )
