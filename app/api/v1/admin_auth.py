from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.core import security
from app.models.user import User, UserRole
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.api import deps
from app.core import security
from app.models.user import User, UserRole
from app.schemas.auth import UserCreateAdmin, UserResponse, Token

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/register-admin", response_model=UserResponse)
async def register_admin_user(
    user_in: UserCreateAdmin,
    current_superuser: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a new admin/manager.
    Only accessible by existing Super Admin.
    Can create users with any role including ADMIN and SUPER_ADMIN.
    """
    user = await User.find_one({"email": user_in.email})
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )

    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=True,
    )
    await user.insert()
    return user

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_admin_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login for Privileged Users (Admin, Developer, Lawyer, etc.).
    Restricted: BUYER role cannot login here.
    """
    user = await User.find_one({"email": form_data.username})

    # Generic error message
    if not user or not security.verify_password(form_data.password, user.hashed_password) or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Restrict Admin Login: BUYERS cannot login here
    if user.role == UserRole.BUYER:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Buyers must use the public portal."
        )

    return {
        "access_token": security.create_access_token(user.id),
        "token_type": "bearer",
    }
