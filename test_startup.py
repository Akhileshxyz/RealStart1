import asyncio
import logging
from app.db.mongodb import init_db
from app.core.config import settings

logging.basicConfig(level=logging.INFO)

async def test_startup():
    print("Testing startup...")
    try:
        client = await init_db()
        print("init_db OK")
        await client.close()
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_startup())
