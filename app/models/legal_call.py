from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from typing import List, Optional
from beanie import Document, Indexed
from pydantic import Field

class LegalCallStatus(str, Enum):
    OPEN = "OPEN"
    ACCEPTED = "ACCEPTED"
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class LegalCallRequest(Document):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    project_id: UUID
    
    topics: List[str] = Field(default_factory=list)
    scheduled_time: Optional[datetime] = None
    
    status: LegalCallStatus = LegalCallStatus.OPEN
    
    # Lawyer Inputs
    lawyer_notes: Optional[str] = None
    opinion_file_url: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Settings:
        name = "legal_call_requests"
