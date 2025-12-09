from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings

from app.models.user import User
from app.models.developer import Developer

async def init_db():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # Initialize Beanie with the User model
    await init_beanie(database=client[settings.DATABASE_NAME], document_models=[User, Developer])
    
    # For now, just return client to show connection works, though init_beanie is where the magic happens
    return client
