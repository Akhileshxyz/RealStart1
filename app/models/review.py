from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from beanie import Document
from pydantic import Field

class ReviewEntityType(str, Enum):
    LANDMARK = "LANDMARK"
    PROJECT = "PROJECT"

class Review(Document):
    id: UUID = Field(default_factory=uuid4)
    entity_id: UUID
    entity_type: ReviewEntityType = ReviewEntityType.LANDMARK
    user_id: UUID
    
    rating: float # 1.0 to 5.0
    content: str
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "reviews"
        indexes = [
            "entity_id",
            "user_id"
        ]
