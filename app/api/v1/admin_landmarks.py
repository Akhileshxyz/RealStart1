from typing import Any, List, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from app.api import deps
from app.models.user import User
from app.models.landmark import Landmark
from app.schemas.landmark import PaginatedLandmarkResponse
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=PaginatedLandmarkResponse)
async def list_all_landmarks(
    city: str = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    List all landmarks, optionally filtered by city.
    Includes unique cities for filtering in the response.
    """
    query = {}
    if city:
        query["city"] = city
        
    # Get total count (filtered)
    total_count = await Landmark.find(query).count()
    
    # Get paginated data
    landmarks = await Landmark.find(query).skip(skip).limit(limit).to_list()
    
    # Get unique cities from ALL records (unfiltered for dropdown usage)
    unique_cities = await Landmark.distinct("city")
    
    return {
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "data": landmarks,
        "unique_cities": sorted(unique_cities) if unique_cities else []
    }

@router.post("/", response_model=Landmark)
async def create_landmark(
    landmark_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Create a new landmark.
    """
    # Simple dict mapping. Production should use Pydantic schema.
    landmark = Landmark(
        **landmark_data,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    await landmark.save()
    return landmark

@router.put("/{landmark_id}", response_model=Landmark)
async def update_landmark(
    landmark_id: UUID,
    landmark_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update a landmark.
    """
    landmark = await Landmark.get(landmark_id)
    if not landmark:
        raise HTTPException(status_code=404, detail="Landmark not found")
        
    for k, v in landmark_data.items():
        if hasattr(landmark, k):
            setattr(landmark, k, v)
            
    landmark.updated_at = datetime.utcnow()
    await landmark.save()
    return landmark

@router.delete("/{landmark_id}")
async def delete_landmark(
    landmark_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Delete a landmark.
    """
    landmark = await Landmark.get(landmark_id)
    if not landmark:
        raise HTTPException(status_code=404, detail="Landmark not found")
        
    await landmark.delete()
    return {"message": "Landmark deleted successfully"}

# --- Performance Analytics ---

@router.get("/performance", response_model=Any)
async def get_landmark_performance(
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get reach by location (aggregated active layouts/projects count).
    """
    # Similar to Analytics module but focused on management view
    landmarks = await Landmark.find_all().to_list()
    # Sort by active layouts
    sorted_landmarks = sorted(landmarks, key=lambda x: x.active_layouts_count or 0, reverse=True)
    return sorted_landmarks[:10]

@router.get("/top-performing", response_model=List[Landmark])
async def get_top_performing_landmarks(
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Top landmarks by traction (projects count for now).
    """
    return await Landmark.find_all().sort("-total_projects").limit(5).to_list()
