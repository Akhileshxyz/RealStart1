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
    
    collections = ['landmarks', 'cities', 'projects', 'market_intelligence', 'societies']
    for coll_name in collections:
        print(f"--- Checking {coll_name} ---")
        # Find any document with at least one float field stored as string
        # This is a bit complex in one query, so let's just check typical fields
        if coll_name == 'landmarks':
            fields = ['avg_plot_price', 'avg_apartment_price']
        elif coll_name == 'cities':
            fields = ['avg_commercial_plot_price', 'avg_residential_plot_price']
        elif coll_name == 'projects':
            fields = ['min_price', 'max_price']
        else:
            fields = []

        for field in fields:
            docs = await db[coll_name].find({field: {'$type': 'string'}}).to_list(10)
            if docs:
                print(f"  Field '{field}' has string values in {len(docs)} docs (sampled):")
                for d in docs:
                    print(f"    - {d.get('name', 'N/A')}: {d.get(field)}")
            else:
                print(f"  Field '{field}' has no string values.")

if __name__ == "__main__":
    asyncio.run(main())
