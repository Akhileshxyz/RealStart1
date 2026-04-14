import asyncio
import os
import sys
from uuid import uuid4
from motor.motor_asyncio import AsyncIOMotorClient

# Add project root to path
sys.path.append(os.getcwd())

from app.core.config import settings

def simple_slug(text):
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

async def fix_missing_slugs():
    print("Initializing Database Client...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    collection = db["blogs"]
    
    # Find documents where slug is missing or null
    cursor = collection.find({"$or": [{"slug": {"$exists": False}}, {"slug": None}]})
    
    count = 0
    async for doc in cursor:
        title = doc.get("title", "untitled")
        slug = simple_slug(title)
        
        # Check if slug exists in DB to avoid duplicates
        if not slug:
            slug = str(uuid4())[:8]
            
        await collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"slug": slug}}
        )
        print(f"Fixed blog: {title} -> {slug}")
        count += 1
        
    print(f"\nFixed {count} blog(s).")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(fix_missing_slugs())
