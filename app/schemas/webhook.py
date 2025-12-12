from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, HttpUrl

class WebhookCreate(BaseModel):
    url: HttpUrl
    events: List[str]
    secret_token: Optional[str] = None

class WebhookResponse(BaseModel):
    id: UUID
    developer_id: UUID
    url: HttpUrl
    events: List[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
