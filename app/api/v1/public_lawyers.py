from typing import Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query
from app.models.lawyer import LawyerProfile
from app.models.project import Project
from app.models.lawyer_consultation import LawyerConsultation, ConsultationStatus
from app.schemas.lawyer import (
    LawyerEnvelope, 
    AvailabilityEnvelope, 
    DateAvailability, 
    TimeSlot,
    LawyerResponse
)
from beanie.operators import In

router = APIRouter()

@router.get("/projects/{project_id}", response_model=LawyerEnvelope)
async def get_lawyer_by_project(project_id: UUID) -> Any:
    """
    Retrieves lawyer associated with a project.
    """
    project = await Project.get(project_id)
    if not project or not project.lawyer_id:
        # Fallback to a default lawyer if none is linked to the project yet
        default_lawyer = await LawyerProfile.find_one(LawyerProfile.is_active == True)
        if not default_lawyer:
            raise HTTPException(status_code=404, detail="No lawyer associated with this project.")
        lawyer = default_lawyer
    else:
        lawyer = await LawyerProfile.get(project.lawyer_id)
        
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found.")
        
    # Map model to response schema
    return {
        "status": "success",
        "data": LawyerResponse(
            id=lawyer.id,
            name=lawyer.name,
            specialization=", ".join(lawyer.specialization) if lawyer.specialization else "General Property Law",
            experience=f"{lawyer.experience_years}+ Yrs",
            rating=lawyer.rating,
            review_count=lawyer.review_count,
            image_url=lawyer.image_url,
            fee=lawyer.fee
        )
    }

@router.get("/{lawyer_id}/availability", response_model=AvailabilityEnvelope)
async def get_lawyer_availability(
    lawyer_id: UUID,
    start_date: str = Query(..., example="2024-04-16"),
    end_date: str = Query(..., example="2024-04-20")
) -> Any:
    """
    Fetches available slots for a lawyer.
    """
    lawyer = await LawyerProfile.get(lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")

    # Fetch existing confirmed bookings
    existing_bookings = await LawyerConsultation.find(
        LawyerConsultation.lawyer_id == lawyer_id,
        LawyerConsultation.date >= start_date,
        LawyerConsultation.date <= end_date,
        In(LawyerConsultation.status, [ConsultationStatus.CONFIRMED, ConsultationStatus.PENDING])
    ).to_list()

    booked_map = {}
    for b in existing_bookings:
        booked_map[(b.date, b.time)] = True

    # Generate standard slots (10:00 AM to 5:00 PM)
    slots_config = ["10:00 AM", "11:30 AM", "01:00 PM", "02:30 PM", "04:00 PM"]
    
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    results = []
    curr = start_dt
    while curr <= end_dt:
        date_str = curr.strftime("%Y-%m-%d")
        day_slots = []
        for s in slots_config:
            is_avail = not booked_map.get((date_str, s), False)
            # Weekend Check (0=Mon, 6=Sun)
            if curr.weekday() in [5, 6]:
                is_avail = False
            day_slots.append(TimeSlot(time=s, available=is_avail))
            
        results.append(DateAvailability(date=date_str, slots=day_slots))
        curr += timedelta(days=1)

    return {
        "status": "success",
        "data": results
    }
