from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from beanie import Document, Indexed
from pydantic import Field, EmailStr

class Developer(Document):
    id: UUID = Field(default_factory=uuid4)
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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "developers"
