from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.mongodb import init_db
from app.api.v1 import public_auth, admin_auth, developers, users, public_projects, developer_projects, admin_projects, developer_leads
from app.middleware import SecurityHeadersMiddleware, RequestSizeLimitMiddleware
from app.core.logging_config import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up RealStart application...")
    await init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down RealStart application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS Configuration
allowed_origins = settings.ALLOWED_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    max_age=3600,
)

# Security Middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware, max_size=settings.MAX_FILE_SIZE)

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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "RealStart API"}
