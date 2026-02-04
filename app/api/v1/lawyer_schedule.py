from typing import Any, List
from fastapi import APIRouter, Depends, Body, HTTPException
from app.api import deps
from app.models.user import User
from datetime import datetime
from uuid import UUID
from beanie.operators import In, Or
from app.models.lawyer import LawyerProfile, LawyerLead, LawyerEvent
from app.models.legal_call import LegalCallRequest, LegalCallStatus
from app.models.project import Project
from app.schemas.lawyer_portal import (
    LawyerScheduleData, LawyerScheduleEvent, EventType, format_indian_datetime,
    LawyerEventCreate, LawyerEventUpdate
)


router = APIRouter()

async def get_lawyer_id(user: User) -> UUID:
    if user.lawyer_profile_id:
        return user.lawyer_profile_id
    profile = await LawyerProfile.find_one(LawyerProfile.user_id == user.id)
    if profile:
        return profile.id
    raise HTTPException(status_code=404, detail="Lawyer profile not found")

@router.get("/schedule", response_model=LawyerScheduleData)
async def get_schedule(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    lawyer_id = await get_lawyer_id(current_user)
    
    # 1. Fetch Legal Calls (System generated)
    # These are currently global as LegalCallRequest doesn't have lawyer_id yet
    calls = await LegalCallRequest.find(
        In(LegalCallRequest.status, [LegalCallStatus.ACCEPTED, LegalCallStatus.SCHEDULED])
    ).sort("-created_at").limit(20).to_list()
    
    # 2. Fetch Personal Lawyer Events
    personal_events = await LawyerEvent.find(
        {"lawyer_id": lawyer_id, "is_completed": False}
    ).sort("start_time").limit(30).to_list()
    
    today_events = []
    upcoming_events = []
    now = datetime.utcnow()
    
    # Process Legal Calls
    user_ids = list({call.user_id for call in calls})
    users = await User.find({"_id": {"$in": user_ids}}).to_list() if user_ids else []
    user_map = {user.id: user.full_name for user in users}

    project_ids = list({call.project_id for call in calls})
    projects = await Project.find({"_id": {"$in": project_ids}}).to_list() if project_ids else []
    project_map = {project.id: project for project in projects}

    for call in calls:
        scheduled_time = call.scheduled_time or call.created_at
        project = project_map.get(call.project_id)
        location = f"{project.city}, {project.state}" if project and project.city and project.state else (project.city if project else None)
        title = f"Legal Consultation - {project.name}" if project else "Legal Consultation Call"

        evt = LawyerScheduleEvent(
            id=str(call.id),
            title=title,
            date=format_indian_datetime(scheduled_time),
            time_str=scheduled_time.strftime("%I:%M %p"),
            location=location,
            client_name=user_map.get(call.user_id),
            type=EventType.CONSULTATION,
            is_completed=False
        )
        if scheduled_time.date() == now.date(): today_events.append(evt)
        elif scheduled_time > now: upcoming_events.append(evt)

    # Process Personal Events
    for pe in personal_events:
        evt = LawyerScheduleEvent(
            id=str(pe.id),
            title=pe.title,
            date=format_indian_datetime(pe.start_time),
            time_str=pe.start_time.strftime("%I:%M %p"),
            location=pe.location,
            client_name=pe.client_name,
            type=pe.event_type,
            description=pe.description,
            is_completed=pe.is_completed
        )
        if pe.start_time.date() == now.date(): today_events.append(evt)
        elif pe.start_time > now: upcoming_events.append(evt)
            
    # Sort by time
    today_events.sort(key=lambda x: x.date['iso'])
    upcoming_events.sort(key=lambda x: x.date['iso'])

    return LawyerScheduleData(today=today_events, upcoming=upcoming_events)

@router.post("/schedule/events", response_model=LawyerScheduleEvent)
async def create_event(
    event_in: LawyerEventCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    lawyer_id = await get_lawyer_id(current_user)
    event = LawyerEvent(
        lawyer_id=lawyer_id,
        **event_in.dict()
    )
    await event.insert()
    
    return LawyerScheduleEvent(
        id=str(event.id),
        title=event.title,
        date=format_indian_datetime(event.start_time),
        time_str=event.start_time.strftime("%I:%M %p"),
        location=event.location,
        client_name=event.client_name,
        type=event.event_type,
        description=event.description,
        is_completed=event.is_completed
    )

@router.get("/schedule/events/{event_id}", response_model=LawyerScheduleEvent)
async def get_event(
    event_id: UUID,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    event = await LawyerEvent.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    return LawyerScheduleEvent(
        id=str(event.id),
        title=event.title,
        date=format_indian_datetime(event.start_time),
        time_str=event.start_time.strftime("%I:%M %p"),
        location=event.location,
        client_name=event.client_name,
        type=event.event_type,
        description=event.description,
        is_completed=event.is_completed
    )

@router.patch("/schedule/events/{event_id}", response_model=LawyerScheduleEvent)
async def update_event(
    event_id: UUID,
    event_in: LawyerEventUpdate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    event = await LawyerEvent.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    update_data = event_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    event.updated_at = datetime.utcnow()
    await event.save()
    
    return LawyerScheduleEvent(
        id=str(event.id),
        title=event.title,
        date=format_indian_datetime(event.start_time),
        time_str=event.start_time.strftime("%I:%M %p"),
        location=event.location,
        client_name=event.client_name,
        type=event.event_type,
        description=event.description,
        is_completed=event.is_completed
    )

@router.delete("/schedule/events/{event_id}")
async def delete_event(
    event_id: UUID,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    event = await LawyerEvent.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    await event.delete()
    return {"message": "Event deleted"}

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
