from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class WishlistToggleRequest(BaseModel):
    property_id: UUID
    type: Optional[str] = "project"

class WishlistToggleResponse(BaseModel):
    status: str = "success"
    message: str
    action: str  # "added" or "removed"
    count: int

class WishlistItem(BaseModel):
    id: UUID
    name: str
    location: Optional[str] = None
    distance: Optional[str] = "1.4 km" # Placeholder as per user's example
    price_sqft: Optional[float] = None
    image_url: Optional[str] = None
    added_at: datetime

class WishlistResponse(BaseModel):
    status: str = "success"
    data: List[WishlistItem]
