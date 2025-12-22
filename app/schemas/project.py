from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.models.project import ProjectStatus, ProjectAppovalType, LegalDocumentStatus

# Legal Document Schemas
class LegalDocumentCreate(BaseModel):
    name: str
    file_url: str

class LegalDocumentResponse(BaseModel):
    id: UUID
    name: str
    file_url: str
    status: LegalDocumentStatus
    lawyer_notes: Optional[str] = None
    verified_at: Optional[datetime] = None

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
    developer_id: Optional[UUID] = None # Inferred from auth
    documents: Optional[List[LegalDocumentCreate]] = None

# Update by Developer
class ProjectUpdate(ProjectBase):
    documents: Optional[List[LegalDocumentCreate]] = None

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
    documents: List[LegalDocumentResponse] = []
    legal_status_summary: Optional[str] = None
    
    # Enhanced Fields
    owner_name: Optional[str] = None
    owner_email: Optional[str] = None
    owner_phone: Optional[str] = None
    subscription_end_date: Optional[datetime] = None
    subscription_plan_name: Optional[str] = None

    class Config:
        from_attributes = True
