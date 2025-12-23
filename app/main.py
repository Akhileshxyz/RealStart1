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
    admin_subscriptions,
    developer_subscriptions,
    lawyer_portal,
    admin_dashboard,
    admin_analytics,
    admin_ads,
    admin_team,
    admin_team,
    admin_landmarks,
    admin_videos,
    locality
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
    {"name": "Authentication", "description": "User login and registration."},
    {"name": "Public Projects", "description": "Publicly accessible project listings."},
    {"name": "User - Profile", "description": "User profile management and information."},
    {"name": "User - History & Wishlist", "description": "View history and wishlist management."},
    {"name": "User - Landmarks", "description": "Market analyzer and landmark information."},
    {"name": "User - Visit Bookings", "description": "Site visit booking and management."},
    {"name": "User - Interactions", "description": "Project interactions: views, wishlist, legal requests, and visit bookings."},
    {"name": "Developer - Projects", "description": "Developer project creation, editing, and visibility management."},
    {"name": "Developer - Leads", "description": "Developer lead tracking and analytics dashboard."},
    {"name": "Developer - Webhooks", "description": "Developer webhook management for real-time notifications."},
    {"name": "Developer - Team", "description": "Developer team member management and access control."},
    {"name": "Developer - Subscriptions", "description": "Developer subscription plans and purchases."},
    {"name": "Admin - Authentication", "description": "Login for System Administrators."},
    {"name": "Admin - Projects", "description": "Admin project approval and management."},
    {"name": "Admin - Developers", "description": "Admin developer account management."},
    {"name": "Admin - Users", "description": "Admin user account management."},
    {"name": "Admin - Subscriptions", "description": "Subscription Plan Management."},
    {"name": "Admin - Dashboard", "description": "System-wide statistics and overview."},
    {"name": "Admin - Analytics", "description": "System analytics and insights."},
    {"name": "Admin - Ads", "description": "Ads management and tracking."},
    {"name": "Admin - Team", "description": "Internal team and staff management."},
    {"name": "Admin - Landmarks", "description": "Admin landmark creation and management."},
    {"name": "Admin - Videos", "description": "Video content management and analytics."},
    {"name": "Locality", "description": "Map-based Locality Intelligence APIs (Mappls integration)."},
    {"name": "Settings", "description": "User settings for all user types - Password change and Profile management."},
    {"name": "Lawyer Portal", "description": "Legal document verification and call management."},
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

# 1. Public APIs
app.include_router(public_auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(public_projects.router, prefix=f"{settings.API_V1_STR}/public/projects", tags=["Public Projects"])
app.include_router(user_portal.router, prefix=f"{settings.API_V1_STR}")
app.include_router(user_interactions.router, prefix=f"{settings.API_V1_STR}/users/interactions", tags=["User - Interactions"])

# 2. Developer Portal
app.include_router(developer_projects.router, prefix=f"{settings.API_V1_STR}/developers/projects", tags=["Developer - Projects"])
app.include_router(developer_leads.router, prefix=f"{settings.API_V1_STR}/developers/leads", tags=["Developer - Leads"])
app.include_router(developer_webhooks.router, prefix=f"{settings.API_V1_STR}/developers/webhooks", tags=["Developer - Webhooks"])
app.include_router(developer_team.router, prefix=f"{settings.API_V1_STR}/developers/team", tags=["Developer - Team"])
app.include_router(developer_subscriptions.router, prefix=f"{settings.API_V1_STR}/developers/subscriptions", tags=["Developer - Subscriptions"])

# 3. Admin Portal
app.include_router(admin_auth.router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin - Authentication"])
app.include_router(admin_projects.router, prefix=f"{settings.API_V1_STR}/admin/projects", tags=["Admin - Projects"])
app.include_router(developers.router, prefix=f"{settings.API_V1_STR}/admin/developers", tags=["Admin - Developers"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/admin/users", tags=["Admin - Users"])
app.include_router(admin_change_requests.router, prefix=f"{settings.API_V1_STR}/admin/projects/change-requests", tags=["Admin - Projects"])
app.include_router(admin_subscriptions.router, prefix=f"{settings.API_V1_STR}/admin/subscriptions", tags=["Admin - Subscriptions"])
app.include_router(admin_dashboard.router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin - Dashboard"])
app.include_router(admin_analytics.router, prefix=f"{settings.API_V1_STR}/admin/analytics", tags=["Admin - Analytics"])
app.include_router(admin_ads.router, prefix=f"{settings.API_V1_STR}/admin/ads", tags=["Admin - Ads"])
app.include_router(admin_team.router, prefix=f"{settings.API_V1_STR}/admin/team", tags=["Admin - Team"])
app.include_router(admin_landmarks.router, prefix=f"{settings.API_V1_STR}/admin/landmarks", tags=["Admin - Landmarks"])
app.include_router(admin_videos.router, prefix=f"{settings.API_V1_STR}/admin/videos", tags=["Admin - Videos"])

app.include_router(admin_videos.router, prefix=f"{settings.API_V1_STR}/admin/videos", tags=["Admin - Videos"])

# 4. Locality Intelligence (Public/Auth optional depending on business logic)
# Keeping strict auth validation inside endpoints if needed, generic prefix here.
app.include_router(locality.router, prefix=f"{settings.API_V1_STR}/locality", tags=["Locality"])

# 5. Settings (for all user types)
app.include_router(admin_settings.router, prefix=f"{settings.API_V1_STR}/settings", tags=["Settings"])

# 5. Lawyer Portal
app.include_router(lawyer_portal.router, prefix=f"{settings.API_V1_STR}/lawyer", tags=["Lawyer Portal"])

@app.get("/")
async def root():
    return {"message": "Welcome to RealStart Auth System"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "RealStart API"}
