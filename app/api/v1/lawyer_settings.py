from typing import Any
from fastapi import APIRouter, Depends, Body, HTTPException
from app.api import deps
from app.models.user import User
from app.models.lawyer import LawyerProfile
from datetime import datetime
from app.schemas.lawyer_portal import (
    LawyerSettingsData, LawyerProfileData, NotificationPreference, LawyerProfileUpdate
)

router = APIRouter()

async def get_lawyer_profile(user: User) -> LawyerProfile:
    # Fallback to user_id if linked id not set
    profile = await LawyerProfile.find_one(LawyerProfile.user_id == user.id)
    if not profile:
        profile = LawyerProfile(user_id=user.id)
        await profile.insert()
        user.lawyer_profile_id = profile.id
        await user.save()
    return profile

@router.get("/settings", response_model=LawyerSettingsData)
async def get_settings(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    profile_db = await get_lawyer_profile(current_user)
    
    profile_data = LawyerProfileData(
        full_name=current_user.full_name or "Advocate",
        email=current_user.email,
        phone=current_user.phone or "",
        bar_council_number=profile_db.bar_council_id,
        specialization=profile_db.specialization,
        experience=profile_db.experience_years,
        city=profile_db.cities[0] if profile_db.cities else None,
        office_address=profile_db.office_address,
        bio=profile_db.bio,
        working_days=profile_db.working_days,
        working_hours=profile_db.working_hours,
    )
    
    pref_definitions = [
        {"id": "email_notifications", "label": "Email Notifications", "description": "Receive notifications via email"},
        {"id": "case_updates", "label": "Case Updates", "description": "Get notified about case status changes"},
        {"id": "schedule_reminders", "label": "Schedule Reminders", "description": "Receive reminders for upcoming events"},
        {"id": "client_requests", "label": "Client Requests", "description": "Get notified about new client inquiries"},
    ]
    prefs = []
    for pref in pref_definitions:
        prefs.append(
            NotificationPreference(
                id=pref["id"],
                label=pref["label"],
                description=pref["description"],
                enabled=profile_db.notification_preferences.get(pref["id"], True),
            )
        )

    return LawyerSettingsData(
        profile=profile_data,
        notification_preferences=prefs
    )

@router.patch("/settings/profile")
async def update_profile(
    profile_in: LawyerProfileUpdate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    profile_db = await get_lawyer_profile(current_user)
    
    # Update User fields if provided
    user_updated = False
    if profile_in.full_name is not None:
        current_user.full_name = profile_in.full_name
        user_updated = True
    if profile_in.phone is not None:
        current_user.phone = profile_in.phone
        user_updated = True
    
    if user_updated:
        await current_user.save()

    # Update Profile fields
    if profile_in.bio is not None: 
        profile_db.bio = profile_in.bio
    if profile_in.specialization is not None: 
        profile_db.specialization = profile_in.specialization
    if profile_in.bar_council_number is not None: 
        profile_db.bar_council_id = profile_in.bar_council_number
    if profile_in.experience is not None: 
        profile_db.experience_years = profile_in.experience
    if profile_in.city is not None: 
        profile_db.cities = [profile_in.city]
    if profile_in.office_address is not None:
        profile_db.office_address = profile_in.office_address
    if profile_in.working_days is not None: 
        profile_db.working_days = profile_in.working_days
    if profile_in.working_hours is not None: 
        profile_db.working_hours = profile_in.working_hours
    if profile_in.notification_preferences is not None:
        profile_db.notification_preferences = profile_in.notification_preferences
        
    profile_db.updated_at = datetime.utcnow()
    await profile_db.save()
    
    return {"message": "Profile updated successfully"}
