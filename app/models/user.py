from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from beanie import Document, Indexed
from pydantic import Field, EmailStr

class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    LAWYER = "LAWYER"
    BUYER = "BUYER"
    SALES = "SALES"
    MARKETING = "MARKETING"

class User(Document):
    id: UUID = Field(default_factory=uuid4)
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    full_name: str
    role: UserRole = UserRole.BUYER
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Optional Profile Fields can be added here or in separate collections
    # e.g., lawyer_profile_id: Optional[UUID] = None

    class Settings:
        name = "users"
