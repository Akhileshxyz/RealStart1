import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from app.db.mongodb import init_db
from app.models.user import User, UserRole
from app.models.developer import Developer
from app.core import security

async def seed_developer():
    print("Initializing Database...")
    await init_db()
    
    email = "developer@realstart.com"
    password = "developer123"
    
    # Check if user exists
    existing_user = await User.find_one(User.email == email)
    if existing_user:
        print(f"User {email} already exists.")
        if existing_user.role != UserRole.DEVELOPER:
            print("WARNING: User exists but is not a DEVELOPER role.")
        else:
             print("User is already a DEVELOPER.")
        return

    print(f"Creating new Developer User: {email}")
    
    # 1. Create Developer Profile
    developer_profile = Developer(
        name="RealStart Test Developer",
        legal_name="RealStart Developers Pvt Ltd",
        contact_email=email,
        is_verified=True,
        is_active=True
    )
    await developer_profile.insert()
    print(f"Created Developer Profile with ID: {developer_profile.id}")
    
    # 2. Create User linked to Developer
    hashed_password = security.get_password_hash(password)
    user = User(
        email=email,
        hashed_password=hashed_password,
        full_name="Test Developer User",
        role=UserRole.DEVELOPER,
        is_active=True,
        developer_id=developer_profile.id
    )
    await user.insert()
    print(f"Created User with ID: {user.id}")
    print("Seed Complete!")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_developer())
