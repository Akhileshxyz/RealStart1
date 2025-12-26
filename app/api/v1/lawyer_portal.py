from typing import List, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User, UserRole
from app.models.project import Project, LegalDocumentStatus
from app.models.legal_call import LegalCallRequest, LegalCallStatus
from app.models.lawyer import (
    LawyerProfile, LawyerLead, LawyerSubscription, 
    LawyerLeadStatus, LawyerPaymentStatus
)
import urllib.parse

router = APIRouter()

# Dependency to check if user is a Lawyer (or Super Admin)
def check_lawyer_access(current_user: User = Depends(deps.get_current_user)):
    if current_user.role not in [UserRole.LAWYER, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized as Lawyer")
    return current_user

async def get_my_profile(user: User) -> LawyerProfile:
    # If using linked profile
    if user.lawyer_profile_id:
        profile = await LawyerProfile.get(user.lawyer_profile_id)
        if profile:
            return profile
    
    # Fallback: find by user_id
    profile = await LawyerProfile.find_one(LawyerProfile.user_id == user.id)
    if not profile:
        # Auto-create if not exists for a valid lawyer user?
        # For now, create one
        profile = LawyerProfile(user_id=user.id)
        await profile.insert()
        
        # Link back to user if not linked
        if not user.lawyer_profile_id:
            user.lawyer_profile_id = profile.id
            await user.save()
            
    return profile

# --- Dashboard Module ---

@router.get("/dashboard/analytics")
async def get_dashboard_analytics(
    current_user: User = Depends(check_lawyer_access)
) -> Any:
    lawyer_id = (await get_my_profile(current_user)).id
    
    # Leads count
    total_leads = await LawyerLead.find(LawyerLead.lawyer_id == lawyer_id).count()
    new_leads = await LawyerLead.find(LawyerLead.lawyer_id == lawyer_id, LawyerLead.status == LawyerLeadStatus.NEW).count()
    
    # Document Verification Pending
    # (This is global across projects for now, or we could filter by assigned projects if we had that assignment logic)
    # Re-using the query from incoming-items but counting
    projects_with_docs = await Project.find({"documents.0": {"$exists": True}}).to_list()
    pending_docs = 0
    for p in projects_with_docs:
        pending_docs += sum(1 for d in p.documents if d.status == LegalDocumentStatus.PENDING)

    # Earnings (Mock logic for now as we don't have transaction history table fully spec'd for lawyers yet)
    total_earnings = 50000.0 # Placeholder
    pending_payouts = 12000.0 # Placeholder
    
    return {
        "total_leads": total_leads,
        "new_leads": new_leads,
        "pending_document_verifications": pending_docs,
        "earnings": {
            "total_revenue": total_earnings,
            "pending_payouts": pending_payouts
        }
    }

@router.get("/notifications")
async def get_notifications(
    current_user: User = Depends(check_lawyer_access)
) -> Any:
    # Mock notifications
    return [
        {"id": "1", "title": "New Lead", "message": "You have a new inquiry from Rajesh", "timestamp": datetime.utcnow()},
        {"id": "2", "title": "Document Update", "message": "Prestige City layout uploaded", "timestamp": datetime.utcnow() - timedelta(hours=2)}
    ]

# --- Client & Lead Management (CRM) ---

@router.get("/leads")
async def list_leads(
    status: Optional[LawyerLeadStatus] = None,
    current_user: User = Depends(check_lawyer_access)
) -> Any:
    lawyer_id = (await get_my_profile(current_user)).id
    query = {LawyerLead.lawyer_id: lawyer_id}
    if status:
        query[LawyerLead.status] = status
        
    leads = await LawyerLead.find(query).sort("-created_at").to_list()
    return leads

@router.post("/leads")
async def create_lead(
    lead_data: dict = Body(...),
    current_user: User = Depends(check_lawyer_access)
) -> Any:
    lawyer_id = (await get_my_profile(current_user)).id
    
    lead = LawyerLead(
        lawyer_id=lawyer_id,
        client_name=lead_data["client_name"],
        client_phone=lead_data["client_phone"],
        property_id=lead_data.get("property_id"),
        status=LawyerLeadStatus.NEW,
        notes=lead_data.get("notes")
    )
    await lead.insert()
    return lead

@router.patch("/leads/{lead_id}/status")
async def update_lead_status(
    lead_id: UUID,
    status: LawyerLeadStatus = Body(..., embed=True),
    current_user: User = Depends(check_lawyer_access)
) -> Any:
    lead = await LawyerLead.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    lawyer_id = (await get_my_profile(current_user)).id
    if lead.lawyer_id != lawyer_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    lead.status = status
    await lead.save()
    return lead

@router.get("/leads/{lead_id}/whatsapp-link")
async def get_whatsapp_link(
    lead_id: UUID,
    current_user: User = Depends(check_lawyer_access)
) -> Any:
    lead = await LawyerLead.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    # Format message
    message = f"Hello {lead.client_name}, this is regarding your legal inquiry."
    if lead.property_id:
        # Optionally fetch property details
        message += " about the property."
        
    encoded_message = urllib.parse.quote(message)
    phone = lead.client_phone.replace("+", "").replace(" ", "")
    link = f"https://wa.me/{phone}?text={encoded_message}"
    
    return {"whatsapp_link": link}

# --- Lawyer Profile ---

@router.get("/profile")
async def get_profile(
    current_user: User = Depends(check_lawyer_access)
) -> Any:
    return await get_my_profile(current_user)

@router.patch("/profile")
async def update_profile(
    profile_data: dict = Body(...),
    current_user: User = Depends(check_lawyer_access)
) -> Any:
    profile = await get_my_profile(current_user)
    
    # Update fields
    if "bio" in profile_data: profile.bio = profile_data["bio"]
    if "specialization" in profile_data: profile.specialization = profile_data["specialization"]
    if "bar_council_id" in profile_data: profile.bar_council_id = profile_data["bar_council_id"]
    if "experience_years" in profile_data: profile.experience_years = profile_data["experience_years"]
    if "is_online" in profile_data: profile.is_online = profile_data["is_online"]
    if "cities" in profile_data: profile.cities = profile_data["cities"]
    if "languages" in profile_data: profile.languages = profile_data["languages"]
    
    profile.updated_at = datetime.utcnow()
    await profile.save()
    return profile

# --- Subscription Management ---

@router.get("/subscription")
async def get_subscription(
    current_user: User = Depends(check_lawyer_access)
) -> Any:
    lawyer_id = (await get_my_profile(current_user)).id
    sub = await LawyerSubscription.find_one(
        LawyerSubscription.lawyer_id == lawyer_id,
        LawyerSubscription.is_active == True
    )
    if not sub:
        return {"status": "NO_ACTIVE_PLAN", "plan": None}
    return sub

# --- Existing: Incoming Items (Documents) ---

@router.get("/incoming-items")
async def list_incoming_items(
    current_user: User = Depends(check_lawyer_access)
) -> Any:
    """
    List projects that have documents for review.
    Filter: Projects with at least one document.
    """
    # MongoDB query: {"documents.0": {"$exists": True}}
    projects = await Project.find({"documents.0": {"$exists": True}}).to_list()
    
    # Summary response
    results = []
    for p in projects:
        pending_count = sum(1 for d in p.documents if d.status == LegalDocumentStatus.PENDING)
        results.append({
            "project_id": p.id,
            "project_name": p.name,
            "developer_id": p.developer_id,
            "total_docs": len(p.documents),
            "pending_docs": pending_count,
            "legal_status_summary": p.legal_status_summary
        })
    return results

@router.get("/projects/{project_id}/documents")
async def get_project_documents(
    project_id: UUID,
    current_user: User = Depends(check_lawyer_access)
) -> Any:
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.documents

@router.patch("/projects/{project_id}/documents/{doc_id}")
async def review_document(
    project_id: UUID,
    doc_id: UUID,
    status: LegalDocumentStatus = Body(...),
    lawyer_notes: str = Body(None),
    current_user: User = Depends(check_lawyer_access)
) -> Any:
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    doc = next((d for d in project.documents if d.id == doc_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc.status = status
    if lawyer_notes is not None:
        doc.lawyer_notes = lawyer_notes
    doc.verified_at = datetime.utcnow()
    
    # Audit Trail (Implicitly logged via verified_at and we might want to log who did it if multiple lawyers)
    # doc.verified_by = current_user.id # (If we added this field, but for now strict adherence to existing model unless changed)
    
    await project.save()
    return {"message": "Document updated", "document": doc}

# --- Existing: Legal Calls ---

@router.get("/legal-calls")
async def list_legal_calls(
    status: LegalCallStatus = None,
    current_user: User = Depends(check_lawyer_access)
) -> Any:
    query = {}
    if status:
        query["status"] = status
    
    calls = await LegalCallRequest.find(query).sort("-created_at").to_list()
    return calls

@router.patch("/legal-calls/{request_id}/complete")
async def complete_legal_call(
    request_id: UUID,
    lawyer_notes: str = Body(...),
    opinion_file_url: str = Body(None),
    current_user: User = Depends(check_lawyer_access)
) -> Any:
    req = await LegalCallRequest.get(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    req.status = LegalCallStatus.COMPLETED
    req.lawyer_notes = lawyer_notes
    req.opinion_file_url = opinion_file_url
    req.completed_at = datetime.utcnow()
    
    await req.save()
    return {"message": "Call marked as completed", "request": req}
