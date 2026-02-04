from typing import Any, List, Optional
from fastapi import APIRouter, Depends
from app.api import deps
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.schemas.project import ProjectListResponse

router = APIRouter()

@router.get("/properties", response_model=List[ProjectListResponse])
async def list_lawyer_properties(
    search: Optional[str] = None,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get a list of properties (projects) for the lawyer portal.
    Used for linking properties to client leads.
    """
    query = {"status": ProjectStatus.APPROVED}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    
    projects = await Project.find(query).limit(50).to_list()
    return projects
