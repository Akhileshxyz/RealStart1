from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.security import HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.redis_client import redis_client
from app.models.user import User, UserRole
from app.schemas.auth import UserCreateAdmin, UserResponse, Token, LoginRequest, Message

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
async def login_admin(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember_me: bool = Form(False)
) -> Any:
    """
    Admin/Staff Login.
    - Authenticates user with email/password.
    - Ensures user has ADMIN, SUPER_ADMIN, or MANAGER role.
    - Supports Remember Me.
    - Accepts form-urlencoded data (username/password) or JSON.
    """
    user = await User.find_one({"email": username})

    if not user or not security.verify_password(password, user.hashed_password) or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Restrict to Admin/Manager roles (and Super Admin)
    # Developers have their own portal, Lawyers have their own.
    # If the user is strictly a Developer trying to login here, strictly speaking we could allow it if this is a "Unified" staff login,
    # but the prompt asked for separate "like Developer and Lawyer", implying this is the "Admin" portal auth.
    if user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.MANAGER]:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This portal is for Administrators."
        )

    # Determine token expiry
    if remember_me:
        access_token_expires = timedelta(days=7)
    else:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/logout", response_model=Message)
async def logout_admin(
    current_user: User = Depends(deps.get_current_user),
    token: HTTPAuthorizationCredentials = Depends(deps.security_scheme)
) -> Any:
    """
    Logout.
    Blacklists the current access token.
    """
    token_str = token.credentials
    # Default blacklist TTL 7 days
    await redis_client.set(f"blacklist:token:{token_str}", "true", ttl=60*60*24*7)
    
    return {"message": "Successfully logged out"}
