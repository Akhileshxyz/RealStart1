import asyncio
from app.main import app

async def test_lifespan():
    print("Testing application lifespan...")
    try:
        async with app.router.lifespan_context(app):
            print("Lifespan Startup OK")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_lifespan())
