from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from enum import Enum
from beanie import Document, Indexed
from typing import Optional, List
from enum import Enum
from beanie import Document, Indexed
from pydantic import Field, BaseModel

class LegalDocumentStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    NEEDS_UPDATE = "NEEDS_UPDATE"

class LegalDocument(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str # e.g., "RTC", "EC"
    file_url: str
    status: LegalDocumentStatus = LegalDocumentStatus.PENDING
    lawyer_notes: Optional[str] = None
    verified_at: Optional[datetime] = None

class ProjectStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DRAFT = "DRAFT"
    DELETED = "DELETED"

class ProjectAppovalType(str, Enum):
    RERA = "RERA"
    DTCP = "DTCP"
    PANCHAYAT = "PANCHAYAT"
    OTHER = "OTHER"

class Project(Document):
    id: UUID = Field(default_factory=uuid4)
    developer_id: UUID
    city_id: Optional[UUID] = None
    zone_id: Optional[UUID] = None
    landmark_id: Optional[UUID] = None # Linked Locality
    
    name: str
    slug: Indexed(str, unique=True)
    description: Optional[str] = None
    
    # Approval Details
    status: ProjectStatus = ProjectStatus.PENDING
    approval_type: Optional[ProjectAppovalType] = None
    rera_number: Optional[str] = None
    
    # Location
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Metadata
    launch_year: Optional[int] = None
    total_area_sqft: Optional[float] = None
    is_hidden: bool = False
    hidden_at: Optional[datetime] = None
    is_active: bool = True # For soft delete
    
    # Legal / Documents
    documents: List[LegalDocument] = Field(default_factory=list)
    legal_status_summary: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "projects"
