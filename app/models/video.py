from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from beanie import Document
from pydantic import Field

class Video(Document):
    id: UUID = Field(default_factory=uuid4)
    title: str
    description: Optional[str] = None
    video_url: str = Field(..., alias="url")
    thumbnail_url: Optional[str] = None
    
    # New Metadata
    duration_seconds: int = 0
    format: str = "mp4"
    video_type: str = "REEL"  # REEL, PROMO, HIGHLIGHT
    landmark_id: Optional[UUID] = None
    
    # Engagement Metrics
    views_count: int = 0
    total_watch_time_seconds: float = 0.0
    average_watch_percentage: float = 0.0
    likes_count: int = 0
    shares_count: int = 0
    
    is_active: bool = True
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "videos"
        # Since we use alias for video_url, we need to allow population by field name
        # but Beanie models usually handle this via Pydantic.
        # Actually Pydantic v2 uses model_config.
    
    model_config = {
        "populate_by_name": True
    }
