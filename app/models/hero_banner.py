from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from beanie import Document
from pydantic import Field

class HeroBanner(Document):
    id: UUID = Field(default_factory=uuid4)
    title: Optional[str] = None
    image_url: str  # Web banner image path/URL
    mobile_image_url: Optional[str] = None # Mobile banner image path/URL
    link_url: Optional[str] = None # Optional CTA link
    order: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "hero_banners"
        indexes = [
            "is_active",
            "order",
        ]
