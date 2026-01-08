from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.models.project import ProjectStatus, ProjectAppovalType, LegalDocumentStatus, PropertyType

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

    class Config:
        from_attributes = True

# Shared Properties
class ProjectBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    approval_type: Optional[ProjectAppovalType] = None
    rera_number: Optional[str] = None
    address: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    landmark: Optional[str] = None
    google_maps_link: Optional[str] = None
    
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    landmark_id: Optional[UUID] = None
    
    launch_year: Optional[int] = None
    property_type: Optional[PropertyType] = None
    total_area_sqft: Optional[float] = None
    number_of_units: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    possession_date: Optional[datetime] = None
    video_url: Optional[str] = None

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
    landmark_id: Optional[UUID] = None
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
