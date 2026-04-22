from typing import Any, List
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from app.api import deps
from app.core import security
from app.models.user import User, UserRole
from app.schemas.auth import UserCreateAdmin, UserResponse
from app.schemas.user import UserUpdate
import logging

logger = logging.getLogger(__name__)
security_logger = logging.getLogger("security")

from app.utils.cache_invalidation import invalidate_user_cache

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Retrieve users.
    """
    users = await User.find_all().skip(skip).limit(limit).to_list()
    return users

@router.post("/", response_model=UserResponse)
async def create_user(
    *,
    user_in: UserCreateAdmin,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Create new user.
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

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    *,
    user_id: UUID,
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update a user.
    """
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    if user_in.password:
        user.hashed_password = security.get_password_hash(user_in.password)
    
    if user_in.email:
        existing_user = await User.find_one({"email": user_in.email})
        if existing_user and existing_user.id != user_id:
             raise HTTPException(
                status_code=400,
                detail="A user with this email already exists",
            )
        user.email = user_in.email

    if user_in.full_name:
        user.full_name = user_in.full_name
    if user_in.role:
        user.role = user_in.role
    if user_in.is_active is not None:
        user.is_active = user_in.is_active
        
    await user.save()

    # Invalidate user cache
    await invalidate_user_cache(user.id)

    return user

@router.get("/{user_id}", response_model=UserResponse)
async def read_user_by_id(
    user_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get a specific user by id.
    """
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    return user

@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(
    *,
    user_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Delete a user.
    Only SUPER_ADMIN can delete admin users.
    Users cannot delete themselves.
    """
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # Prevent self-deletion
    if user.id == current_user.id:
        security_logger.warning(f"User {current_user.email} attempted to delete their own account")
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own account"
        )

    # Only SUPER_ADMIN can delete other admins
    if user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        if current_user.role != UserRole.SUPER_ADMIN:
            security_logger.warning(
                f"User {current_user.email} (role: {current_user.role}) attempted to delete admin user {user.email}"
            )
            raise HTTPException(
                status_code=403,
                detail="Only super admins can delete admin users"
            )

    user.is_deleted = True
    user.is_active = False
    user.deleted_at = datetime.utcnow()
    await user.save()

    # Invalidate user cache
    await invalidate_user_cache(user.id)

    logger.info(f"User {user.email} (ID: {user.id}) soft-deleted by {current_user.email}")
    security_logger.info(f"User soft-deletion: {user.email} by {current_user.email}")
    return user

@router.patch("/{user_id}/suspend", response_model=UserResponse)
async def suspend_user(
    *,
    user_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Suspend a user (set is_active=False).
    """
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    user.is_active = False
    await user.save()

    # Invalidate user cache
    await invalidate_user_cache(user.id)

    return user

@router.patch("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    *,
    user_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Activate a user (set is_active=True).
    """
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    user.is_active = True
    await user.save()

    # Invalidate user cache
    await invalidate_user_cache(user.id)

    return user
