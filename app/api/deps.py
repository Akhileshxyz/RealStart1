from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import ValidationError
from app.core import security
from app.core.config import settings
from app.core.config import settings
from app.models.user import User, UserRole
from app.schemas.auth import TokenPayload

# HTTPBearer scheme for Swagger UI
security_scheme = HTTPBearer()
optional_security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> User:
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    # Fetch from database (Cache removed)
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

async def get_current_active_team_member(
    current_user: User = Depends(get_current_user),
) -> User:
    # Admin and team members (SALES, MARKETING, MANAGER, ADMIN, SUPER_ADMIN)
    if current_user.role not in [
        UserRole.ADMIN, 
        UserRole.SUPER_ADMIN, 
        UserRole.SALES, 
        UserRole.MARKETING, 
        UserRole.MANAGER
    ]:
         raise HTTPException(
            status_code=403, detail="Only admin and team members can perform this action"
        )
    return current_user

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security_scheme)) -> Optional[User]:
    if not credentials:
        return None
    try:
        user = await get_current_user(credentials)
        return user
    except HTTPException:
        return None
