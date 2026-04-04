import asyncio
from app.db.mongodb import init_db
from app.models.city import City

async def drop_cities():
    print("Connecting to DB...")
    await init_db()
    print("Dropping Cities collection...")
    await City.get_motor_collection().drop()
    print("Cities collection dropped successfully.")

if __name__ == "__main__":
    asyncio.run(drop_cities())
