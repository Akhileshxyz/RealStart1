from typing import Any, List, Optional
from uuid import UUID
from pathlib import Path
import shutil
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from app.api import deps
from app.models.user import User
from app.models.landmark import Landmark
from app.models.project import Project
from app.schemas.landmark import (
    PaginatedLandmarkResponse, 
    LandmarkResponse, 
    LandmarkCreate, 
    LandmarkUpdate,
    LandmarkSummary,
    UpcomingProjectSummary
)
from beanie.operators import In
from app.core.config import settings

_ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

router = APIRouter()

def _save_landmark_images(landmark_id: UUID, files: List[UploadFile]) -> List[str]:
    """Helper to save multiple landmark images to the filesystem"""
    saved_paths = []
    upload_root = Path(settings.UPLOAD_DIR)
    localities_dir = upload_root / "localities" / str(landmark_id)
    localities_dir.mkdir(parents=True, exist_ok=True)

    for i, file in enumerate(files):
        content_type = (file.content_type or "").split(";")[0].strip().lower()
        if content_type in _ALLOWED_IMAGE_TYPES:
            ext = _ALLOWED_IMAGE_TYPES[content_type]
            # Use index + timestamp to avoid name collisions
            filename = f"image_{i}_{int(datetime.utcnow().timestamp())}{ext}"
            dest = localities_dir / filename
            with dest.open("wb") as out:
                shutil.copyfileobj(file.file, out)
            saved_paths.append(f"/uploads/localities/{landmark_id}/{filename}")
    
    return saved_paths

async def _resolve_landmark_relationships(landmark: Landmark) -> dict:
    """Helper to resolve UUID lists into detailed summaries for the response"""
    data = landmark.model_dump()
    
    # 1. Resolve Nearby Landmarks
    if landmark.nearby_landmarks_ids:
        nearby_lms = await Landmark.find(In(Landmark.id, landmark.nearby_landmarks_ids)).to_list()
        data["nearby_landmarks"] = [
            LandmarkSummary.model_validate(l.model_dump()) for l in nearby_lms
        ]
    else:
        data["nearby_landmarks"] = []

    # 2. Resolve Upcoming Projects
    if landmark.upcoming_project_ids:
        upcoming_projs = await Project.find(In(Project.id, landmark.upcoming_project_ids)).to_list()
        data["upcoming_projects_list"] = [
            UpcomingProjectSummary.model_validate(p.model_dump()) for p in upcoming_projs
        ]
    else:
        data["upcoming_projects_list"] = []

    # 3. Resolve Nearby Projects
    if landmark.nearby_project_ids:
        nearby_projs = await Project.find(In(Project.id, landmark.nearby_project_ids)).to_list()
        data["nearby_projects"] = [
            UpcomingProjectSummary.model_validate(p.model_dump()) for p in nearby_projs
        ]
    else:
        data["nearby_projects"] = []

    return data

@router.get("/", response_model=PaginatedLandmarkResponse)
async def list_all_landmarks(
    city_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=5000),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    List all landmarks, optionally filtered by city_id.
    """
    query = {}
    if city_id:
        query["city_id"] = city_id
        
    total_count = await Landmark.find(query).count()
    landmarks = await Landmark.find(query).skip(skip).limit(limit).to_list()
    
    # Get unique city IDs for filtering
    unique_city_ids = await Landmark.distinct("city_id")
    
    # Resolve relationships for the list (limited for performance)
    enriched_data = []
    for lm in landmarks:
        enriched_data.append(await _resolve_landmark_relationships(lm))

    return {
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "data": enriched_data,
        "unique_cities": unique_city_ids if unique_city_ids else []
    }

@router.post("/", response_model=LandmarkResponse)
async def create_landmark(
    data: str = Form(...), # JSON stringified schema
    files: List[UploadFile] = File(default=[]),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Create a new landmark with multiple images (multipart/form-data).
    """
    try:
        landmark_dict = json.loads(data)
        # Validate with schema
        landmark_in = LandmarkCreate(**landmark_dict)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid data format: {str(e)}")

    landmark = Landmark(**landmark_in.model_dump())
    
    if files:
        landmark.images = _save_landmark_images(landmark.id, files)
        
    await landmark.insert()
    return await _resolve_landmark_relationships(landmark)

@router.put("/{landmark_id}", response_model=LandmarkResponse)
async def update_landmark(
    landmark_id: UUID,
    data: str = Form(...),
    files: List[UploadFile] = File(default=[]),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update a landmark and optionally add more images.
    """
    landmark = await Landmark.get(landmark_id)
    if not landmark:
        raise HTTPException(status_code=404, detail="Landmark not found")

    try:
        update_dict = json.loads(data)
        update_in = LandmarkUpdate(**update_dict)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid update format: {str(e)}")

    # Update fields
    update_data = update_in.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(landmark, k, v)
            
    # Handle new file uploads
    if files:
        new_images = _save_landmark_images(landmark.id, files)
        landmark.images.extend(new_images)

    landmark.updated_at = datetime.utcnow()
    await landmark.save()
    return await _resolve_landmark_relationships(landmark)

@router.get("/{landmark_id}", response_model=LandmarkResponse)
async def get_landmark_by_id(
    landmark_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    landmark = await Landmark.get(landmark_id)
    if not landmark:
        raise HTTPException(status_code=404, detail="Landmark not found")
    return await _resolve_landmark_relationships(landmark)

@router.delete("/{landmark_id}")
async def delete_landmark(
    landmark_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    landmark = await Landmark.get(landmark_id)
    if not landmark:
        raise HTTPException(status_code=404, detail="Landmark not found")
        
    # Optional: Delete images from disk
    shutil.rmtree(Path(settings.UPLOAD_DIR) / "localities" / str(landmark_id), ignore_errors=True)
    
    await landmark.delete()
    return {"message": "Landmark deleted successfully"}

@router.get("/performance/stats", response_model=Any)
async def get_landmark_performance(
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Top landmarks by layouts traction"""
    return await Landmark.find_all().sort("-active_layouts_count").limit(10).to_list()
