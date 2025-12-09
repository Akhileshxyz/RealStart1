from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from app.core import security
from app.core.config import settings
from app.models.user import User, UserRole
from app.schemas.auth import TokenPayload

# Two distinct OAuth2 schemes if needed, or one shared logic
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user = await User.get(token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_current_active_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
         raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_current_user_optional(token: str = Depends(oauth2_scheme)) -> Optional[User]:
    try:
        user = await get_current_user(token)
        return user
    except HTTPException:
        return None
