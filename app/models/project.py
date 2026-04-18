from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List, Any, Union
from enum import Enum
from beanie import Document, Indexed
from pydantic import Field, BaseModel, field_validator
from app.utils.parsers import parse_price_string

class LegalDocumentStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    NEEDS_UPDATE = "NEEDS_UPDATE"

class LegalDocumentType(str, Enum):
    RERA_CERT = "RERA_CERT"
    APPROVED_PLAN = "APPROVED_PLAN"
    SALE_DEED = "SALE_DEED"
    MOTHER_DEED = "MOTHER_DEED"
    ENCUMBRANCE_CERT = "ENCUMBRANCE_CERT"
    OTHER = "OTHER"

class LegalCompliance(BaseModel):
    is_rera_registered: bool = False
    has_approved_plan: bool = False
    has_clear_title: bool = False

class LegalDocument(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str # e.g., "RERA Certificate"
    type: LegalDocumentType = LegalDocumentType.OTHER
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

class PropertyType(str, Enum):
    RESIDENTIAL_APARTMENT = "Residential apartment"
    VILLA = "Villa"
    PLOTS = "Plots"
    COMMERCIAL = "Commercial"
    ROW_HOUSE = "Row House"

class Project(Document):
    id: UUID = Field(default_factory=uuid4)
    developer_id: UUID
    lawyer_id: Optional[UUID] = None
    city_id: Optional[UUID] = None
    zone_id: Optional[UUID] = None
    landmark_id: Optional[UUID] = None # Linked Locality
    
    name: str
    slug: str = Indexed(unique=True)
    description: Optional[str] = None
    
    # Approval Details
    status: ProjectStatus = ProjectStatus.PENDING
    approval_type: Optional[ProjectAppovalType] = None
    rera_number: Optional[str] = None
    
    # Location
    address: Optional[str] = None # Legacy/Full Address
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    landmark: Optional[str] = None # Descriptive landmark text
    google_maps_link: Optional[str] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Metadata
    property_type: Optional[PropertyType] = None
    launch_year: Optional[int] = None
    total_area_sqft: Optional[float] = None
    number_of_units: Optional[int] = None
    total_units: Optional[int] = None
    available_units: Optional[int] = None
    sold_units: Optional[int] = None
    
    # Price
    min_price: Optional[Union[float, str]] = None
    max_price: Optional[Union[float, str]] = None
    
    # Other
    possession_date: Optional[datetime] = None
    video_url: Optional[str] = None
    brochure_url: Optional[str] = None
    gallery_images: List[str] = Field(default_factory=list)

    # Features
    amenities: List[str] = Field(default_factory=list)
    special_features: List[str] = Field(default_factory=list)
    nearby_facilities: List[str] = Field(default_factory=list)

    is_hidden: bool = False
    hidden_at: Optional[datetime] = None
    is_featured: bool = False  # Shown on homepage Featured section
    is_active: bool = True # For soft delete
    
    # Legal / Documents
    documents: List[LegalDocument] = Field(default_factory=list)
    legal_compliance: LegalCompliance = Field(default_factory=LegalCompliance)
    legal_status_summary: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "projects"
