from typing import Any, List, Optional, Dict, Tuple
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User
from app.models.lawyer import LawyerProfile, LawyerLead, LawyerLeadStatus
from app.schemas.lawyer_portal import (
    LawyerClient, LawyerClientStats, ClientLeadCreate,
    LawyerClientsData, LawyerClientsStatsSummary
)
from uuid import UUID
from datetime import datetime
import urllib.parse

router = APIRouter()


def normalize_phone(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return None
    cleaned = phone.replace(" ", "").replace("-", "")
    if cleaned.startswith("+"):
        return cleaned
    if len(cleaned) == 10 and cleaned.isdigit():
        return f"+91{cleaned}"
    return cleaned

async def get_lawyer_id(user: User) -> UUID:
    if user.lawyer_profile_id:
        return user.lawyer_profile_id
    profile = await LawyerProfile.find_one(LawyerProfile.user_id == user.id)
    if profile:
        return profile.id
    raise HTTPException(status_code=404, detail="Lawyer profile not found")

@router.get("/clients", response_model=LawyerClientsData)
async def list_clients(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    lawyer_id = await get_lawyer_id(current_user)
    leads = await LawyerLead.find(LawyerLead.lawyer_id == lawyer_id).sort("-created_at").to_list()
    
    client_map: Dict[Tuple[str, str], List[LawyerLead]] = {}
    for lead in leads:
        key = (lead.client_phone or "", lead.client_email or "")
        client_map.setdefault(key, []).append(lead)

    clients: List[LawyerClient] = []
    for (phone, email), grouped_leads in client_map.items():
        primary = grouped_leads[0]
        initials = "".join([n[0] for n in primary.client_name.split(" ")[:2]]).upper()
        active_cases = sum(
            1 for l in grouped_leads
            if l.status not in [LawyerLeadStatus.COMPLETED, LawyerLeadStatus.LOST]
        )
        completed_cases = sum(1 for l in grouped_leads if l.status == LawyerLeadStatus.COMPLETED)

        stats = LawyerClientStats(
            total_cases=len(grouped_leads),
            active_cases=active_cases,
            completed_cases=completed_cases
        )

        clients.append(LawyerClient(
            id=str(primary.id),
            initials=initials,
            name=primary.client_name,
            email=email or None,
            phone=normalize_phone(phone),
            city=primary.client_city,
            stats=stats
        ))

    total_clients = len(clients)
    active_clients = sum(1 for c in clients if c.stats.active_cases > 0)
    cases_completed = sum(c.stats.completed_cases for c in clients)
    now = datetime.utcnow()
    new_this_month = len({
        (lead.client_phone or "", lead.client_email or "")
        for lead in leads
        if lead.created_at.month == now.month and lead.created_at.year == now.year
    })

    summary = LawyerClientsStatsSummary(
        total_clients=total_clients,
        active_clients=active_clients,
        cases_completed=cases_completed,
        new_this_month=new_this_month
    )

    return LawyerClientsData(stats=summary, clients=clients)

@router.post("/clients")
async def create_client_lead(
    client_data: ClientLeadCreate = Body(...),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    lawyer_id = await get_lawyer_id(current_user)
    
    lead = LawyerLead(
        lawyer_id=lawyer_id,
        client_name=client_data.client_name,
        client_phone=normalize_phone(client_data.client_phone) or client_data.client_phone,
        client_email=client_data.client_email,
        client_city=client_data.client_city,
        property_id=client_data.property_id,
        project_name=client_data.project_name,
        service_type=client_data.service_type,
        priority=client_data.priority,
        service_fee=client_data.service_fee or 0.0,
        status=LawyerLeadStatus.NEW,
        notes=client_data.notes
    )
    await lead.insert()
    return lead

@router.get("/clients/{id}/whatsapp-link")
async def get_whatsapp_link(
    id: UUID,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    lead = await LawyerLead.get(id)
    if not lead:
        raise HTTPException(status_code=404, detail="Client/Lead not found")
        
    message = f"Hello {lead.client_name}, this is regarding your legal inquiry."
    encoded_message = urllib.parse.quote(message)
    phone = lead.client_phone.replace("+", "").replace(" ", "")
    link = f"https://wa.me/{phone}?text={encoded_message}"
    
    return {"whatsapp_link": link}
