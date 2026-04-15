import sys
import os
import asyncio
from uuid import uuid4
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.landmark import Landmark
from app.models.user import User

sys.path.append(os.getcwd())

async def test_legacy_landmark_loading():
    print("Testing Legacy Landmark Loading...")
    
    # Init DB
    client = AsyncIOMotorClient(settings.MONGODB_URL, uuidRepresentation='standard')
    await init_beanie(database=client[settings.DATABASE_NAME], document_models=[Landmark, User])
    
    # 1. Create a raw document directly in MongoDB (bypassing Beanie validation) to simulate legacy data
    legacy_id = uuid4()
    raw_doc = {
        "_id": legacy_id,
        "name": "Legacy Landmark",
        "city": "Old City",
        "latitude": 12.0,
        "longitude": 77.0,
        # NO "location" field
        "created_at": "2023-01-01T00:00:00"
    }
    
    await client[settings.DATABASE_NAME]["landmarks"].insert_one(raw_doc)
    print(f"Inserted legacy document with ID: {legacy_id}")
    
    try:
        # 2. Try to load it via Beanie
        landmark = await Landmark.get(legacy_id)
        if landmark:
            print(f"PASS: Successfully loaded legacy landmark: {landmark.name}")
            print(f"Location field is: {landmark.location}")
        else:
            print("FAILED: Landmark not found (but should be)")
            
    except Exception as e:
        print(f"FAILED: Error loading legacy landmark: {e}")
        import traceback
        traceback.print_exc()
        
    # Cleanup
    await client[settings.DATABASE_NAME]["landmarks"].delete_one({"_id": legacy_id})

if __name__ == "__main__":
    asyncio.run(test_legacy_landmark_loading())
