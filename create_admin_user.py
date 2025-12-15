import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.db.mongodb import init_db
from app.models.user import User, UserRole
from app.core.security import get_password_hash

async def create_user():
    await init_db()
    
    email = "admin@realtech.in"
    password = "admin"
    
    existing_user = await User.find_one({"email": email})
    if existing_user:
        print(f"User {email} already exists.")
        return

    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name="Admin User",
        role=UserRole.SUPER_ADMIN,
        is_active=True
    )
    await user.insert()
    print(f"User {email} created successfully with SUPER_ADMIN role.")

if __name__ == "__main__":
    asyncio.run(create_user())
