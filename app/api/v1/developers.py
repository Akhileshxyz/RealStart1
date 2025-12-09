from typing import Any, List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User
from app.models.developer import Developer
from app.schemas.developer import DeveloperCreate, DeveloperUpdate, DeveloperResponse

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
    return developers

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
    update_data["updated_at"] = datetime.utcnow()
    
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
