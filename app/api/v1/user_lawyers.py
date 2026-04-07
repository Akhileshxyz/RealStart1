from typing import Any, List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User
from app.models.lawyer import LawyerProfile
from app.models.project import Project
from app.models.lawyer_consultation import LawyerConsultation, ConsultationStatus
from app.schemas.lawyer import (
    ConsultationCreate, 
    BookingEnvelope, 
    HistoryEnvelope, 
    ConsultationHistoryItem
)
from beanie.operators import In

router = APIRouter()

@router.post("/", response_model=BookingEnvelope)
async def book_consultation(
    booking: ConsultationCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Creates a consultation booking and initiates payment.
    """
    lawyer = await LawyerProfile.get(booking.lawyer_id)
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer profile not found.")

    # 1. Server-side Availability Validation (Safety Check)
    existing_consult = await LawyerConsultation.find_one(
        LawyerConsultation.lawyer_id == booking.lawyer_id,
        LawyerConsultation.date == booking.date,
        LawyerConsultation.time == booking.time,
        In(LawyerConsultation.status, [ConsultationStatus.CONFIRMED])
    )
    if existing_consult:
        raise HTTPException(status_code=409, detail="This slot has just been booked. Please choose another.")

    # 2. Create Consultation Record
    consultation = LawyerConsultation(
        user_id=current_user.id,
        lawyer_id=booking.lawyer_id,
        project_id=booking.project_id,
        date=booking.date,
        time=booking.time,
        mode=booking.mode,
        amount=lawyer.fee
    )
    await consultation.create()

    # 3. Simulate Payment Portal URL
    booking_id = f"LC-{str(consultation.id).split('-')[0].upper()}"
    payment_url = f"https://payment-gateway.com/session/{consultation.id}"

    return {
        "status": "success",
        "data": {
            "booking_id": booking_id,
            "payment_portal_url": payment_url,
            "amount": lawyer.fee
        }
    }

@router.get("/", response_model=HistoryEnvelope)
async def list_my_consultations(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Lists all consultations booked by the user.
    """
    consultations = await LawyerConsultation.find(
        LawyerConsultation.user_id == current_user.id
    ).sort("-created_at").to_list()

    history = []
    # Batch fetch lawyers for naming
    lawyer_ids = [c.lawyer_id for c in consultations]
    lawyers = await LawyerProfile.find(In(LawyerProfile.id, lawyer_ids)).to_list()
    lawyer_map = {l.id: l.name for l in lawyers}

    for c in consultations:
        history.append(ConsultationHistoryItem(
            id=f"LC-{str(c.id).split('-')[0].upper()}",
            lawyer_name=lawyer_map.get(c.lawyer_id, "Property Lawyer"),
            date=c.date,
            time=c.time,
            mode=c.mode,
            status=c.status.value
        ))

    return {
        "status": "success",
        "data": history
    }
