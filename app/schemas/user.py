from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole
from app.schemas.auth import UserCreateAdmin, UserResponse

# Properties to receive via API on update
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

# Using UserResponse from auth schema for reading
# Using UserCreateAdmin from auth schema for creation
