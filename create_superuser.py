import asyncio
from app.db.mongodb import init_db
from app.models.user import User, UserRole
from app.core import security

async def create_superuser():
    await init_db()
    
    email = "admin@realstart.com"
    password = "admin"
    
    user = await User.find_one(User.email == email)
    if user:
        print(f"User {email} already exists")
        return

    user = User(
        email=email,
        hashed_password=security.get_password_hash(password),
        full_name="Super Admin",
        role=UserRole.SUPER_ADMIN,
        is_active=True,
    )
    await user.insert()
    print(f"Superuser {email} created successfully")

if __name__ == "__main__":
    asyncio.run(create_superuser())
