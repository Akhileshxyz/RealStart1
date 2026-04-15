import asyncio
import os
import sys

# Ensure app is in path
sys.path.append(os.getcwd())

from app.db.mongodb import init_db
from app.models.user import User, UserRole
from app.models.landmark import Landmark
from app.core import security
from app.core.config import settings

async def setup_data():
    print("Initializing database connection...")
    await init_db()

    users_to_create = [
        {
            "email": "superadmin@realstart.com",
            "password": "admin123",
            "full_name": "Super Admin",
            "role": UserRole.SUPER_ADMIN
        },
        {
            "email": "dev@realstart.com",
            "password": "dev123",
            "full_name": "Developer User",
            "role": UserRole.DEVELOPER
        },
        {
            "email": "user@realstart.com",
            "password": "user123",
            "full_name": "Buyer User",
            "role": UserRole.BUYER
        }
    ]

    for user_data in users_to_create:
        existing_user = await User.find_one(User.email == user_data["email"])
        if not existing_user:
            print(f"Creating user: {user_data['email']}")
            hashed_pw = security.get_password_hash(user_data["password"])
            new_user = User(
                email=user_data["email"],
                hashed_password=hashed_pw,
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=True
            )
            await new_user.insert()
            print(f"User {user_data['email']} created.")
        else:
            print(f"User {user_data['email']} already exists.")

    print("--- Seeding Landmarks ---")
    landmark_data = {
        "name": "Devanahalli Bus Stand",
        "city": "Devanahalli", # Case sensitive match for now
        "latitude": 13.2486,
        "longitude": 77.7126,
        "avg_price_per_sqft": 4500.0,
        "growth_forecast_5yr": 12.5,
        "price_trend": "rising",
        "total_projects": 15,
        "description": "Key transit hub near Airport"
    }

    existing_landmark = await Landmark.find_one(Landmark.name == landmark_data["name"])
    if not existing_landmark:
        l = Landmark(**landmark_data)
        await l.insert()
        print(f"Landmark {l.name} created.")
    else:
        print(f"Landmark {landmark_data['name']} already exists.")

    print("Test data setup complete.")

if __name__ == "__main__":
    asyncio.run(setup_data())
