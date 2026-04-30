from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List
from beanie import Document, Indexed
from pydantic import Field

class Reel(Document):
    id: UUID = Field(default_factory=uuid4)
    video_url: str
    title: str
    description: Optional[str] = None
    landmark_id: Optional[UUID] = None
    uploaded_by: UUID
    status: str = "READY"  # READY, PROCESSING, FAILED
    processing_error: Optional[str] = None
    
    # Interaction counts for quick access (can be updated on like/comment)
    likes_count: int = 0
    comments_count: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "reels"
        indexes = [
            "-created_at",
            "uploaded_by"
        ]

class ReelLike(Document):
    id: UUID = Field(default_factory=uuid4)
    reel_id: UUID
    user_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "reels_likes"
        indexes = [
            "reel_id",
            "user_id",
            [("reel_id", 1), ("user_id", 1)]  # Unique per user-reel pair
        ]

class ReelComment(Document):
    id: UUID = Field(default_factory=uuid4)
    reel_id: UUID
    user_id: UUID
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "reels_comments"
        indexes = [
            "-created_at",
            "reel_id"
        ]

class ReelSave(Document):
    id: UUID = Field(default_factory=uuid4)
    reel_id: UUID
    user_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "reels_saves"
        indexes = [
            "reel_id",
            "user_id",
            [("reel_id", 1), ("user_id", 1)]  # Unique per user-reel pair
        ]
