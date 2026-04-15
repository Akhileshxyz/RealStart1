
import asyncio
from uuid import UUID
import ast
import bson
from bson.binary import Binary, UuidRepresentation
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def check_users():
    client = AsyncIOMotorClient(settings.MONGODB_URL, uuidRepresentation="standard")
    db = client["realstart_db"]
    collection = db["users"]
    
    cursor = collection.find({})
    async for doc in cursor:
        print(f"User: {doc.get('email')}, _id type: {type(doc.get('_id'))}, role: {doc.get('role')}")
        for key, val in doc.items():
            if isinstance(val, str) and val.startswith("b'") and val.endswith("'"):
                print(f"  Field {key} is BUGGED: {val!r}")

if __name__ == "__main__":
    asyncio.run(check_users())
