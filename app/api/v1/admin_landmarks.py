from typing import Any, List, Dict
from uuid import UUID
from pathlib import Path
import shutil
from fastapi import APIRouter, Depends, HTTPException, Body, Query, UploadFile, File
from app.api import deps
from app.models.user import User
from app.models.landmark import Landmark
from app.schemas.landmark import PaginatedLandmarkResponse
from app.core.config import settings
from datetime import datetime

_ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

router = APIRouter()

@router.get("/", response_model=PaginatedLandmarkResponse)
async def list_all_landmarks(
    city: str = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=5000),
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


@router.post("/{landmark_id}/image", response_model=Landmark)
async def upload_landmark_image(
    landmark_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Upload a locality / market-intelligence hero image. Stored under /uploads/localities/{landmark_id}.ext
    and `landmark.image_url` is set to the public path (use in GET /market-intelligence and related APIs).
    """
    landmark = await Landmark.get(landmark_id)
    if not landmark:
        raise HTTPException(status_code=404, detail="Landmark not found")

    content_type = (file.content_type or "").split(";")[0].strip().lower()
    if content_type not in _ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="File must be an image (jpeg, png, webp, gif)",
        )
    ext = _ALLOWED_IMAGE_TYPES[content_type]
    upload_root = Path(settings.UPLOAD_DIR)
    localities_dir = upload_root / "localities"
    localities_dir.mkdir(parents=True, exist_ok=True)

    dest = localities_dir / f"{landmark_id}{ext}"
    try:
        with dest.open("wb") as out:
            shutil.copyfileobj(file.file, out)
    finally:
        await file.close()

    landmark.image_url = f"/uploads/localities/{landmark_id}{ext}"
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
