from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.db.mongodb import init_db
from app.core.redis_client import redis_client
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
    user_portal,
    admin_settings,
    developer_team,
    admin_subscriptions,
    developer_subscriptions
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

    # Initialize Redis
    await redis_client.initialize()
    if redis_client.is_available:
        logger.info("Redis cache initialized successfully")
    else:
        logger.warning("Redis cache not available - continuing without caching")

    yield

    # Shutdown
    logger.info("Shutting down RealStart application...")
    await redis_client.close()

# Define Tags Metadata for ordering
tags_metadata = [
    {"name": "🔐 User Authentication", "description": "Login and Registration for Buyers/Developers."},
    {"name": "🛡️ Admin Authentication", "description": "Login for System Administrators."},
    {"name": "🏠 End User Portal", "description": "Buyer features: Landmarks, History, Wishlist, Profile."},
    {"name": "🏢 Public Listings", "description": "Publicly accessible project listings."},
    {"name": "Developer - Projects", "description": "Developer project creation, editing, and visibility management."},
    {"name": "Developer - Leads", "description": "Developer lead tracking and analytics dashboard."},
    {"name": "Developer - Webhooks", "description": "Developer webhook management for real-time notifications."},
    {"name": "Developer - Team", "description": "Developer team member management and access control."},
    {"name": "Developer - Subscriptions", "description": "Developer subscription plans and purchases."},
    {"name": "Admin - Projects", "description": "Admin project approval and management."},
    {"name": "Admin - Developers", "description": "Admin developer account management."},
    {"name": "Admin - Users", "description": "Admin user account management."},
    {"name": "Admin - Subscriptions", "description": "Subscription Plan Management."},
    {"name": "⚙️ Settings", "description": "User settings for all user types - Password change and Profile management."},
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
    openapi_tags=tags_metadata
)

# Rate Limiting Setup
limiter = Limiter(key_func=get_remote_address, storage_uri=settings.REDIS_URL)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
app.include_router(developer_projects.router, prefix=f"{settings.API_V1_STR}/developers/projects", tags=["Developer - Projects"])
app.include_router(developer_leads.router, prefix=f"{settings.API_V1_STR}/developers/leads", tags=["Developer - Leads"])
app.include_router(developer_webhooks.router, prefix=f"{settings.API_V1_STR}/developers/webhooks", tags=["Developer - Webhooks"])
app.include_router(developer_team.router, prefix=f"{settings.API_V1_STR}/developers/team", tags=["Developer - Team"])
app.include_router(developer_subscriptions.router, prefix=f"{settings.API_V1_STR}/developers/subscriptions", tags=["Developer - Subscriptions"])

# 5. Admin Portal
app.include_router(admin_projects.router, prefix=f"{settings.API_V1_STR}/admin/projects", tags=["Admin - Projects"])
app.include_router(developers.router, prefix=f"{settings.API_V1_STR}/admin/developers", tags=["Admin - Developers"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/admin/users", tags=["Admin - Users"])
app.include_router(admin_change_requests.router, prefix=f"{settings.API_V1_STR}/admin/projects", tags=["Admin - Projects"])
app.include_router(admin_subscriptions.router, prefix=f"{settings.API_V1_STR}/admin/subscriptions", tags=["Admin - Subscriptions"])

# 6. Settings (for all user types)
app.include_router(admin_settings.router, prefix=f"{settings.API_V1_STR}/settings", tags=["⚙️ Settings"])

@app.get("/")
async def root():
    return {"message": "Welcome to RealStart Auth System"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "RealStart API"}
