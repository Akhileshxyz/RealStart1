from typing import Any
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api import deps
from app.core import security
from app.models.user import User, UserRole
from app.models.developer import Developer
from app.schemas.auth import Token, UserCreate, UserResponse
from app.schemas.developer import DeveloperCreate, DeveloperResponse

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/register", response_model=UserResponse)
async def register_public_user(user_in: UserCreate) -> Any:
    """
    Create a new user (Public Portal).
    Public users can only register as BUYER role.
    Admin/SuperAdmin roles must be created via admin endpoints only.
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
        role=UserRole.BUYER,
        is_active=True,
    )
    await user.insert()
    return user

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """


    user = await User.find_one({"email": form_data.username})

    # Generic error message to prevent user enumeration
    if not user or not security.verify_password(form_data.password, user.hashed_password) or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    return {
        "access_token": security.create_access_token(user.id),
        "token_type": "bearer",
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user
    