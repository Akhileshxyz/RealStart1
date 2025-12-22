import sys
import os
import asyncio
from uuid import UUID

sys.path.append(os.getcwd())

from app.models.landmark import Landmark
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.user import User

async def init_db():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(database=client[settings.DATABASE_NAME], document_models=[Landmark, User])

async def verify_locality_flow():
    print("Verifying Locality/Map Flow...")
    await init_db()
    
    # Check Mappls Config
    if settings.MAPPLS_CLIENT_ID:
        print("INFO: Mappls Client ID is set - Will attempt real API call")
    else:
        print("INFO: Mappls Client ID is missing - Will use fallback logic")
        
    try:
        from app.api.v1.locality import resolve_location, get_locality_details, LocationResolveRequest
        print("PASS: Locality module imported")
        
        # Test Resolution (Create New)
        req = LocationResolveRequest(
            place_name="Test Locality Area",
            latitude=12.9716,
            longitude=77.5946
        )
        
        # Simulate call
        res = await resolve_location(req)
        # res is a dict in the implementation or an object if pydantic response model handling is implicitly verified by framework
        # Our implementation returns a dict directly in the function for now or object. 
        # API returns object converted to JSON. Function returns dict.
        
        print(f"PASS: Resolution returned: {res}")
        landmark_id = res["landmark_id"]
        
        # Test Details
        details = await get_locality_details(landmark_id)
        print(f"PASS: Details fetch successful: {details['name']}")
        
        # Clean up
        lm = await Landmark.get(landmark_id)
        if lm:
            await lm.delete()
            print("PASS: Cleanup successful")
            
        print("Locality Module Verified Successfully!")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_locality_flow())
