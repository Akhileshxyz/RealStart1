from typing import Any
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from app.api import deps
from app.core import security
from app.core.redis_client import redis_client
from app.models.user import User, UserRole
from app.schemas.auth import TokenWithUser, UserResponse, CompleteProfileRequest
from app.services.otp_service import send_otp, verify_otp
import re

router = APIRouter()

class SendOTPRequest(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        cleaned = re.sub(r"\s+", "", v)
        if not re.match(r"^\+?\d{7,15}$", cleaned):
            raise ValueError("Invalid phone number format")
        return cleaned

class VerifyOTPRequest(BaseModel):
    phone: str
    session_id: str
    otp: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        cleaned = re.sub(r"\s+", "", v)
        if not re.match(r"^\+?\d{7,15}$", cleaned):
            raise ValueError("Invalid phone number format")
        return cleaned

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, v):
        if not re.match(r"^\d{4,8}$", v.strip()):
            raise ValueError("OTP must be 4-8 digits")
        return v.strip()

def normalize_phone(phone: str) -> str:
    return re.sub(r"\s+", "", phone)

@router.post("/send-otp")
async def send_otp_endpoint(req: SendOTPRequest) -> Any:
    phone = normalize_phone(req.phone)
    try:
        session_id = await send_otp(phone)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )

    await redis_client.set(f"otp_session:{phone}", session_id, ttl=300)

    return {"message": "OTP sent successfully", "session_id": session_id}

@router.post("/verify-otp", response_model=TokenWithUser)
async def verify_otp_endpoint(req: VerifyOTPRequest) -> Any:
    phone = normalize_phone(req.phone)

    is_valid = await verify_otp(req.session_id, req.otp)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    user = await User.find_one({"phone": phone})

    if not user:
        phone_suffix = phone[-4:] if len(phone) >= 4 else phone
        placeholder_email = f"{phone.replace('+', '')}@otp.realstart.app"
        user = User(
            phone=phone,
            email=placeholder_email,
            hashed_password=security.get_password_hash(str(uuid4())),
            full_name=f"User {phone_suffix}",
            role=UserRole.BUYER,
            is_active=True,
        )
        await user.insert()

    from app.models.lead import ProjectLead
    leads = await ProjectLead.find(
        ProjectLead.user_id == user.id,
        ProjectLead.is_wishlisted == True
    ).to_list()

    saved_properties = [lead.project_id for lead in leads]
    is_complete = not user.email.endswith("@otp.realstart.app")

    return {
        "access_token": security.create_access_token(user.id),
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            is_profile_complete=is_complete,
            saved_properties=saved_properties
        )
    }


@router.post("/complete-profile", response_model=TokenWithUser)
async def complete_profile(
    req: CompleteProfileRequest,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    if not current_user.email.endswith("@otp.realstart.app"):
        raise HTTPException(status_code=400, detail="Profile is already complete")

    existing = await User.find_one({"email": req.email})
    if existing and existing.id != current_user.id:
        raise HTTPException(status_code=400, detail="Email already in use")

    current_user.full_name = req.full_name
    current_user.email = req.email
    current_user.hashed_password = security.get_password_hash(req.password)
    await current_user.save()

    from app.models.lead import ProjectLead
    leads = await ProjectLead.find(
        ProjectLead.user_id == current_user.id,
        ProjectLead.is_wishlisted == True
    ).to_list()

    saved_properties = [lead.project_id for lead in leads]

    return {
        "access_token": security.create_access_token(current_user.id),
        "token_type": "bearer",
        "user": UserResponse(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            role=current_user.role,
            is_active=current_user.is_active,
            is_profile_complete=True,
            saved_properties=saved_properties
        )
    }
