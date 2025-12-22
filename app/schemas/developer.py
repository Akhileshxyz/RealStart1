from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr

class DeveloperBase(BaseModel):
    name: str
    legal_name: Optional[str] = None
    owner_name: Optional[str] = None
    gst_number: Optional[str] = None
    rera_number: Optional[str] = None
    sub_developer: Optional[str] = None
    office_address: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    logo_url: Optional[str] = None
    about_text: Optional[str] = None
    is_verified: bool = False
    is_active: bool = True

class DeveloperCreate(DeveloperBase):
    pass

class DeveloperUpdate(BaseModel):
    name: Optional[str] = None
    legal_name: Optional[str] = None
    owner_name: Optional[str] = None
    gst_number: Optional[str] = None
    rera_number: Optional[str] = None
    sub_developer: Optional[str] = None
    office_address: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    logo_url: Optional[str] = None
    about_text: Optional[str] = None
    is_verified: Optional[bool] = None
    is_active: Optional[bool] = None

class DeveloperResponse(DeveloperBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Computed
    tenure: Optional[str] = None # e.g. "2 years, 3 months"

    class Config:
        from_attributes = True
