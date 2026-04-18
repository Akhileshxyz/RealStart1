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

class ProjectWishlistItem(BaseModel):
    uuid: UUID
    name: str
    image: Optional[str] = None
    slug: str
    description: Optional[str] = None
    is_liked: bool = True

class ReelWishlistItem(BaseModel):
    uuid: UUID
    title: str
    video_url: str
    thumbnail: Optional[str] = None
    is_liked: bool = True

class CombinedWishlistResponse(BaseModel):
    reels: List[ReelWishlistItem]
    projects: List[ProjectWishlistItem]
