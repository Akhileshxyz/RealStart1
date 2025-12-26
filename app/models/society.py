from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List
from beanie import Document
from pydantic import Field

class Society(Document):
    """Housing society/apartment complex details"""
    id: UUID = Field(default_factory=uuid4)

    # Basic info
    name: str
    landmark_id: Optional[UUID] = None
    locality_name: str
    city: str

    # Builder info
    builder_name: Optional[str] = None
    builder_id: Optional[UUID] = None

    # Society details
    total_units: Optional[int] = None
    possession_year: Optional[int] = None
    rera_registered: bool = False
    rera_id: Optional[str] = None

    # Pricing
    price_range_min: Optional[float] = None  # in INR
    price_range_max: Optional[float] = None
    avg_price_per_sqft: Optional[float] = None

    # Amenities
    amenities: List[str] = []

    # Ratings
    rating: Optional[float] = None  # 0-5
    total_reviews: int = 0

    # Location
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Demand metrics (for analytics)
    search_count: int = 0  # How many times searched
    view_count: int = 0

    # Metadata
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "societies"
        indexes = [
            "landmark_id",
            "locality_name",
            "city",
            "builder_id",
            "search_count"
        ]
