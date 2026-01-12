from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Optional
from beanie import Document
from pydantic import Field, HttpUrl

class WebhookSubscription(Document):
    id: UUID = Field(default_factory=uuid4)
    developer_id: UUID
    url: str
    events: List[str] = []  # e.g., ["lead.wishlist", "lead.legal_request", "lead.visit_booked"]
    secret_token: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "webhook_subscriptions"
