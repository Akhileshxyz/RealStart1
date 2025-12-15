import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.db.mongodb import init_db
from app.models.user import User

async def check_user():
    await init_db()
    user = await User.find_one({"email": "admin@realtech.in"})
    if user:
        print(f"User found: {user.email}")
        print(f"Is Active: {user.is_active}")
        print(f"Role: {user.role}")
    else:
        print("User NOT found")

if __name__ == "__main__":
    asyncio.run(check_user())
