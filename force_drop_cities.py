import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def force_drop():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.realstart_db # Correct name from your config
    if "cities" in await db.list_collection_names():
        await db.cities.drop()
        print("Forced drop of cities collection successful.")
    else:
        print("Cities collection not found, nothing to drop.")

if __name__ == "__main__":
    asyncio.run(force_drop())
