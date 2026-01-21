from typing import Any, List
from fastapi import APIRouter, Depends, Body, HTTPException
from app.api import deps
from app.models.user import User
from app.models.legal_call import LegalCallRequest, LegalCallStatus
from app.models.project import Project
from app.schemas.lawyer_portal import (
    LawyerScheduleData, LawyerScheduleEvent, EventType, format_indian_datetime
)
from datetime import datetime
from uuid import UUID
from beanie.operators import In
from beanie.operators import In

router = APIRouter()

@router.get("/schedule", response_model=LawyerScheduleData)
async def get_schedule(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # 1. Fetch Legal Calls (closest thing to scheduled events)
    calls = await LegalCallRequest.find(
        In(LegalCallRequest.status, [LegalCallStatus.ACCEPTED, LegalCallStatus.SCHEDULED])
    ).sort("created_at").limit(25).to_list()
    
    today_events = []
    upcoming_events = []
    
    now = datetime.utcnow()
    
    user_ids = list({call.user_id for call in calls})
    users = await User.find(User.id.in_(user_ids)).to_list() if user_ids else []
    user_map = {user.id: user.full_name for user in users}

    project_ids = list({call.project_id for call in calls})
    projects = await Project.find(Project.id.in_(project_ids)).to_list() if project_ids else []
    project_map = {project.id: project for project in projects}

    # Process calls into events
    for call in calls:
        scheduled_time = call.scheduled_time or call.created_at
        project = project_map.get(call.project_id)
        location = None
        if project and project.city and project.state:
            location = f"{project.city}, {project.state}"
        elif project and project.city:
            location = project.city

        title = "Legal Consultation Call"
        if project:
            title = f"Legal Consultation - {project.name}"

        evt = LawyerScheduleEvent(
            id=str(call.id),
            title=title,
            date=format_indian_datetime(scheduled_time),
            time_str=scheduled_time.strftime("%I:%M %p"),
            location=location,
            client_name=user_map.get(call.user_id),
            type=EventType.MEETING,
        )
        
        # Simple date aggregation
        if scheduled_time.date() == now.date():
            today_events.append(evt)
        elif scheduled_time > now:
            upcoming_events.append(evt)
            
    return LawyerScheduleData(
        today=today_events,
        upcoming=upcoming_events
    )

@router.patch("/schedule/{id}/complete")
async def complete_event(
    id: str,
    notes: str = Body(...),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Logic to complete call
    try:
        uuid_id = UUID(id)
        req = await LegalCallRequest.get(uuid_id)
    except ValueError:
        # If it was an invalid UUID, handle gracefully
        return {"message": "Event updated"}
        
    if not req:
        # If the event is not found, handle gracefully
        return {"message": "Event updated"}
        
    req.status = LegalCallStatus.COMPLETED
    req.lawyer_notes = notes
    req.completed_at = datetime.utcnow()
    await req.save()
    
    return {"message": "Event completed", "id": str(id)}
