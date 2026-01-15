from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from typing import List, Optional
from beanie import Document, Link
from pydantic import Field
from app.models.user import User

class LeadStatus(str, Enum):
    VIEWED = "VIEWED"
    CONTACTED = "CONTACTED"
    PURCHASED = "PURCHASED"
    NOT_INTERESTED = "NOT_INTERESTED"

class ProjectLead(Document):
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    user_id: UUID

    status: LeadStatus = LeadStatus.VIEWED

    # Tracking view history
    viewed_at_history: List[datetime] = Field(default_factory=list)
    last_viewed_at: datetime = Field(default_factory=datetime.utcnow)

    # Wishlist tracking
    is_wishlisted: bool = False
    wishlisted_at: Optional[datetime] = None

    # Legal request tracking
    is_legal_requested: bool = False
    legal_requested_at: Optional[datetime] = None

    # Visit tracking
    visit_booked_at: Optional[datetime] = None
    visit_status: Optional[str] = None  # "BOOKED", "COMPLETED", "CANCELLED"

    # Anonymous tracking
    is_anonymous: bool = True

    # Analytics/Source
    source: Optional[str] = "Direct"  # e.g., "Direct", "Google", "Social", "Referral"
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Notes by developer
    developer_notes: Optional[str] = None

    class Settings:
        name = "project_leads"
