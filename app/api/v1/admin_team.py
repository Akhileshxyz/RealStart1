from typing import Any, List, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User, UserRole
from app.models.team import StaffTask, TaskStatus, SharedClient
from app.schemas.auth import UserCreate # Correct import logic
from app.schemas.user import UserUpdate # Assuming this is in user.py
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

# --- Staff Management ---

@router.get("/", response_model=List[User])
async def list_team_members(
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    List all internal team members (Sales, Marketing, Manager).
    """
    staff_roles = [UserRole.SALES, UserRole.MARKETING, UserRole.MANAGER, UserRole.ADMIN]
    # Exclude Super Admin to prevent accidental edits? Or include all.
    users = await User.find({"role": {"$in": staff_roles}}).to_list()
    return users

@router.post("/", response_model=User)
async def create_team_member(
    user_in: UserCreate, # Using schema if available, else standard body
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Add a new team member.
    """
    # Verify role is a staff role
    if user_in.role not in [UserRole.SALES, UserRole.MARKETING, UserRole.MANAGER]:
         raise HTTPException(status_code=400, detail="Invalid role for team member")
         
    # Check if user exists
    user = await User.find_one(User.email == user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
        
    # Create user logic (hashing pw etc)
    # Ideally use a service function from app.services.user_service
    # For now, simplistic creation:
    from app.core.security import get_password_hash
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=True
    )
    await user.save()
    return user

@router.delete("/{user_id}")
async def remove_team_member(
    user_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Remove (deactivate) a team member.
    """
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Prevent deleting self
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
        
    user.is_active = False # Soft delete
    await user.save()
    return {"message": "Team member deactivated"}

# --- Task Assignment ---

@router.post("/{member_id}/tasks", response_model=StaffTask)
async def assign_task(
    member_id: UUID,
    task_in: Dict[str, Any] = Body(...),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Assign a task to a team member.
    """
    user = await User.get(member_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    task = StaffTask(
        assigned_to=member_id,
        assigned_by=current_user.id,
        **task_in,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    await task.save()
    return task

@router.get("/{member_id}/tasks", response_model=List[StaffTask])
async def view_assigned_tasks(
    member_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    View tasks assigned to a team member.
    """
    tasks = await StaffTask.find({"assigned_to": member_id}).to_list()
    tasks = await StaffTask.find({"assigned_to": member_id}).to_list()
    return tasks

# --- Data Sharing ---

@router.post("/{member_id}/share-client", response_model=SharedClient)
async def share_client_with_member(
    member_id: UUID,
    share_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Share a client (developer) with a team member.
    """
    user = await User.get(member_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    shared = SharedClient(
        member_id=member_id,
        shared_by=current_user.id,
        **share_data,
        created_at=datetime.utcnow()
    )
    await shared.insert()
    return shared

@router.get("/{member_id}/shared-clients", response_model=List[SharedClient])
async def get_shared_clients(
    member_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get list of clients shared with this team member.
    """
    shared = await SharedClient.find({"member_id": member_id}).to_list()
    return shared
