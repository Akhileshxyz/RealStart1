import asyncio
import os
import sys
from uuid import uuid4

# Add project root to path
sys.path.append(os.getcwd())

from app.db.mongodb import init_db
from app.models.user import User, UserRole
from app.models.lawyer import LawyerProfile
from app.core import security

async def seed_lawyer():
    print("Initializing Database...")
    await init_db()
    
    email = "lawyer@realstart.com"
    password = "lawyer123"
    
    # Check if user exists
    existing_user = await User.find_one(User.email == email)
    if existing_user:
        print(f"User {email} already exists.")
        if existing_user.role != UserRole.LAWYER:
            print("WARNING: User exists but is not a LAWYER role.")
        else:
             print("User is already a LAWYER.")
        return

    print(f"Creating new Lawyer User: {email}")
    
    # Generate ID for user to link manually or insert user first
    # Strategy: Insert User first, then Profile, then update User
    
    hashed_password = security.get_password_hash(password)
    user = User(
        email=email,
        hashed_password=hashed_password,
        full_name="Test Lawyer User",
        role=UserRole.LAWYER,
        is_active=True
    )
    await user.insert()
    print(f"Created User with ID: {user.id}")
    
    # Create Lawyer Profile
    lawyer_profile = LawyerProfile(
        user_id=user.id,
        bio="Senior Real Estate Lawyer with 10 years experience.",
        specialization=["Property Verification", "RERA Compliance"],
        bar_council_id="KAR/1234/2015",
        experience_years=10,
        is_online=True,
        cities=["Bangalore"],
        languages=["English", "Kannada"]
    )
    await lawyer_profile.insert()
    print(f"Created Lawyer Profile with ID: {lawyer_profile.id}")
    
    # Link profile back to user
    user.lawyer_profile_id = lawyer_profile.id
    await user.save()
    print("Linked Profile to User.")
    
    print("Seed Complete!")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_lawyer())
