import sys
import os
import asyncio
from uuid import uuid4
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.landmark import Landmark
from app.models.user import User
from app.schemas.landmark import LandmarkResponse

sys.path.append(os.getcwd())

async def test_full_landmark_flow():
    print("Testing Full Landmark Flow (Load -> Schema)...")
    
    # Init DB
    client = AsyncIOMotorClient(settings.MONGODB_URL, uuidRepresentation='standard')
    await init_beanie(database=client[settings.DATABASE_NAME], document_models=[Landmark, User])
    
    # 1. Create a raw legacy document (no location field)
    legacy_id = uuid4()
    raw_doc = {
        "_id": legacy_id,
        "name": "Legacy Landmark For Schema",
        "city": "Test City",
        # NO lat/long
        # NO created_at/updated_at (simulate very old data)
        # NO location
    }
    
    await client[settings.DATABASE_NAME]["landmarks"].insert_one(raw_doc)
    print(f"Inserted legacy document: {legacy_id}")
    
    try:
        # 2. Load via Beanie
        landmark = await Landmark.get(legacy_id)
        if not landmark:
            print("FAILED: Could not load landmark")
            return

        print(f"Loaded landmark: {landmark.name}")
        
        # 3. Test Schema Conversion (The potential crash point)
        try:
            # Check if from_orm exists or we need model_validate
            if hasattr(LandmarkResponse, "from_orm"):
                response = LandmarkResponse.from_orm(landmark)
                print("PASS: LandmarkResponse.from_orm successful")
            else:
                response = LandmarkResponse.model_validate(landmark)
                print("PASS: LandmarkResponse.model_validate successful")
                
            print(f"Response ID: {response.id}")
            
        except Exception as e:
            print(f"FAILED during Schema Conversion: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        
    # Cleanup
    await client[settings.DATABASE_NAME]["landmarks"].delete_one({"_id": legacy_id})

if __name__ == "__main__":
    asyncio.run(test_full_landmark_flow())
