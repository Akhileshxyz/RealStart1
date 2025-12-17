from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException
from app.models.user import User, UserRole
from app.models.team import DeveloperTeamMember

class PermissionService:
    @staticmethod
    async def has_permission(user: User, required_permission: str) -> bool:
        # 1. Super Admin and Admin have access to everything (context dependent, usually)
        # But for Developer resources, Admin is usually allowed.
        if user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            return True
            
        # 2. Developer (Owner) has all permissions for their own scope
        if user.role == UserRole.DEVELOPER:
            return True
            
        # 3. Team Members (Sales, Marketing, etc.)
        if user.role in [UserRole.SALES, UserRole.MARKETING, UserRole.MANAGER]:
            # Find the team membership
            # Optimally, user.developer_id should be set, but we might need to verify the record
            member = await DeveloperTeamMember.find_one(DeveloperTeamMember.user_id == user.id)
            if not member:
                return False
                
            if not member.is_active:
                return False
                
            return required_permission in member.permissions
            
        # Other roles (Buyer, Lawyer) usually don't have these permissions
        return False

    @staticmethod
    async def enforce(user: User, required_permission: str, developer_id_scope: Optional[UUID] = None):
        """
        Check permission and raise 403 if failed.
        Optionally check if the user belongs to the specific developer scope.
        """
        permitted = await PermissionService.has_permission(user, required_permission)
        if not permitted:
             raise HTTPException(status_code=403, detail=f"Missing permission: {required_permission}")
             
        # Scope Check
        if developer_id_scope:
            if user.role == UserRole.DEVELOPER:
                if user.id != developer_id_scope:
                    raise HTTPException(status_code=403, detail="Not authorized for this context")
            elif user.role in [UserRole.SALES, UserRole.MARKETING, UserRole.MANAGER]:
                 member = await DeveloperTeamMember.find_one(DeveloperTeamMember.user_id == user.id)
                 if not member or member.developer_id != developer_id_scope:
                      raise HTTPException(status_code=403, detail="Not authorized for this context")
