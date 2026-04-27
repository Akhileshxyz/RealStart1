from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class HeroBannerCreate(BaseModel):
    title: Optional[str] = None
    image_url: Optional[str] = None
    mobile_image_url: Optional[str] = None
    link_url: Optional[str] = None
    order: int = 0
    is_active: bool = True

class HeroBannerUpdate(BaseModel):
    title: Optional[str] = None
    image_url: Optional[str] = None
    mobile_image_url: Optional[str] = None
    link_url: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None

class HeroBannerResponse(BaseModel):
    id: UUID
    title: Optional[str] = None
    image_url: str
    mobile_image_url: Optional[str] = None
    link_url: Optional[str] = None
    order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PublicHeroBannerResponse(BaseModel):
    image: str
    mobile_image: Optional[str] = None
    link: Optional[str] = None
    title: Optional[str] = None
