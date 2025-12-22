from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from typing import Optional
from beanie import Document
from pydantic import Field

class CommunicationType(str, Enum):
    CALL = "CALL"
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    MEETING = "MEETING"

class ProjectCommunication(Document):
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    admin_id: UUID  # User ID of the admin logging this
    type: CommunicationType = CommunicationType.CALL
    summary: str
    details: Optional[str] = None
    outcome: Optional[str] = None
    
    date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "project_communications"
