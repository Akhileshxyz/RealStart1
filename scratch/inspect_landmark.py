import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

# Add the project root to sys.path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.config import settings

async def main():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    landmark = await db['landmarks'].find_one({'price_prediction': {'$exists': True, '$ne': []}})
    if landmark:
        print(f"Landmark: {landmark.get('name')}")
        print(f"Price Prediction: {landmark.get('price_prediction')}")
    else:
        print("No landmark with price prediction found.")

if __name__ == "__main__":
    asyncio.run(main())
