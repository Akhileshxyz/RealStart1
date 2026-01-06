from typing import Optional, Any, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, HttpUrl, ConfigDict
from app.models.ad import AdPlatform, AdType

class AdBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    target_link: Optional[str] = None
    platform: AdPlatform = AdPlatform.ALL
    start_date: datetime
    end_date: datetime
    is_active: bool = True

class AdCreate(AdBase):
    pass

class AdUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    target_link: Optional[str] = None
    platform: Optional[AdPlatform] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class AdResponse(AdBase):
    id: UUID
    ad_type: AdType
    impressions: int
    clicks: int
    spend: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
