import asyncio
from app.db.mongodb import init_db
from app.models.user import User
from app.core import security

async def reset_password():
    await init_db()
    email = "admin@realstart.com"
    new_password = "admin"
    
    user = await User.find_one(User.email == email)
    if not user:
        print(f"User {email} not found!")
        return

    user.hashed_password = security.get_password_hash(new_password)
    await user.save()
    print(f"Password for {email} reset to '{new_password}'")

if __name__ == "__main__":
    asyncio.run(reset_password())
