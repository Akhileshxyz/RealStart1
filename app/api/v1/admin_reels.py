from typing import Any, List, Optional
from uuid import UUID
import uuid
import shutil
from pathlib import Path
import subprocess
import asyncio
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile, Form, BackgroundTasks
from app.api import deps
from app.models.user import User
from app.models.reel import Reel, ReelLike, ReelComment, ReelSave
from app.models.landmark import Landmark
from app.schemas.reel import ReelCreate, ReelUpdate, ReelResponse, PaginatedReelResponse
from app.core.config import settings

router = APIRouter()

@router.get("/", response_model=PaginatedReelResponse)
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
    query_filter = {}
    if search:
        query_filter = {
            "$or": [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        }
    
    total = await Reel.find(query_filter).count()
    reels = await Reel.find(query_filter).sort("-created_at").skip(skip).limit(limit).to_list()
    
    # Resolve landmark names for better UI
    landmark_ids = [r.landmark_id for r in reels if r.landmark_id]
    landmark_map = {}
    if landmark_ids:
        landmarks = await Landmark.find({"_id": {"$in": landmark_ids}}).to_list()
        landmark_map = {l.id: l.name for l in landmarks}
    
    enriched_reels = []
    for r in reels:
        r_dict = r.model_dump()
        if r.landmark_id in landmark_map:
            r_dict["landmark_name"] = landmark_map[r.landmark_id]
        enriched_reels.append(r_dict)
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": enriched_reels
    }


async def compress_video(input_path: Path, output_path: Path, reel_id: UUID):
    """
    Compresses video to H.264 MP4 with web optimization.
    """
    try:
        # Check if ffmpeg is available
        ffmpeg_check = subprocess.run(["ffmpeg", "-version"], capture_output=True)
        if ffmpeg_check.returncode != 0:
             reel = await Reel.get(reel_id)
             if reel:
                 reel.status = "READY"
                 reel.processing_error = "FFmpeg not found. Using original file."
                 await reel.save()
             return

        # Optimization command
        command = [
            "-i", str(input_path),
            "-c:v", "libx264", "-crf", "28", "-preset", "fast",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            "-vf", "scale='if(gt(iw,ih),-2,1280):if(gt(iw,ih),720,-2)'", # Max 720p vertical
            "-y", str(output_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            "ffmpeg", *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        reel = await Reel.get(reel_id)
        if not reel: return
        
        if process.returncode == 0:
            reel.status = "READY"
            # Switch URL to compressed version
            reel.video_url = reel.video_url.replace("_original", "_compressed")
            # Optionally remove original
            try:
                os.remove(input_path)
            except:
                pass
        else:
            reel.status = "FAILED"
            reel.processing_error = process.stderr
            # Fallback to original if compression failed but original exists
            reel.video_url = reel.video_url.replace("_compressed", "_original")
            reel.status = "READY" # Still usable
        
        await reel.save()
    except Exception as e:
        reel = await Reel.get(reel_id)
        if reel:
            reel.status = "FAILED"
            reel.processing_error = str(e)
            await reel.save()


@router.post("/", response_model=ReelResponse, status_code=status.HTTP_201_CREATED)
async def create_reel(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    landmark_id: Optional[UUID] = Form(None),
    video: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
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
    
    file_id = uuid.uuid4()
    original_filename = f"{file_id}_original{file_ext}"
    compressed_filename = f"{file_id}_compressed.mp4"
    
    original_path = upload_dir / original_filename
    compressed_path = upload_dir / compressed_filename

    try:
        with original_path.open("wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save video: {str(e)}")
    finally:
        video.file.close()

    # Initial URL points to original, but we queue compression
    video_url = f"/uploads/{current_user.id}/reels/{original_filename}"

    reel = Reel(
        id=file_id,
        title=title,
        description=description,
        landmark_id=landmark_id,
        video_url=video_url,
        uploaded_by=current_user.id,
        status="PROCESSING"
    )
    await reel.insert()

    # Queue compression
    if background_tasks:
        background_tasks.add_task(compress_video, original_path, compressed_path, reel.id)

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
