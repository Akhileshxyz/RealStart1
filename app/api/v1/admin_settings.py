from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.core import security
from app.models.user import User
from app.schemas.auth import PasswordChange, UserResponse
from app.utils.cache_invalidation import invalidate_user_cache
import logging

logger = logging.getLogger(__name__)
security_logger = logging.getLogger("security")

router = APIRouter()


@router.patch("/change-password", response_model=UserResponse)
async def change_password(
    *,
    password_data: PasswordChange,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Change password for the currently authenticated user.

    This unified endpoint works for all user types:
    - End users (buyers)
    - Developers
    - Admins
    - Super admins
    """
    # Verify old password
    if not security.verify_password(password_data.old_password, current_user.hashed_password):
        security_logger.warning(
            f"Failed password change attempt for user {current_user.email} - incorrect old password"
        )
        raise HTTPException(
            status_code=400,
            detail="Incorrect old password"
        )

    # Check that new password is different from old password
    if security.verify_password(password_data.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="New password must be different from old password"
        )

    # Update password
    current_user.hashed_password = security.get_password_hash(password_data.new_password)
    await current_user.save()

    # Invalidate user cache to force re-authentication
    await invalidate_user_cache(current_user.id)

    logger.info(f"Password changed successfully for user {current_user.email}")
    security_logger.info(f"Password changed: {current_user.email} (role: {current_user.role})")

    return current_user


@router.get("/profile", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user's profile.

    Works for all authenticated users regardless of role.
    """
    return current_user
