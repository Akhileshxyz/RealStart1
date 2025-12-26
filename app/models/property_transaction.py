from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from beanie import Document
from pydantic import Field

class PropertyTransaction(Document):
    """Registry transaction data for properties"""
    id: UUID = Field(default_factory=uuid4)

    # Location
    landmark_id: Optional[UUID] = None
    locality_name: str
    city: str
    society_name: Optional[str] = None

    # Transaction details
    registry_date: datetime
    agreement_price: float  # in INR
    area_sqft: float
    area_type: str = "BUILT_UP"  # "BUILT_UP", "CARPET", "SUPER_BUILT_UP"
    price_per_sqft: float

    # Property details
    property_type: str = "apartment"  # "apartment", "villa", "plot", "independent_floor"
    bhk: Optional[int] = None
    floor: Optional[int] = None
    total_floors: Optional[int] = None

    # Sale details
    purchase_type: str = "Resale"  # "Resale", "New"
    is_verified: bool = False

    # Coordinates
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "property_transactions"
        indexes = [
            "landmark_id",
            "locality_name",
            "city",
            "registry_date",
            "property_type"
        ]
