from typing import List, Any
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User, UserRole
from app.models.project import Project, LegalDocumentStatus
from app.models.legal_call import LegalCallRequest, LegalCallStatus

router = APIRouter()

# Dependency to check if user is a Lawyer (or Super Admin)
def check_lawyer_access(current_user: User = Depends(deps.get_current_user)):
    if current_user.role not in [UserRole.LAWYER, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized as Lawyer")
    return current_user

# --- Incoming Items (Documents) ---

@router.get("/incoming-items")
async def list_incoming_items(
    current_user: User = Depends(check_lawyer_access)
) -> Any:
    """
    List projects that have documents for review.
    Filter: Projects with at least one document.
    """
    # Simple query: find projects where documents array is not empty
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
    
    # Update project-level summary if needed (simple logic: append status)
    # Or just keep it manual. Let's auto-update summary if all verified?
    # For now, simplistic.
    
    await project.save()
    return {"message": "Document updated", "document": doc}

# --- Legal Calls ---

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
