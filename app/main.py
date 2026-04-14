from contextlib import asynccontextmanager
from typing import Any, List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
    developer_subscriptions,
    admin_dashboard,
    admin_analytics,
    admin_ads,
    admin_team,
    admin_landmarks,
    admin_videos,
    locality,
    developer_uploads,
    developer_auth,
    lawyer_auth,
    lawyer_dashboard,
    lawyer_cases,
    lawyer_clients,
    lawyer_schedule,
    lawyer_analytics,
    lawyer_settings,
    lawyer_properties,
    public_lawyers,
    user_lawyers,
    admin_market_intelligence,
    user_notifications,
    wishlist,
    public_home,
    admin_blogs,
    admin_reels,
    user_reels,
    admin_cities,
    public_blogs
)

from app.middleware import SecurityHeadersMiddleware, RequestSizeLimitMiddleware
from app.core.logging_config import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Custom StaticFiles class to handle CORS for PDF generation/Canvas
class CORSStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: Any) -> Any:
        response = await super().get_response(path, scope)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

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
    {"name": "Public - Home", "description": "Homepage feed APIs: featured cities, featured projects, and latest blogs."},
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
    {"name": "Developer - Uploads", "description": "File upload for documents and images (RERA, RTC, DC Conversion, Layout Approval, Project Images)."},
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
    {"name": "Admin - Blogs", "description": "Blog post creation, editing, publishing, and deletion."},
    {"name": "Locality", "description": "Map-based Locality Intelligence APIs (Mappls integration)."},
    {"name": "Developer - Authentication", "description": "Login and password management for Developers."},
    {"name": "Settings", "description": "User settings for all user types - Password change and Profile management."},
    {"name": "Lawyer - Authentication", "description": "Login and password management for Lawyers."},
    {"name": "Lawyer - Dashboard", "description": "Lawyer dashboard analytics and overview."},
    {"name": "Lawyer - Cases", "description": "Legal case management and details."},
    {"name": "Lawyer - Clients", "description": "Client management for lawyers."},
    {"name": "Lawyer - Schedule", "description": "Lawyer appointment and consultation scheduling."},
    {"name": "Lawyer - Analytics", "description": "Case and performance analytics for lawyers."},
    {"name": "Lawyer - Settings", "description": "Lawyer profile and availability settings."},
    {"name": "Reels", "description": "Short video content feed and interactions."},
    {"name": "Admin - Reels", "description": "Admin/Team management for short video content (reels)."},
    {"name": "Admin - Cities", "description": "Admin city management and CRUD operations."},
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

# (CORS middleware moved below to be outermost)

# Security & Size Middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware, max_size=settings.MAX_FILE_SIZE)

# CORS Configuration (Outer-most to handle final headers)
allowed_origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]
if "http://localhost:5173" not in allowed_origins:
    allowed_origins.append("http://localhost:5173")
if "http://127.0.0.1:5173" not in allowed_origins:
    allowed_origins.append("http://127.0.0.1:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include Routers
app.include_router(public_auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(public_projects.router, prefix=f"{settings.API_V1_STR}/public/projects", tags=["Public Projects"])
app.include_router(public_blogs.router, prefix=f"{settings.API_V1_STR}/public/blogs", tags=["Public Blogs"])
app.include_router(public_home.router, prefix=f"{settings.API_V1_STR}/public", tags=["Public - Home"])
app.include_router(user_portal.router, prefix=f"{settings.API_V1_STR}")
app.include_router(user_interactions.router, prefix=f"{settings.API_V1_STR}/users/interactions", tags=["User - Interactions"])
app.include_router(user_notifications.router, prefix=f"{settings.API_V1_STR}", tags=["User - Notifications"])
app.include_router(wishlist.router, prefix=f"{settings.API_V1_STR}/wishlist", tags=["User - Wishlist"])
app.include_router(user_reels.router, prefix=f"{settings.API_V1_STR}/reels", tags=["Reels"])
app.include_router(public_lawyers.router, prefix=f"{settings.API_V1_STR}/public/lawyers", tags=["Lawyer - Public"])
app.include_router(user_lawyers.router, prefix=f"{settings.API_V1_STR}/users/interactions/lawyer-consultations", tags=["Lawyer - User"])

app.include_router(developer_auth.router, prefix=f"{settings.API_V1_STR}/developers/auth", tags=["Developer - Authentication"])
app.include_router(developer_projects.router, prefix=f"{settings.API_V1_STR}/developers/projects", tags=["Developer - Projects"])
app.include_router(developer_leads.router, prefix=f"{settings.API_V1_STR}/developers/leads", tags=["Developer - Leads"])
app.include_router(developer_webhooks.router, prefix=f"{settings.API_V1_STR}/developers/webhooks", tags=["Developer - Webhooks"])
app.include_router(developer_team.router, prefix=f"{settings.API_V1_STR}/developers/team", tags=["Developer - Team"])
app.include_router(developer_subscriptions.router, prefix=f"{settings.API_V1_STR}/developers/subscriptions", tags=["Developer - Subscriptions"])
app.include_router(developer_uploads.router, prefix=f"{settings.API_V1_STR}/developers", tags=["Developer - Uploads"])

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
app.include_router(admin_blogs.router, prefix=f"{settings.API_V1_STR}/admin/blogs", tags=["Admin - Blogs"])
app.include_router(admin_reels.router, prefix=f"{settings.API_V1_STR}/admin/reels", tags=["Admin - Reels"])
app.include_router(admin_market_intelligence.router, prefix=f"{settings.API_V1_STR}/admin/market-intelligence", tags=["Admin - Market Intelligence"])
app.include_router(admin_cities.router, prefix=f"{settings.API_V1_STR}/admin/cities", tags=["Admin - Cities"])

app.include_router(locality.router, prefix=f"{settings.API_V1_STR}/locality", tags=["Locality"])
app.include_router(admin_settings.router, prefix=f"{settings.API_V1_STR}/settings", tags=["Settings"])

app.include_router(lawyer_auth.router, prefix=f"{settings.API_V1_STR}/lawyer/auth", tags=["Lawyer - Authentication"])
app.include_router(lawyer_dashboard.router, prefix=f"{settings.API_V1_STR}/lawyer", tags=["Lawyer - Dashboard"])
app.include_router(lawyer_cases.router, prefix=f"{settings.API_V1_STR}/lawyer", tags=["Lawyer - Cases"])
app.include_router(lawyer_clients.router, prefix=f"{settings.API_V1_STR}/lawyer", tags=["Lawyer - Clients"])
app.include_router(lawyer_schedule.router, prefix=f"{settings.API_V1_STR}/lawyer", tags=["Lawyer - Schedule"])
app.include_router(lawyer_analytics.router, prefix=f"{settings.API_V1_STR}/lawyer", tags=["Lawyer - Analytics"])
app.include_router(lawyer_settings.router, prefix=f"{settings.API_V1_STR}/lawyer", tags=["Lawyer - Settings"])
app.include_router(lawyer_properties.router, prefix=f"{settings.API_V1_STR}/lawyer", tags=["Lawyer - Properties"])

# Static files for uploads with explicit CORS for cross-origin PDF generation
from pathlib import Path
upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", CORSStaticFiles(directory=str(upload_dir)), name="uploads")

@app.get("/")
async def root():
    return {"message": "Welcome to RealStart Auth System"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "RealStart API"}
