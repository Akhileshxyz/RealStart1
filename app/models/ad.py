from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Dict, Any
from enum import Enum
from beanie import Document
from pydantic import Field

class AdType(str, Enum):
    INTERNAL = "INTERNAL"
    EXTERNAL_META = "EXTERNAL_META"
    EXTERNAL_GOOGLE = "EXTERNAL_GOOGLE"

class AdPlatform(str, Enum):
    MOBILE_APP = "MOBILE_APP"
    WEB = "WEB"
    ALL = "ALL"

class Ad(Document):
    id: UUID = Field(default_factory=uuid4)
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    target_link: Optional[str] = None
    
    ad_type: AdType = AdType.INTERNAL
    platform: AdPlatform = AdPlatform.ALL
    
    start_date: datetime
    end_date: datetime
    
    # Performance Metrics
    impressions: int = 0
    clicks: int = 0
    spend: float = 0.0 # For external ads
    
    is_active: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "ads"
