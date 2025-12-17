from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User, UserRole
from app.models.team import DeveloperTeamMember
from app.schemas.team import TeamMemberInvite, TeamMemberUpdate, TeamMemberResponse
from app.core.security import get_password_hash

router = APIRouter()

@router.get("/", response_model=List[TeamMemberResponse])
async def list_team_members(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    List all team members for the current developer.
    """
    if current_user.role != UserRole.DEVELOPER:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    members = await DeveloperTeamMember.find(DeveloperTeamMember.developer_id == current_user.id).to_list()
    
    response = []
    for m in members:
        user = await User.get(m.user_id)
        resp = TeamMemberResponse(
            id=m.id,
            developer_id=m.developer_id,
            user_id=m.user_id,
            role=m.role,
            permissions=m.permissions,
            invited_at=m.invited_at,
            is_active=m.is_active,
            full_name=user.full_name if user else "Unknown",
            email=user.email if user else "Unknown"
        )
        response.append(resp)
        
    return response

@router.post("/invite", response_model=TeamMemberResponse)
async def invite_team_member(
    invite_in: TeamMemberInvite,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Invite a team member.
    If user exists, links them.
    If not, creates a new user account (Status: Buying/Marketing?) with basic details.
    """
    if current_user.role != UserRole.DEVELOPER:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if user exists
    user = await User.find_one(User.email == invite_in.email)
    if not user:
        # Create new user
        # Note: In a real app we'd trigger an email invite flow.
        # Here we creates a user with a placeholder password.
        user = User(
            email=invite_in.email,
            full_name=invite_in.email.split("@")[0],
            hashed_password=get_password_hash("TempPass123!"), # Explicit temp password
            role=UserRole.MARKETING if invite_in.role == "Marketing" else UserRole.SALES, 
            is_active=True
        )
        await user.insert()
    
    # Check if already in team
    existing = await DeveloperTeamMember.find_one(
        DeveloperTeamMember.developer_id == current_user.id,
        DeveloperTeamMember.user_id == user.id
    )
    if existing:
        raise HTTPException(status_code=400, detail="User already in team")
        
    member = DeveloperTeamMember(
        developer_id=current_user.id,
        user_id=user.id,
        role=invite_in.role,
        permissions=invite_in.permissions
    )
    await member.insert()
    
    return TeamMemberResponse(
        id=member.id,
        developer_id=member.developer_id,
        user_id=member.user_id,
        role=member.role,
        permissions=member.permissions,
        invited_at=member.invited_at,
        is_active=member.is_active,
        full_name=user.full_name,
        email=user.email
    )

@router.put("/{member_id}/permissions", response_model=TeamMemberResponse)
async def update_member_permissions(
    member_id: UUID,
    update_in: TeamMemberUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a team member's role or permissions.
    """
    if current_user.role != UserRole.DEVELOPER:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    member = await DeveloperTeamMember.get(member_id)
    if not member or member.developer_id != current_user.id:
        raise HTTPException(status_code=404, detail="Team member not found")
        
    if update_in.role:
        member.role = update_in.role
    if update_in.permissions is not None:
        member.permissions = update_in.permissions
        
    await member.save()
    
    user = await User.get(member.user_id)
    return TeamMemberResponse(
        id=member.id,
        developer_id=member.developer_id,
        user_id=member.user_id,
        role=member.role,
        permissions=member.permissions,
        invited_at=member.invited_at,
        is_active=member.is_active,
        full_name=user.full_name if user else "Unknown",
        email=user.email if user else "Unknown"
    )

@router.delete("/{member_id}")
async def remove_team_member(
    member_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Remove a team member.
    """
    if current_user.role != UserRole.DEVELOPER:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    member = await DeveloperTeamMember.get(member_id)
    if not member or member.developer_id != current_user.id:
        raise HTTPException(status_code=404, detail="Team member not found")
        
    await member.delete()
    return {"message": "Team member removed"}
