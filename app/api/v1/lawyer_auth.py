from datetime import timedelta
from typing import Any
import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPAuthorizationCredentials

from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.redis_client import redis_client
from app.models.user import User, UserRole
from app.schemas.auth import (
    LoginRequest,
    Token,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    Message
)

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_lawyer(
    username: str = Form(...),
    password: str = Form(...),
    remember_me: bool = Form(False)
) -> Any:
    """
    Lawyer Login.
    - Authenticates user with email/password.
    - Ensures user has LAWYER role.
    - Supports Remember Me (7 days expiry vs standard).
    - Accepts form-urlencoded data (username/password) or JSON.
    """
    user = await User.find_one({"email": username})

    if not user or not security.verify_password(password, user.hashed_password) or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if user.role != UserRole.LAWYER:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only Lawyers can login here."
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
async def logout_lawyer(
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

@router.post("/forgot-password", response_model=Message)
async def forgot_password(
    request: ForgotPasswordRequest
) -> Any:
    """
    Initiate Password Reset.
    Generates a reset token and (mocks) sending an email.
    """
    user = await User.find_one({"email": request.email})
    if not user:
        return {"message": "If an account exists with this email, a password reset link has been sent."}
    
    # Generate reset token (short lived, e.g., 1 hour)
    reset_token_expires = timedelta(hours=1)
    reset_token = security.create_access_token(
        subject=user.email,
        expires_delta=reset_token_expires
    )
    
    # Mock Email Sending
    print(f"DEBUG: Password Reset Token for {user.email}: {reset_token}")

    return {"message": "If an account exists with this email, a password reset link has been sent."}

@router.post("/reset-password", response_model=Message)
async def reset_password(
    request: ResetPasswordRequest
) -> Any:
    """
    Reset Password using token.
    """
    try:
        payload = jwt.decode(
            request.token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")
            
    except (jwt.InvalidTokenError, Exception):
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = await User.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = security.get_password_hash(request.new_password)
    await user.save()

    return {"message": "Password updated successfully"}
