from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.models.change_request import RequestStatus, RequestType

class ChangeRequestResponse(BaseModel):
    id: UUID
    project_id: UUID
    project_name: Optional[str] = None
    developer_name: Optional[str] = None
    request_type: RequestType
    data: Optional[Dict[str, Any]] = None
    status: RequestStatus
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
