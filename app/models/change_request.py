from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Dict, Any
from enum import Enum
from beanie import Document
from pydantic import Field

class RequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class RequestType(str, Enum):
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class ProjectChangeRequest(Document):
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    request_type: RequestType
    data: Optional[Dict[str, Any]] = None  # For UPDATE requests
    status: RequestStatus = RequestStatus.PENDING
    admin_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "project_change_requests"
