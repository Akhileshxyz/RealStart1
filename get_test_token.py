import asyncio
import jwt
import sys
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.db.mongodb import init_db
from app.models.user import User

async def get_admin_token():
    await init_db()
    email = "admin@realstart.com"
    user = await User.find_one({"email": email})
    if not user:
        print(f"User {email} not found")
        return None
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode = {"exp": expire, "sub": str(user.id)}
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

if __name__ == "__main__":
    token = asyncio.run(get_admin_token())
    if token:
        print(f"TOKEN:{token}")
