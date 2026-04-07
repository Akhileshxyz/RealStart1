import logging
import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from pydantic import BaseModel, EmailStr
from app.api import deps
from app.models.user import User
from app.models.lead import ProjectLead
from app.models.project import Project
from app.models.landmark import Landmark
from app.models.visit import VisitBooking, VisitStatus
from app.schemas.project import ProjectResponse
from app.schemas.lead import LeadResponse
from app.core.config import settings
from app.schemas.landmark import LandmarkResponse, LandmarkCreate, LandmarkSummary
from app.schemas.visit import VisitBookingResponse, VisitBookingCreate
from app.services.project_service import get_all_projects_for_geospatial
from app.core.redis_client import redis_client
from app.core.config import settings
from datetime import datetime
from beanie.operators import In

router = APIRouter()
logger = logging.getLogger(__name__)

# --- User Profile ---

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    region: Optional[str] = None

class UserProfileResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    phone: Optional[str]
    photo_url: Optional[str]
    region: Optional[str]
    role: str

@router.patch("/users/me", response_model=UserProfileResponse, tags=["User - Profile"])
async def update_user_profile(
    current_user: User = Depends(deps.get_current_user),
    full_name: Optional[str] = Form(None),
    email: Optional[EmailStr] = Form(None),
    phone: Optional[str] = Form(None),
    region: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None)
):
    """
    Update current user's profile.
    Accepts multipart/form-data.
    """
    if full_name is not None:
        current_user.full_name = full_name
    if phone is not None:
        current_user.phone = phone
    if email is not None:
        # Check if email is already taken
        user_exists = await User.find_one(User.email == email)
        if user_exists and user_exists.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = email
    if region is not None:
        current_user.region = region
        
    if photo is not None and getattr(photo, 'filename', None):
        # Validate extension
        file_ext = Path(photo.filename).suffix.lower()
        if file_ext not in [".jpg", ".jpeg", ".png", ".heic", ".heif"]:
            raise HTTPException(status_code=400, detail="Invalid photo format. Allowed: .jpg, .jpeg, .png, .heic, .heif")
            
        # Create upload directory
        upload_dir = Path(settings.UPLOAD_DIR) / "profiles" / str(current_user.id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = upload_dir / unique_filename
        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
            current_user.photo_url = f"/uploads/profiles/{current_user.id}/{unique_filename}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")
        finally:
            photo.file.close()
    
    await current_user.save()
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        photo_url=current_user.photo_url,
        region=current_user.region,
        role=current_user.role
    )

@router.get("/users/me", response_model=UserProfileResponse, tags=["User - Profile"])
async def get_user_profile(
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get current user's profile.
    """
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        photo_url=current_user.photo_url,
        region=current_user.region,
        role=current_user.role
    )


# --- History & Wishlist ---

@router.get("/users/me/history", response_model=List[ProjectResponse], tags=["User - History & Wishlist"])
async def get_view_history(
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get projects viewed by the user.
    """
    # Fetch all leads for this user that have a view history
    leads = await ProjectLead.find(ProjectLead.user_id == current_user.id).to_list()
    
    # Extract project IDs
    project_ids = [lead.project_id for lead in leads]
    
    # Fetch projects
    projects = await Project.find(In(Project.id, project_ids)).to_list()
    return projects

@router.get("/users/me/wishlist", response_model=List[ProjectResponse], tags=["User - History & Wishlist"])
async def get_wishlist(
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get projects wishlisted by the user.
    TIER 2 CACHING: Cached for 30 minutes.
    """
    # Try cache first
    cache_key = redis_client.make_key("user", str(current_user.id), "wishlist", "projects")
    cached = await redis_client.get(cache_key)
    if cached:
        return [Project(**p) for p in cached]

    # Cache miss - fetch from database
    leads = await ProjectLead.find(ProjectLead.user_id == current_user.id, ProjectLead.is_wishlisted == True).to_list()
    project_ids = [lead.project_id for lead in leads]
    projects = await Project.find(In(Project.id, project_ids)).to_list()

    # Cache for 30 minutes
    if projects:
        projects_dict = [p.model_dump() for p in projects]
        await redis_client.set(cache_key, projects_dict, 1800)  # 30 minutes

    return projects

# --- Visit Bookings ---

@router.post("/users/me/bookings", response_model=VisitBookingResponse, tags=["User - Visit Bookings"])
async def create_visit_booking(
    data: VisitBookingCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Book a site visit.
    """
    project = await Project.get(data.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    booking = VisitBooking(
        user_id=current_user.id,
        project_id=data.project_id,
        scheduled_time=data.scheduled_time,
        pickup_location=data.pickup_location,
        visitor_name=data.visitor_name or current_user.full_name,
        visitor_phone=data.visitor_phone or current_user.phone
    )
    await booking.create()
    
    # Also update/create a lead entry
    lead = await ProjectLead.find_one(ProjectLead.user_id == current_user.id, ProjectLead.project_id == data.project_id)
    if not lead:
        lead = ProjectLead(
            user_id=current_user.id,
            project_id=data.project_id,
            is_anonymous=False
        )
    
    lead.visit_status = "BOOKED"
    await lead.save()

    return booking

@router.get("/users/me/bookings", response_model=List[VisitBookingResponse], tags=["User - Visit Bookings"])
async def list_my_bookings(
    current_user: User = Depends(deps.get_current_user)
):
    """
    List my visit bookings.
    """
    bookings = await VisitBooking.find(VisitBooking.user_id == current_user.id).sort(-VisitBooking.scheduled_time).to_list()
    return bookings
