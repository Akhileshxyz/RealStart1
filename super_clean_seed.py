import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient

# Add project root to path
sys.path.append(os.getcwd())

async def super_clean_seed():
    print("--- STEP 1: FORCED DROP (Using 127.0.0.1) ---")
    try:
        # Use 127.0.0.1 if localhost is refusing connection
        client = AsyncIOMotorClient("mongodb://127.0.0.1:27017", serverSelectionTimeoutMS=5000)
        db = client.realstart_db 
        await db.cities.drop()
        print("Success: Cities collection dropped.")
    except Exception as e:
        print(f"Error dropping collection: {e}")

    print("\n--- STEP 2: RUNNING SEEDER ---")
    from seed_all_admin import seed_all_admin
    try:
        await seed_all_admin()
        print("\n--- SEEDING FINISHED ---")
    except Exception as e:
         print(f"Error during seeding: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(super_clean_seed())
