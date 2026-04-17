from typing import Any, List, Optional
from uuid import UUID
from pathlib import Path
import shutil
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, Body, status
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
    LandmarkSelection,
    UpcomingProjectSummary,
    LandmarkBulkDelete
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
    # We include projects EXPLICITLY linked in upcoming_project_ids 
    # AND projects that point to this landmark via Project.landmark_id
    projects_via_field = await Project.find(Project.landmark_id == landmark.id).to_list()
    
    manual_ids = landmark.upcoming_project_ids or []
    existing_ids = {p.id for p in projects_via_field}
    remaining_ids = [pid for pid in manual_ids if pid not in existing_ids]
    
    if remaining_ids:
        additional_projs = await Project.find(In(Project.id, remaining_ids)).to_list()
        projects_via_field.extend(additional_projs)

    
    data["upcoming_projects_list"] = [
        UpcomingProjectSummary.model_validate(p.model_dump()) for p in projects_via_field
    ]

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
    raw_city_ids = await Landmark.distinct("city_id")
    unique_city_ids = []
    if raw_city_ids:
        import ast
        import bson
        for uid in raw_city_ids:
            if isinstance(uid, UUID):
                unique_city_ids.append(uid)
            elif isinstance(uid, (bytes, bson.binary.Binary)):
                unique_city_ids.append(UUID(bytes=bytes(uid)))
            elif isinstance(uid, str):
                try:
                    unique_city_ids.append(UUID(uid))
                except ValueError:
                    if uid.startswith("b'") and uid.endswith("'"):
                        try:
                            unique_city_ids.append(UUID(bytes=ast.literal_eval(uid)))
                        except:
                            pass
    
    # Resolve relationships for the list (limited for performance)
    enriched_data = []
    for lm in landmarks:
        enriched_data.append(await _resolve_landmark_relationships(lm))

    return {
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "data": enriched_data,
        "unique_cities": unique_city_ids
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

    # Update fields - include all provided values including nested arrays like price_growth
    update_data = update_in.model_dump(exclude_unset=False)
    for k, v in update_data.items():
        if v is not None:
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

@router.get("/selection", response_model=List[LandmarkSelection])
async def get_landmarks_selection_list(
    city_id: Optional[UUID] = Query(None),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Lightweight list of landmarks (ID, Name, City, Zone) for multi-select dropdowns.
    """
    query = {}
    if city_id:
        query["city_id"] = city_id
    
    # Use projection for efficiency
    landmarks = await Landmark.find(query).project(LandmarkSelection).to_list()
    return landmarks

@router.delete("/bulk-delete", status_code=status.HTTP_200_OK)
async def bulk_delete_landmarks(
    payload: LandmarkBulkDelete,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Delete multiple landmarks and their associated files.
    """
    deleted_count = 0
    errors = []
    
    for landmark_id in payload.landmark_ids:
        try:
            landmark = await Landmark.get(landmark_id)
            if not landmark:
                errors.append({"id": str(landmark_id), "error": "Not found"})
                continue
            
            # Cleanup files
            shutil.rmtree(Path(settings.UPLOAD_DIR) / "localities" / str(landmark_id), ignore_errors=True)
            
            await landmark.delete()
            deleted_count += 1
        except Exception as e:
            errors.append({"id": str(landmark_id), "error": str(e)})
            
    return {
        "message": f"Successfully deleted {deleted_count} landmarks.",
        "deleted_count": deleted_count,
        "errors": errors if errors else None
    }

@router.get("/performance/stats", response_model=Any)
async def get_landmark_performance(
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Top landmarks by layouts traction"""
    return await Landmark.find_all().sort("-active_layouts_count").limit(10).to_list()
