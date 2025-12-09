from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.db.mongodb import init_db
from app.api.v1 import public_auth, admin_auth, developers, users, public_projects, developer_projects, admin_projects, developer_leads

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
# Public Projects
app.include_router(public_projects.router, prefix=f"{settings.API_V1_STR}/public/projects", tags=["Public Projects"])
# Developer Projects
app.include_router(developer_projects.router, prefix=f"{settings.API_V1_STR}/developers/projects", tags=["Developer Projects"])
app.include_router(developer_leads.router, prefix=f"{settings.API_V1_STR}/developers/leads", tags=["Developer Leads"])
# Admin Projects
app.include_router(admin_projects.router, prefix=f"{settings.API_V1_STR}/admin/projects", tags=["Admin Projects"])

app.include_router(developers.router, prefix=f"{settings.API_V1_STR}/admin/developers", tags=["Developers"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/admin/users", tags=["Users Management"])

@app.get("/")
async def root():
    return {"message": "Welcome to RealStart Auth System"} 
