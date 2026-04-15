
import asyncio
import shutil
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.landmark import Landmark
from app.core.config import settings

async def delete_all_landmarks():
    # Initialize Beanie
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[Landmark]
    )
    
    landmarks = await Landmark.find_all().to_list()
    count = len(landmarks)
    print(f"Found {count} landmarks to delete.")
    
    # Delete database records
    await Landmark.find_all().delete()
    print("Database records deleted.")
    
    # Optional: Clean up upload directory
    localities_dir = Path(settings.UPLOAD_DIR) / "localities"
    if localities_dir.exists():
        # Only delete subdirectories (landmark folders) to keep the base dir
        for item in localities_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
        print("Filesystem cleanup completed.")
    
    print(f"Successfully deleted {count} landmarks.")

if __name__ == "__main__":
    asyncio.run(delete_all_landmarks())
