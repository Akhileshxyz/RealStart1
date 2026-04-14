import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient

# Add project root to path
sys.path.append(os.getcwd())

from app.core.config import settings

async def audit_blogs():
    print("Auditing Blogs...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    collection = db["blogs"]
    
    fields = ["title", "slug", "description", "category"]
    
    for field in fields:
        count = await collection.count_documents({"$or": [{field: {"$exists": False}}, {field: None}]})
        print(f"Blogs missing '{field}': {count}")
        
    # Check for empty tags List
    count = await collection.count_documents({"tags": {"$exists": False}})
    print(f"Blogs missing 'tags' list: {count}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(audit_blogs())
