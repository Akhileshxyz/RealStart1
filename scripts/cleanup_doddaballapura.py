import asyncio
from app.db.mongodb import init_db
from app.models.landmark import Landmark
from app.models.market_intelligence import MarketIntelligence

async def cleanup():
    await init_db()
    
    # Clean up the areas
    for name in ["Doddaballapura", "Near Doddaballapura Bus Stand"]:
        lm = await Landmark.find_one(Landmark.name == name)
        if lm:
            print(f"Deleting MarketIntelligence for {name}")
            await MarketIntelligence.find_many(MarketIntelligence.landmark_id == lm.id).delete()
            print(f"Deleting Landmark {name}")
            await lm.delete()

if __name__ == "__main__":
    asyncio.run(cleanup())
