from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import ValidationError
from app.core import security
from app.core.config import settings
from app.core.redis_client import redis_client
from app.models.user import User, UserRole
from app.schemas.auth import TokenPayload

# HTTPBearer scheme for Swagger UI
security_scheme = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> User:
    token = credentials.credentials
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

    # TIER 1 CRITICAL CACHING: Try to get user from cache first
    cache_key = redis_client.make_key("user", "id", str(token_data.sub))
    cached_user = await redis_client.get(cache_key)

    if cached_user:
        # Reconstruct User object from cached data
        user = User(**cached_user)
    else:
        # Cache miss - fetch from database
        user = await User.get(token_data.sub)
        if user:
            # Cache user object for future requests
            user_dict = user.model_dump()
            await redis_client.set(cache_key, user_dict, settings.REDIS_CACHE_TTL_USER)

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

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)) -> Optional[User]:
    try:
        token = credentials.credentials
        user = await get_current_user(credentials)
        return user
    except HTTPException:
        return None
