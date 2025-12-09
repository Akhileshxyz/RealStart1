from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.db.mongodb import init_db
from app.api.v1 import public_auth, admin_auth, developers

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    await init_db()
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Include Routers
app.include_router(public_auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Public Auth"])
app.include_router(admin_auth.router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin Auth"])
app.include_router(developers.router, prefix=f"{settings.API_V1_STR}/admin/developers", tags=["Developers"])

@app.get("/")
async def root():
    return {"message": "Welcome to RealStart Auth System"} 
