import asyncio
import motor.motor_asyncio
import os
from dotenv import load_dotenv

async def check_banners():
    load_dotenv()
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "realstart_db")
    
    client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
    db = client[database_name]
    
    banners = await db.hero_banners.find().to_list(length=100)
    print(f"Total banners: {len(banners)}")
    for b in banners:
        print(f"- Title: {b.get('title')}, Active: {b.get('is_active')}, Image: {b.get('image_url')}")

if __name__ == "__main__":
    asyncio.run(check_banners())
