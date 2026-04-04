import asyncio
import os
import sys
from datetime import datetime, timedelta
from uuid import uuid4

# Add project root to path
sys.path.append(os.getcwd())

from app.db.mongodb import init_db
from app.models.user import User, UserRole
from app.models.developer import Developer
from app.models.project import Project, ProjectStatus, PropertyType, ProjectAppovalType
from app.models.city import City, SubArea, PoliticalAgenda, PricePoint, PredictionPoint
from app.models.landmark import Landmark, GeoJSONLocation
from app.models.ad import Ad, AdType, AdPlatform
from app.models.reel import Reel
from app.models.video import Video
from app.models.blog import Blog
from app.core import security

async def seed_all_admin():
    print("Initializing Database...")
    await init_db()

    # Clear existing cities & landmarks to refresh structure
    await City.find_all().delete()
    await Landmark.find_all().delete()

    # 1. ADMIN USER
    admin_email = "admin@realstart.com"
    admin = await User.find_one(User.email == admin_email)
    if not admin:
        print(f"Creating Admin User: {admin_email}")
        admin = User(
            email=admin_email,
            hashed_password=security.get_password_hash("admin123"),
            full_name="System Admin",
            role=UserRole.ADMIN,
            is_active=True
        )
        await admin.insert()
    
    # 2. DEVELOPER
    dev_email = "dev_seeder@realstart.com"
    developer = await Developer.find_one(Developer.contact_email == dev_email)
    if not developer:
        print(f"Creating Developer: {dev_email}")
        developer = Developer(
            name="Seeder Developer Group",
            legal_name="Seeder Realty Pvt Ltd",
            contact_email=dev_email,
            is_verified=True
        )
        await developer.insert()

    # 3. LANDMARKS (With Amenities)
    print("Creating Landmarks with Amenities...")
    landmarks = []
    cities_list = ["Bangalore", "Mysore", "Hubli"]
    for city_name in cities_list:
        for i in range(1, 3):
            landmark = Landmark(
                name=f"{city_name} Center {i}",
                city=city_name,
                description=f"Prime landmark in {city_name}",
                avg_price_per_sqft=4500 + (i * 500),
                location=GeoJSONLocation(coordinates=[77.5946 + (i*0.05), 12.9716 + (i*0.05)]),
                nearby_amenities=["Hospital", "Mall", "Metro Station", "School"],
                image_url=f"/uploads/localities/dummy_{city_name.lower()}_{i}.jpg"
            )
            await landmark.insert()
            landmarks.append(landmark)

    # 4. PROJECTS
    print("Creating Projects...")
    projects = await Project.find_all().to_list()
    if not projects:
        for i in range(1, 4):
            project = Project(
                developer_id=developer.id,
                name=f"RealStart Heights {i}",
                slug=f"realstart-heights-{i}",
                description="Luxury project.",
                status=ProjectStatus.APPROVED,
                city=cities_list[i % 3],
                min_price=5000000,
                max_price=8000000,
                is_featured=True,
                gallery_images=[f"/uploads/projects/p{i}.jpg"]
            )
            await project.insert()
            projects.append(project)

    # 5. CITIES (New Keys and Landmark Links)
    print("Creating Cities with New Keys & Landmark Links...")
    for city_name in cities_list:
        city_landmarks_ids = [l.id for l in landmarks if l.city == city_name]
        
        city = City(
            name=city_name,
            slug=city_name.lower(),
            latitude=12.9716,
            longitude=77.5946,
            images=[f"/uploads/cities/{city_name.lower()}/hero.jpg"],
            
            # New Financial & Descriptive Keys
            population_urban="13.6M" if city_name == "Bangalore" else "2.1M",
            rental_yield="3.2%" if city_name == "Bangalore" else "2.8%",
            feature_description="Silicon Valley of India with massive tech infrastructure.",
            city_description=f"{city_name} is a rapidly growing hub for real estate and commerce.",

            avg_appreciation_start_value=5.0,
            avg_appreciation_end_value=12.0,
            avg_commercial_plot_price=6000.0,
            avg_residential_plot_price=4500.0,
            residential_rent_2bhk_description="Rs 15,000 - 45,000",

            price_growth_history=[
                PricePoint(year=2021, value=3800),
                PricePoint(year=2022, value=4200),
                PricePoint(year=2023, value=4500)
            ],
            price_prediction=[
                PredictionPoint(year=2024, value1=4900, value2=4700),
                PredictionPoint(year=2025, value1=5400, value2=5100),
                PredictionPoint(year=2026, value1=6000, value2=5500),
                PredictionPoint(year=2027, value1=6800, value2=6100),
                PredictionPoint(year=2028, value1=7500, value2=6800)
            ],
            top_sub_areas=[
                SubArea(name="Whitefield", image="/uploads/areas/wf.jpg", desc="IT Powerhouse", growth="18%"),
                SubArea(name="Sarjapur", image="/uploads/areas/sar.jpg", desc="Residential Hub", growth="14%")
            ],
            political_infrastructure_agenda=PoliticalAgenda(mla="Hon. MLA", mp="Hon. MP"),
            landmarks_id_list=city_landmarks_ids,
            is_active=True
        )
        await city.insert()

    print("Seeding Complete!")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_all_admin())
