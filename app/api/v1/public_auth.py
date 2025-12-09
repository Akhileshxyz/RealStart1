from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api import deps
from app.core import security
from app.models.user import User, UserRole
from app.models.developer import Developer
from app.schemas.auth import Token, UserCreate, UserResponse
from app.schemas.developer import DeveloperCreate, DeveloperResponse

router = APIRouter()

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
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await User.find_one({"email": form_data.username})
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not user.is_active:
         raise HTTPException(status_code=400, detail="Inactive user")

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

@router.post("/register-developer", response_model=DeveloperResponse)
async def register_developer_public(developer_in: DeveloperCreate) -> Any:
    """
    Register as a developer (Public Portal).
    Developers need admin verification before being activated.
    """
    if developer_in.contact_email:
        existing = await Developer.find_one({"contact_email": developer_in.contact_email})
        if existing:
            raise HTTPException(
                status_code=400,
                detail="A developer with this email already exists",
            )

    developer = Developer(
        **developer_in.model_dump(),
        is_verified=False,
        is_active=False
    )
    await developer.insert()
    return developer
