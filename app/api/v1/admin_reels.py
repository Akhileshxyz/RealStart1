from typing import Any, List, Optional
from uuid import UUID
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile, Form
from app.api import deps
from app.models.user import User
from app.models.reel import Reel, ReelLike, ReelComment, ReelSave
from app.schemas.reel import ReelCreate, ReelUpdate, ReelResponse
from app.core.config import settings

router = APIRouter()

@router.get("/", response_model=List[ReelResponse])
async def list_reels_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(deps.get_current_active_team_member)
) -> Any:
    """
    List all reels for admin (paginated).
    Supports searching by title or place.
    """
    query = Reel.find_all()
    if search:
        query = query.find({
            "$or": [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"place": {"$regex": search, "$options": "i"}}
            ]
        })
    
    return await query.sort("-created_at").skip(skip).limit(limit).to_list()


@router.post("/", response_model=ReelResponse, status_code=status.HTTP_201_CREATED)
async def create_reel(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    place: Optional[str] = Form(None),
    video: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_team_member)
) -> Any:
    """
    Create a new reel (Admin/Team only) with video upload.
    """
    file_ext = Path(video.filename).suffix.lower()
    allowed_extensions = {".mp4", ".mov", ".avi", ".webm", ".mkv"}
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )

    upload_dir = Path(settings.UPLOAD_DIR) / str(current_user.id) / "reels"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save video: {str(e)}")
    finally:
        video.file.close()

    video_url = f"/uploads/{current_user.id}/reels/{unique_filename}"

    reel = Reel(
        title=title,
        description=description,
        place=place,
        video_url=video_url,
        uploaded_by=current_user.id
    )
    await reel.insert()
    return reel

@router.put("/{reel_id}", response_model=ReelResponse)
async def update_reel(
    reel_id: UUID,
    reel_in: ReelUpdate,
    current_user: User = Depends(deps.get_current_active_team_member)
) -> Any:
    """
    Update a reel (Admin/Team only).
    Only the uploader or a Super Admin can update the reel.
    """
    reel = await Reel.get(reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
    
    # Ownership or Super Admin check
    if reel.uploaded_by != current_user.id and current_user.role != "SUPER_ADMIN":
         raise HTTPException(
            status_code=403, detail="You do not have permission to update this reel"
        )

    update_data = reel_in.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    await reel.update({"$set": update_data})
    
    # Return updated reel
    return await Reel.get(reel_id)

@router.delete("/{reel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reel(
    reel_id: UUID,
    current_user: User = Depends(deps.get_current_active_team_member)
) -> None:
    """
    Delete a reel (Admin/Team only).
    """
    reel = await Reel.get(reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
        
    # Ownership or Super Admin check
    if reel.uploaded_by != current_user.id and current_user.role != "SUPER_ADMIN":
         raise HTTPException(
            status_code=403, detail="You do not have permission to delete this reel"
        )
    
    # Cascade delete interactions
    await ReelLike.find(ReelLike.reel_id == reel_id).delete()
    await ReelComment.find(ReelComment.reel_id == reel_id).delete()
    await ReelSave.find(ReelSave.reel_id == reel_id).delete()
    
    await reel.delete()
    return None
