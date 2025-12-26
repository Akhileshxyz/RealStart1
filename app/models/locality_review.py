from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from beanie import Document
from pydantic import Field

class LocalityReview(Document):
    """User reviews for localities/landmarks"""
    id: UUID = Field(default_factory=uuid4)

    # Reference
    landmark_id: UUID
    user_id: UUID

    # Overall rating
    overall_rating: float = Field(ge=0, le=5)  # 0-5 stars

    # Category ratings
    connectivity_rating: Optional[float] = Field(None, ge=0, le=5)
    lifestyle_rating: Optional[float] = Field(None, ge=0, le=5)
    safety_rating: Optional[float] = Field(None, ge=0, le=5)
    greenery_rating: Optional[float] = Field(None, ge=0, le=5)
    environment_rating: Optional[float] = Field(None, ge=0, le=5)

    # Review content
    title: Optional[str] = None
    review_text: Optional[str] = None

    # User info (denormalized for performance)
    user_name: Optional[str] = None

    # Helpful votes
    helpful_count: int = 0
    not_helpful_count: int = 0

    # Moderation
    is_verified: bool = False
    is_approved: bool = True
    is_flagged: bool = False

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "locality_reviews"
        indexes = [
            "landmark_id",
            "user_id",
            "overall_rating",
            "created_at"
        ]
