import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import json
from bson import json_util

async def main():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['realstart_db']
    collections = ['landmarks', 'cities', 'projects', 'market_intelligence']
    for coll in collections:
        doc = await db[coll].find_one()
        print(f"--- {coll} ---")
        print(json.dumps(doc, indent=2, default=json_util.default))
        print("\n")

if __name__ == "__main__":
    asyncio.run(main())
