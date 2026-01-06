from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class VideoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    url: str = Field(..., description="Video URL")
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[int] = 0
    format: Optional[str] = "mp4"
    video_type: Optional[str] = "REEL"  # REEL, PROMO, HIGHLIGHT
    landmark_id: Optional[UUID] = None
    is_active: bool = True

class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    format: Optional[str] = None
    video_type: Optional[str] = None
    landmark_id: Optional[UUID] = None
    is_active: Optional[bool] = None

class VideoResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    video_url: str
    thumbnail_url: Optional[str] = None
    duration_seconds: int = 0
    format: str = "mp4"
    video_type: str = "REEL"
    landmark_id: Optional[UUID] = None
    
    views_count: int = 0
    total_watch_time_seconds: float = 0.0
    average_watch_percentage: float = 0.0
    likes_count: int = 0
    shares_count: int = 0
    
    is_active: bool = True
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
