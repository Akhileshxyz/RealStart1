from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.mongodb import init_db
from app.api.v1 import (
    public_auth,
    admin_auth,
    developers,
    users,
    public_projects,
    developer_projects,
    admin_projects,
    developer_leads,
    admin_change_requests,
    developer_webhooks,
    user_interactions,
    user_portal
)
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

# Define Tags Metadata for ordering
tags_metadata = [
    {"name": "🔐 User Authentication", "description": "Login and Registration for Buyers/Developers."},
    {"name": "🛡️ Admin Authentication", "description": "Login for System Administrators."},
    {"name": "🏠 End User Portal", "description": "Buyer features: Landmarks, History, Wishlist, Profile."},
    {"name": "🏢 Public Listings", "description": "Publicly accessible project listings."},
    {"name": "🏗️ Developer Portal", "description": "Project and Lead management for Developers."},
    {"name": "🛡️ Admin Portal", "description": "Master data and System management."},
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
    openapi_tags=tags_metadata
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

# 1. Authentication
app.include_router(public_auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["🔐 User Authentication"])
app.include_router(admin_auth.router, prefix=f"{settings.API_V1_STR}/admin", tags=["🛡️ Admin Authentication"])

# 2. Public Listings
app.include_router(public_projects.router, prefix=f"{settings.API_V1_STR}/public/projects", tags=["🏢 Public Listings"])

# 3. End User Portal
app.include_router(user_portal.router, prefix=f"{settings.API_V1_STR}", tags=["🏠 End User Portal"])
app.include_router(user_interactions.router, prefix=f"{settings.API_V1_STR}/users/interactions", tags=["🏠 End User Portal"])

# 4. Developer Portal
app.include_router(developer_projects.router, prefix=f"{settings.API_V1_STR}/developers/projects", tags=["🏗️ Developer Portal"])
app.include_router(developer_leads.router, prefix=f"{settings.API_V1_STR}/developers/leads", tags=["🏗️ Developer Portal"])
app.include_router(developer_webhooks.router, prefix=f"{settings.API_V1_STR}/developers/webhooks", tags=["🏗️ Developer Portal"])

# 5. Admin Portal
app.include_router(admin_projects.router, prefix=f"{settings.API_V1_STR}/admin/projects", tags=["🛡️ Admin Portal"])
app.include_router(developers.router, prefix=f"{settings.API_V1_STR}/admin/developers", tags=["🛡️ Admin Portal"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/admin/users", tags=["🛡️ Admin Portal"])
app.include_router(admin_change_requests.router, prefix=f"{settings.API_V1_STR}/admin/change-requests", tags=["🛡️ Admin Portal"])

@app.get("/")
async def root():
    return {"message": "Welcome to RealStart Auth System"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "RealStart API"}
