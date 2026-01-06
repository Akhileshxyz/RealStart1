from typing import Any, List, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User
from app.models.video import Video
from app.schemas.video import VideoCreate, VideoResponse, VideoUpdate
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[VideoResponse])
async def list_videos(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    List all videos with metadata.
    """
    return await Video.find_all().skip(skip).limit(limit).to_list()

@router.post("/", response_model=VideoResponse)
async def upload_video(
    video_in: VideoCreate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Register a new video (metadata).
    Payload includes: title, description, url, thumbnail_url, duration_seconds, format, video_type, landmark_id.
    """
    video = Video(**video_in.model_dump())
    await video.save()
    return video

@router.put("/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id: UUID,
    video_in: VideoUpdate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update video metadata.
    """
    video = await Video.get(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    update_data = video_in.model_dump(exclude_unset=True)
    await video.set(update_data)
    return video

@router.delete("/{video_id}")
async def delete_video(
    video_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Delete a video.
    """
    video = await Video.get(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    await video.delete()
    return {"message": "Video deleted"}

@router.get("/{video_id}/analytics", response_model=Dict[str, Any])
async def get_video_analytics(
    video_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get detailed analytics for a video.
    """
    video = await Video.get(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    return {
        "views": video.views_count,
        "watch_time_total": video.total_watch_time_seconds,
        "avg_watch_percentage": video.average_watch_percentage,
        "engagement": {
            "likes": video.likes_count,
            "shares": video.shares_count
        }
    }
