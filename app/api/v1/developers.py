from typing import Any, List
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User
from app.models.developer import Developer
from app.models.project import Project
from app.models.landmark import Landmark
from app.schemas.developer import DeveloperCreate, DeveloperUpdate, DeveloperResponse
from app.core.security import create_access_token
from datetime import timedelta

router = APIRouter()

@router.post("/", response_model=DeveloperResponse)
async def create_developer(
    *,
    developer_in: DeveloperCreate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Create new developer (Admin only).
    """
    developer = Developer(**developer_in.model_dump())
    await developer.insert()
    return developer

@router.get("/", response_model=List[DeveloperResponse])
async def read_developers(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Retrieve developers.
    """
    developers = await Developer.find_all().skip(skip).limit(limit).to_list()
    
    # Calculate Tenure
    results = []
    now = datetime.now(timezone.utc)
    for dev in developers:
        resp = DeveloperResponse.model_validate(dev)
        if dev.created_at:
            # Simple approximation
            delta = now - dev.created_at.replace(tzinfo=timezone.utc)
            years = delta.days // 365
            months = (delta.days % 365) // 30
            resp.tenure = f"{years} years, {months} months"
        results.append(resp)
        
    return results

@router.get("/{developer_id}", response_model=DeveloperResponse)
async def read_developer(
    developer_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get developer by ID.
    """
    developer = await Developer.get(developer_id)
    if not developer:
        raise HTTPException(status_code=404, detail="Developer not found")
    return developer

@router.put("/{developer_id}", response_model=DeveloperResponse)
async def update_developer(
    developer_id: UUID,
    developer_in: DeveloperUpdate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update a developer.
    """
    developer = await Developer.get(developer_id)
    if not developer:
        raise HTTPException(status_code=404, detail="Developer not found")
    
    update_data = developer_in.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await developer.set(update_data)
    return developer

@router.delete("/{developer_id}", response_model=DeveloperResponse)
async def delete_developer(
    developer_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Delete a developer.
    """
    developer = await Developer.get(developer_id)
    if not developer:
        raise HTTPException(status_code=404, detail="Developer not found")
    await developer.delete()
    return developer
    await developer.delete()
    return developer

# --- Enhancements ---

@router.get("/{developer_id}/projects-by-location", response_model=Any)
async def get_developer_projects_by_location(
    developer_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get breakdown of developer's projects by City/Landmark.
    """
    projects = await Project.find({"developer_id": developer_id}).to_list()
    
    # Since Project doesn't store 'City' name directly but uses IDs or internal logic,
    # we might need to fetch associated landmarks or just use available fields.
    # Assuming 'address' or 'city_id' (if added) is used. 
    # For now, we'll try to group by 'address' substring or 'approval_type' as proxy if city missing.
    # Or query related landmarks if project has location.
    
    location_stats = {}
    
    for p in projects:
        # Simplistic extraction or grouping
        loc = "Unknown"
        if p.address:
            # naive city extraction
            loc = p.address.split(",")[-1].strip() 
        elif p.city_id:
           # If we implemented city_id link
           pass
           
        if loc not in location_stats:
            location_stats[loc] = 0
        location_stats[loc] += 1
        
    return location_stats

@router.post("/{developer_id}/impersonate", response_model=Any)
async def impersonate_developer(
    developer_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Generate a temporary login token for the admin to view the system as this developer.
    """
    developer = await Developer.get(developer_id)
    if not developer:
        raise HTTPException(status_code=404, detail="Developer not found")
        
    # Find the User entity for this developer
    # Assuming Developer model links to User or we search User by role and developer_id
    user = await User.find_one({"email": developer.email}) # Best guess link
    if not user:
         raise HTTPException(status_code=404, detail="User account for developer not found")

    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": f"Impersonating {developer.name}"
    }
