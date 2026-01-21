from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User
from app.models.lawyer import LawyerProfile, LawyerLead, LawyerLeadStatus
from app.models.project import Project, LegalDocumentStatus
from app.models.developer import Developer
from app.schemas.lawyer_portal import (
    LawyerCase, CaseStatus, CasePriority, ServiceType,
    LawyerCasesData, LawyerCasesStats, format_indian_datetime
)
from datetime import datetime
from uuid import UUID

router = APIRouter()

# Helper to get lawyer ID (duplicated for independent module usage, could be in deps)
async def get_lawyer_id(user: User) -> UUID:
    if user.lawyer_profile_id:
        return user.lawyer_profile_id
    profile = await LawyerProfile.find_one(LawyerProfile.user_id == user.id)
    if profile:
        return profile.id
    raise HTTPException(status_code=404, detail="Lawyer profile not found")

@router.get("/cases", response_model=LawyerCasesData)
async def list_cases(
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # In a full system, "Cases" might come from a dedicated "LegalCase" collection.
    # For this refactor, we are aggregating functionality from Leads and Projects.
    # 1. Leads (Direct inquiries)
    # 2. Projects (Document verification requests)
    
    lawyer_id = await get_lawyer_id(current_user)
    
    all_cases: List[LawyerCase] = []
    
    # Fetch Leads
    leads_query = {LawyerLead.lawyer_id: lawyer_id}
    if status and status.upper() in LawyerLeadStatus.__members__:
        leads_query[LawyerLead.status] = LawyerLeadStatus[status.upper()]
        
    leads = await LawyerLead.find(leads_query).sort("-created_at").to_list()
    
    for lead in leads:
        # Search Filter (Basic in-memory for now)
        if search and search.lower() not in lead.client_name.lower():
            continue
            
        initials = "".join([n[0] for n in lead.client_name.split(" ")[:2]]).upper()
        
        status_enum = CaseStatus.PENDING
        if lead.status == LawyerLeadStatus.COMPLETED:
            status_enum = CaseStatus.COMPLETED
        elif lead.status == LawyerLeadStatus.LOST:
            status_enum = CaseStatus.ON_HOLD
        elif lead.status != LawyerLeadStatus.NEW:
            status_enum = CaseStatus.IN_PROGRESS

        priority = CasePriority.MEDIUM
        if lead.priority and lead.priority.upper() in CasePriority.__members__:
            priority = CasePriority[lead.priority.upper()]
        elif status_enum == CaseStatus.PENDING and (datetime.utcnow() - lead.created_at).days >= 7:
            priority = CasePriority.HIGH

        service_type = ServiceType.LEGAL_CONSULTATION
        if lead.service_type:
            for service in ServiceType:
                if service.value.lower() == lead.service_type.lower():
                    service_type = service
                    break

        all_cases.append(LawyerCase(
            id=str(lead.id),
            client_initials=initials,
            client_name=lead.client_name,
            project_name=lead.project_name,
            service_type=service_type,
            status=status_enum,
            priority=priority,
            location=lead.client_city,
            date=format_indian_datetime(lead.created_at),
            lead_id=str(lead.id)
        ))
        
    # Fetch Projects with pending docs (Global view logic from original code)
    # Ideally should be assigned projects
    projects = await Project.find({"documents.0": {"$exists": True}}).to_list()
    developer_ids = list({p.developer_id for p in projects})
    developers = await Developer.find(Developer.id.in_(developer_ids)).to_list() if developer_ids else []
    developer_map = {dev.id: dev for dev in developers}
    for p in projects:
        # Search filter
        if search and search.lower() not in p.name.lower():
            continue

        pending_docs_count = sum(1 for d in p.documents if d.status == LegalDocumentStatus.PENDING)
        
        c_status = CaseStatus.COMPLETED
        if pending_docs_count > 0:
            c_status = CaseStatus.PENDING
            
        city_state = None
        if p.city and p.state:
            city_state = f"{p.city}, {p.state}"
        elif p.city:
            city_state = p.city

        developer = developer_map.get(p.developer_id)
        developer_name = developer.name if developer else "Developer"
        developer_initials = "".join([n[0] for n in developer_name.split(" ")[:2]]).upper()

        all_cases.append(LawyerCase(
            id=str(p.id),
            client_initials=developer_initials,
            client_name=developer_name,
            project_name=p.name,
            service_type=ServiceType.DOCUMENT_REVIEW,
            status=c_status,
            priority=CasePriority.HIGH if pending_docs_count > 0 else CasePriority.LOW,
            location=city_state,
            date=format_indian_datetime(p.created_at or datetime.utcnow()),
            project_id=str(p.id)
        ))
    if status and status.upper() in CaseStatus.__members__:
        all_cases = [c for c in all_cases if c.status == CaseStatus[status.upper()]]

    stats = LawyerCasesStats(
        total_cases=len(all_cases),
        pending_cases=sum(1 for c in all_cases if c.status == CaseStatus.PENDING),
        in_progress_cases=sum(1 for c in all_cases if c.status == CaseStatus.IN_PROGRESS),
        completed_cases=sum(1 for c in all_cases if c.status == CaseStatus.COMPLETED),
        on_hold_cases=sum(1 for c in all_cases if c.status == CaseStatus.ON_HOLD)
    )

    filters = {
        "status": [s.value for s in CaseStatus],
        "service_type": [s.value for s in ServiceType],
        "priority": [p.value for p in CasePriority]
    }

    return LawyerCasesData(stats=stats, filters=filters, cases=all_cases)

@router.get("/cases/{case_id}/documents")
async def get_case_documents(
    case_id: UUID,  # Can be project_id based on logic above
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Assuming case_id correlates to Project ID for doc reviews
    project = await Project.get(case_id)
    if not project:
         raise HTTPException(status_code=404, detail="Case/Project not found")
    return project.documents

@router.patch("/cases/{case_id}/documents/{doc_id}")
async def review_document(
    case_id: UUID,
    doc_id: UUID,
    status: LegalDocumentStatus = Body(...),
    lawyer_notes: str = Body(None),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    project = await Project.get(case_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    doc = next((d for d in project.documents if d.id == doc_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc.status = status
    if lawyer_notes is not None:
        doc.lawyer_notes = lawyer_notes
    doc.verified_at = datetime.utcnow()
    
    await project.save()
    return {"message": "Document updated", "document": doc}
