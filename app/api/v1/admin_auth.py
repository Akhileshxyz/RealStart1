from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.core import security
from app.models.user import User, UserRole
from app.schemas.auth import UserCreateAdmin, UserResponse

router = APIRouter()

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
