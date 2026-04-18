from typing import Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api import deps
from app.models.user import User
from app.models.lead import ProjectLead
from app.models.project import Project
from app.models.landmark import Landmark, LandmarkSave
from app.models.reel import Reel, ReelSave
from app.schemas.wishlist import (
    WishlistToggleRequest, 
    WishlistToggleResponse, 
    CombinedWishlistResponse,
    ProjectWishlistItem,
    ReelWishlistItem
)
from app.utils.media import public_image_url

router = APIRouter()

@router.post("/toggle", response_model=WishlistToggleResponse)
async def toggle_wishlist_item(
    payload: WishlistToggleRequest,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Toggle a property/project or landmark in the user's wishlist.
    """
    if payload.type == "landmark":
        # Toggle Landmark
        landmark = await Landmark.get(payload.property_id)
        if not landmark:
            raise HTTPException(status_code=404, detail="Landmark not found")
        
        existing = await LandmarkSave.find_one(
            LandmarkSave.landmark_id == payload.property_id,
            LandmarkSave.user_id == current_user.id
        )
        
        if existing:
            await existing.delete()
            action = "removed"
            message = "Landmark removed from wishlist"
        else:
            new_save = LandmarkSave(
                landmark_id=payload.property_id,
                user_id=current_user.id
            )
            await new_save.insert()
            action = "added"
            message = "Landmark added to wishlist"
            
        count = await LandmarkSave.find(LandmarkSave.user_id == current_user.id).count()
        return {
            "status": "success",
            "message": message,
            "action": action,
            "count": count
        }
    
    # Default to Project
    project = await Project.get(payload.property_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Find or create a Lead entry for this user and project
    lead = await ProjectLead.find_one(
        ProjectLead.user_id == current_user.id,
        ProjectLead.project_id == payload.property_id
    )

    if not lead:
        # Create new lead with wishlist status
        lead = ProjectLead(
            user_id=current_user.id,
            project_id=payload.property_id,
            is_wishlisted=True,
            wishlisted_at=datetime.utcnow(),
            is_anonymous=False
        )
        action = "added"
        message = "Property added to wishlist"
    else:
        # Toggle existing status
        lead.is_wishlisted = not lead.is_wishlisted
        if lead.is_wishlisted:
            lead.wishlisted_at = datetime.utcnow()
            action = "added"
            message = "Property added to wishlist"
        else:
            action = "removed"
            message = "Property removed from wishlist"
    
    await lead.save()

    # Get total count of wishlisted items for this user
    count = await ProjectLead.find(
        ProjectLead.user_id == current_user.id,
        ProjectLead.is_wishlisted == True
    ).count()

    return {
        "status": "success",
        "message": message,
        "action": action,
        "count": count
    }

@router.get("/", response_model=CombinedWishlistResponse)
async def list_wishlist_items(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    List all reels and projects in the user's wishlist.
    """
    # 1. Fetch Saved Projects (ProjectLead)
    leads = await ProjectLead.find(
        ProjectLead.user_id == current_user.id,
        ProjectLead.is_wishlisted == True
    ).sort("-wishlisted_at").to_list()
    
    projects_data = []
    for lead in leads:
        p = await Project.get(lead.project_id)
        if p:
            projects_data.append(ProjectWishlistItem(
                uuid=p.id,
                name=p.name,
                image=public_image_url(p.gallery_images[0] if p.gallery_images else None),
                slug=p.slug,
                description=p.description,
                is_liked=True
            ))

    # 2. Fetch Saved Reels
    reel_saves = await ReelSave.find(
        ReelSave.user_id == current_user.id
    ).sort("-created_at").to_list()
    
    reels_data = []
    for save in reel_saves:
        reel = await Reel.get(save.reel_id)
        if reel:
            reels_data.append(ReelWishlistItem(
                uuid=reel.id,
                title=reel.title,
                video_url=reel.video_url,
                thumbnail=None, # Reel model has no thumbnail yet
                is_liked=True
            ))

    return {
        "reels": reels_data,
        "projects": projects_data
    }

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_wishlist(
    current_user: User = Depends(deps.get_current_user)
) -> None:
    """
    Clear all items from the user's wishlist (Projects, Landmarks, and Reels).
    """
    # Clear Projects
    await ProjectLead.find(
        ProjectLead.user_id == current_user.id,
        ProjectLead.is_wishlisted == True
    ).update({"$set": {"is_wishlisted": False, "wishlisted_at": None}})
    
    # Clear Landmarks
    await LandmarkSave.find(LandmarkSave.user_id == current_user.id).delete()
    
    # Clear Reels
    await ReelSave.find(ReelSave.user_id == current_user.id).delete()
    
    return None
