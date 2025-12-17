from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from enum import Enum
from beanie import Document, Indexed
from pydantic import Field

class ProjectStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DRAFT = "DRAFT"

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
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "projects"
