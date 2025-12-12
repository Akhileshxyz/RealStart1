import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.api import deps
from app.models.user import User
from app.models.lead import ProjectLead
from app.models.project import Project
from app.models.landmark import Landmark
from app.models.visit import VisitBooking, VisitStatus
from app.schemas.project import ProjectResponse
from app.schemas.lead import LeadResponse
from app.schemas.landmark import LandmarkResponse, LandmarkCreate
from app.schemas.visit import VisitBookingResponse, VisitBookingCreate
from datetime import datetime
from beanie.operators import In

router = APIRouter()
logger = logging.getLogger(__name__)

# --- User Profile ---

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    # Password update should be separate secure endpoint typically, but creating placeholder
    
class UserProfileResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    role: str

@router.patch("/users/me", response_model=UserProfileResponse)
async def update_user_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Update current user's profile.
    """
    if data.full_name is not None:
        current_user.full_name = data.full_name
    if data.phone is not None:
        current_user.phone = data.phone
    
    await current_user.save()
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        role=current_user.role
    )

@router.get("/users/me", response_model=UserProfileResponse)
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
        role=current_user.role
    )


# --- History & Wishlist ---

@router.get("/users/me/history", response_model=List[ProjectResponse])
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

@router.get("/users/me/wishlist", response_model=List[ProjectResponse])
async def get_wishlist(
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get projects wishlisted by the user.
    """
    leads = await ProjectLead.find(ProjectLead.user_id == current_user.id, ProjectLead.is_wishlisted == True).to_list()
    project_ids = [lead.project_id for lead in leads]
    projects = await Project.find(In(Project.id, project_ids)).to_list()
    return projects

# --- Landmarks (Market Analyzer) ---

@router.get("/public/landmarks", response_model=List[LandmarkResponse])
async def list_landmarks(
    city: Optional[str] = None
):
    """
    List landmarks, optionally filtered by city.
    """
    if city:
        landmarks = await Landmark.find(Landmark.city == city).to_list()
    else:
        landmarks = await Landmark.find_all().to_list()
    return landmarks

@router.get("/public/landmarks/{id}", response_model=LandmarkResponse)
async def get_landmark(id: str):
    """
    Get detailed market data for a landmark.
    """
    landmark = await Landmark.get(id)
    if not landmark:
        raise HTTPException(status_code=404, detail="Landmark not found")
    return landmark

# Admin endpoint to create landmarks (for testing/population)
@router.post("/admin/landmarks", response_model=LandmarkResponse)
async def create_landmark(
    data: LandmarkCreate,
    current_admin: User = Depends(deps.get_current_active_admin)
):
    landmark = Landmark(**data.dict())
    await landmark.create()
    return landmark


# --- Visit Bookings ---

@router.post("/users/me/bookings", response_model=VisitBookingResponse)
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

@router.get("/users/me/bookings", response_model=List[VisitBookingResponse])
async def list_my_bookings(
    current_user: User = Depends(deps.get_current_user)
):
    """
    List my visit bookings.
    """
    bookings = await VisitBooking.find(VisitBooking.user_id == current_user.id).sort(-VisitBooking.scheduled_time).to_list()
    return bookings
