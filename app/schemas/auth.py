from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class UserAuth(BaseModel):
    email: EmailStr
    password: str

class UserCreate(UserAuth):
    full_name: str

class UserCreateAdmin(UserAuth):
    full_name: str
    role: UserRole

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True
