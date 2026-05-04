import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import sys
import os

# Add the project root to sys.path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.landmark import Landmark
from app.models.city import City
from app.models.project import Project
from app.models.market_intelligence import MarketIntelligence
from app.models.society import Society
from app.utils.parsers import parse_price_string
from app.core.config import settings

async def migrate_collection(client, Model, fields):
    print(f"Migrating {Model.__name__}...")
    # Use raw collection via client to avoid Beanie validation during find
    collection = client[settings.DATABASE_NAME][Model.Settings.name]
    count = 0
    
    # Generic update for top-level fields
    for field in fields:
        cursor = collection.find({field: {"$type": "string"}})
        async for raw_doc in cursor:
            val = raw_doc.get(field)
            if isinstance(val, str):
                new_val = parse_price_string(val)
                await collection.update_one(
                    {"_id": raw_doc["_id"]},
                    {"$set": {field: new_val}}
                )
                count += 1

    # Special handling for nested fields (price_growth etc)
    # We can still use Beanie for this if we are careful, 
    # but let's stick to raw for completeness if shorthands are deep
    if Model in [Landmark, City]:
        cursor = collection.find({
            "$or": [
                {"price_growth.value": {"$type": "string"}},
                {"price_growth_history.value": {"$type": "string"}},
                {"price_prediction.value1": {"$type": "string"}},
                {"price_prediction.value2": {"$type": "string"}},
                {"price_prediction.value": {"$type": "string"}}
            ]
        })
        async for raw_doc in cursor:
            # For nested arrays, it's easier to load via Beanie and save, 
            # now that validators are in place to handle the load.
            try:
                doc = await Model.get(raw_doc["_id"])
                if doc:
                    await doc.save() # This will write back validated floats
                    count += 1
            except Exception as e:
                print(f"Error saving doc {raw_doc['_id']}: {e}")
    
    print(f"Updated {count} {Model.__name__} fields/documents.")

async def main():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[Landmark, City, Project, MarketIntelligence, Society]
    )
    
    await migrate_collection(client, Landmark, ['avg_plot_price', 'avg_commercial_plot_price', 'avg_price_per_sqft'])
    await migrate_collection(client, City, ['avg_appreciation_start_value', 'avg_appreciation_end_value', 
                                    'avg_commercial_plot_price', 'avg_residential_plot_price'])
    await migrate_collection(client, Project, ['min_price', 'max_price'])
    await migrate_collection(client, MarketIntelligence, ['avg_commercial_plot_price', 'avg_residential_plot_price'])
    await migrate_collection(client, Society, ['price_range_min', 'price_range_max', 'avg_price_per_sqft'])
    
    print("Migration complete.")

if __name__ == "__main__":
    asyncio.run(main())
