from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.models.project import ProjectStatus, ProjectAppovalType

# Shared Properties
class ProjectBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    approval_type: Optional[ProjectAppovalType] = None
    rera_number: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    launch_year: Optional[int] = None

# Creation by Developer (Status not allowed, defaults to PENDING)
class ProjectCreate(ProjectBase):
    name: str
    slug: str
    developer_id: UUID # In a real app, this might be inferred from auth, but passing it for now or we will handle it in the endpoint

# Update by Developer
class ProjectUpdate(ProjectBase):
    pass

# Update by Admin (Allows Status Change)
class ProjectAdminUpdate(ProjectBase):
    status: Optional[ProjectStatus] = None

# Response
class ProjectResponse(ProjectBase):
    id: UUID
    developer_id: UUID
    slug: str
    status: ProjectStatus
    is_hidden: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
