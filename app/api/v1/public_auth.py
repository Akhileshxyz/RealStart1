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
from app.models.lead import ProjectLead
from app.core.redis_client import redis_client
from fastapi.security import HTTPAuthorizationCredentials
from app.schemas.auth import Token, TokenWithUser, UserCreate, UserResponse, Message
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

@router.post("/login", response_model=TokenWithUser)
@limiter.limit("5/minute")
async def login_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Returns access token along with user profile information including role.
    """


    user = await User.find_one({"email": form_data.username})

    # Generic error message to prevent user enumeration
    if not user or not security.verify_password(form_data.password, user.hashed_password) or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Restrict Public Login to BUYERS only
    if user.role != UserRole.BUYER:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden from this portal. Please use the administrative portal."
        )

    leads = await ProjectLead.find(
        ProjectLead.user_id == user.id,
        ProjectLead.is_wishlisted == True
    ).to_list()
    
    saved_properties = [lead.project_id for lead in leads]

    return {
        "access_token": security.create_access_token(user.id),
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            saved_properties=saved_properties
        )
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    leads = await ProjectLead.find(
        ProjectLead.user_id == current_user.id,
        ProjectLead.is_wishlisted == True
    ).to_list()
    
    saved_properties = [lead.project_id for lead in leads]
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        saved_properties=saved_properties
    )

@router.post("/logout", response_model=Message)
async def logout_public_user(
    current_user: User = Depends(deps.get_current_user),
    token: HTTPAuthorizationCredentials = Depends(deps.security_scheme)
) -> Any:
    """
    Logout.
    Blacklists the current access token in Redis.
    """
    token_str = token.credentials
    # Default blacklist TTL 7 days (604800 seconds)
    await redis_client.set(f"blacklist:token:{token_str}", "true", ttl=60*60*24*7)
    
    return {"message": "Successfully logged out"}
    