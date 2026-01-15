from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.core import security
from app.models.user import User, UserRole
from app.models.user_preferences import UserNotificationPreferences
from app.schemas.auth import PasswordChange, UserResponse
from app.schemas.admin_settings import (
    ProfileUpdate,
    UserProfileResponse,
    NotificationPreferences,
    NotificationPreferencesUpdate,
    UserSettingsResponse
)
from app.utils.cache_invalidation import invalidate_user_cache
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
security_logger = logging.getLogger("security")

router = APIRouter()


# ==================== PROFILE MANAGEMENT ====================

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user's profile.
    
    Returns detailed profile information including:
    - Email, full name, phone
    - Role and active status
    - Account creation date
    """
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        role=current_user.role.value,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


@router.patch("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update user profile information.
    
    Allows updating:
    - Full name
    - Phone number
    
    Note: Email cannot be changed through this endpoint for security reasons.
    """
    # Update fields if provided
    if profile_update.full_name is not None:
        current_user.full_name = profile_update.full_name
    
    if profile_update.phone is not None:
        current_user.phone = profile_update.phone
    
    await current_user.save()
    
    # Invalidate cache
    await invalidate_user_cache(current_user.id)
    
    logger.info(f"Profile updated for user {current_user.email}")
    
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        role=current_user.role.value,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


# ==================== PASSWORD MANAGEMENT ====================

@router.patch("/change-password", response_model=UserResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Change password for the currently authenticated user.
    
    Requirements:
    - Must provide correct old password
    - New password must meet security requirements
    - New password must be different from old password
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


# ==================== NOTIFICATION PREFERENCES ====================

@router.get("/notifications", response_model=NotificationPreferences)
async def get_notification_preferences(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get user notification preferences.
    
    Returns settings for:
    - Email notifications
    - Subscription reminders
    - New developer alerts
    - Payment alerts
    - System updates
    """
    # Get or create preferences
    prefs = await UserNotificationPreferences.find_one({"user_id": current_user.id})
    
    if not prefs:
        # Create default preferences
        prefs = UserNotificationPreferences(
            user_id=current_user.id,
            email_notifications=True,
            subscription_reminders=True,
            new_developer_alerts=True,
            payment_alerts=True,
            system_updates=True
        )
        await prefs.insert()
    
    return NotificationPreferences(
        email_notifications=prefs.email_notifications,
        subscription_reminders=prefs.subscription_reminders,
        new_developer_alerts=prefs.new_developer_alerts,
        payment_alerts=prefs.payment_alerts,
        system_updates=prefs.system_updates
    )


@router.patch("/notifications", response_model=NotificationPreferences)
async def update_notification_preferences(
    preferences_update: NotificationPreferencesUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update user notification preferences.
    
    Allows selective updates to any notification setting.
    Only provided fields will be updated.
    """
    # Get or create preferences
    prefs = await UserNotificationPreferences.find_one({"user_id": current_user.id})
    
    if not prefs:
        prefs = UserNotificationPreferences(user_id=current_user.id)
        await prefs.insert()
    
    # Update fields if provided
    if preferences_update.email_notifications is not None:
        prefs.email_notifications = preferences_update.email_notifications
    
    if preferences_update.subscription_reminders is not None:
        prefs.subscription_reminders = preferences_update.subscription_reminders
    
    if preferences_update.new_developer_alerts is not None:
        prefs.new_developer_alerts = preferences_update.new_developer_alerts
    
    if preferences_update.payment_alerts is not None:
        prefs.payment_alerts = preferences_update.payment_alerts
    
    if preferences_update.system_updates is not None:
        prefs.system_updates = preferences_update.system_updates
    
    prefs.updated_at = datetime.utcnow()
    await prefs.save()
    
    logger.info(f"Notification preferences updated for user {current_user.email}")
    
    return NotificationPreferences(
        email_notifications=prefs.email_notifications,
        subscription_reminders=prefs.subscription_reminders,
        new_developer_alerts=prefs.new_developer_alerts,
        payment_alerts=prefs.payment_alerts,
        system_updates=prefs.system_updates
    )


# ==================== COMBINED SETTINGS ====================

@router.get("/all", response_model=UserSettingsResponse)
async def get_all_settings(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get all user settings in one call.
    
    Returns:
    - Profile information
    - Notification preferences
    
    Useful for loading settings page in one request.
    """
    # Get profile
    profile = UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        role=current_user.role.value,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )
    
    # Get notification preferences
    prefs = await UserNotificationPreferences.find_one({"user_id": current_user.id})
    
    if not prefs:
        prefs = UserNotificationPreferences(
            user_id=current_user.id,
            email_notifications=True,
            subscription_reminders=True,
            new_developer_alerts=True,
            payment_alerts=True,
            system_updates=True
        )
        await prefs.insert()
    
    notifications = NotificationPreferences(
        email_notifications=prefs.email_notifications,
        subscription_reminders=prefs.subscription_reminders,
        new_developer_alerts=prefs.new_developer_alerts,
        payment_alerts=prefs.payment_alerts,
        system_updates=prefs.system_updates
    )
    
    return UserSettingsResponse(
        profile=profile,
        notifications=notifications
    )
