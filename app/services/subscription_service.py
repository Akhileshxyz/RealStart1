from datetime import datetime
from uuid import UUID
from typing import Optional, Any
from fastapi import HTTPException
from app.models.subscription import DeveloperSubscription, SubscriptionPlan, SubscriptionStatus
from app.models.project import Project, ProjectStatus
from app.models.team import DeveloperTeamMember

class SubscriptionService:
    DEFAULT_LIMITS = {
        "max_projects": 1,
        "max_team_members": 0,
        "can_view_leads": False
    }

    @staticmethod
    async def get_active_subscription(developer_id: UUID) -> Optional[DeveloperSubscription]:
        return await DeveloperSubscription.find(
            DeveloperSubscription.developer_id == developer_id,
            DeveloperSubscription.status == SubscriptionStatus.ACTIVE,
            DeveloperSubscription.end_date > datetime.utcnow()
        ).sort("-end_date").first_or_none()

    @staticmethod
    async def get_current_limits(developer_id: UUID) -> dict:
        sub = await SubscriptionService.get_active_subscription(developer_id)
        if not sub:
            return SubscriptionService.DEFAULT_LIMITS
            
        plan = await SubscriptionPlan.get(sub.plan_id)
        if not plan:
            return SubscriptionService.DEFAULT_LIMITS
            
        # Merge default with plan features (plan overrides)
        return {**SubscriptionService.DEFAULT_LIMITS, **plan.features}

    @staticmethod
    async def check_project_limit(developer_id: UUID):
        """
        Check if developer can create a new project.
        """
        limits = await SubscriptionService.get_current_limits(developer_id)
        max_projects = limits.get("max_projects", 1)
        
        # Count active projects (excluding deleted/rejected?)
        # Usually Rejected counts until deleted to prevent spam? Or only Pending/Approved?
        # Let's count Pending + Approved + Draft.
        count = await Project.find(
            Project.developer_id == developer_id,
            Project.status != ProjectStatus.DELETED,
            Project.status != ProjectStatus.REJECTED
        ).count()
        
        if count >= max_projects:
             raise HTTPException(
                 status_code=403, 
                 detail=f"Project limit reached ({count}/{max_projects}). Please upgrade your plan."
             )

    @staticmethod
    async def check_team_limit(developer_id: UUID):
        """
        Check if developer can add a new team member.
        """
        limits = await SubscriptionService.get_current_limits(developer_id)
        max_members = limits.get("max_team_members", 0)
        
        count = await DeveloperTeamMember.find(
            DeveloperTeamMember.developer_id == developer_id,
            DeveloperTeamMember.is_active == True
        ).count()
        
        if count >= max_members:
             raise HTTPException(
                 status_code=403, 
                 detail=f"Team member limit reached ({count}/{max_members}). Please upgrade your plan."
             )
