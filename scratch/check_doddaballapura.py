import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.city import City
from app.models.landmark import Landmark
from app.core.config import settings

async def check_city():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(database=client[settings.MONGODB_DB_NAME], document_models=[City, Landmark])
    
    city = await City.find_one(City.slug == "doddaballapura")
    if not city:
        print("City not found")
        return
    
    print(f"City found: {city.name}")
    print(f"Landmarks ID list: {city.landmarks_id_list}")
    print(f"Top Landmarks to invest: {city.top_landmarks_to_invest}")
    print(f"Top Developed Projects: {city.top_developed_projects}")
    
    for lm_id in city.landmarks_id_list:
        lm = await Landmark.get(lm_id)
        if not lm:
            print(f"Landmark NOT FOUND: {lm_id}")
        else:
            print(f"Landmark found: {lm.name}")

if __name__ == "__main__":
    asyncio.run(check_city())
