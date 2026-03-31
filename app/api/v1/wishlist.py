from typing import Any, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api import deps
from app.models.user import User
from app.models.lead import ProjectLead
from app.models.project import Project
from app.schemas.wishlist import (
    WishlistToggleRequest, 
    WishlistToggleResponse, 
    WishlistResponse, 
    WishlistItem
)

router = APIRouter()

@router.post("/toggle", response_model=WishlistToggleResponse)
async def toggle_wishlist_item(
    payload: WishlistToggleRequest,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Toggle a property/project in the user's wishlist.
    """
    # Verify the project exists
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

@router.get("/", response_model=WishlistResponse)
async def list_wishlist_items(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    List all projects in the user's wishlist with basic project data.
    """
    skip = (page - 1) * size
    
    # Fetch wishlisted leads
    leads = await ProjectLead.find(
        ProjectLead.user_id == current_user.id,
        ProjectLead.is_wishlisted == True
    ).sort(-ProjectLead.wishlisted_at).skip(skip).limit(size).to_list()

    wishlist_data = []
    for lead in leads:
        project = await Project.get(lead.project_id)
        if project:
            # Map project data to WishlistItem
            price_sqft = None
            if project.min_price and project.total_area_sqft and project.total_area_sqft > 0:
                price_sqft = project.min_price / project.total_area_sqft
            
            image_url = project.gallery_images[0] if project.gallery_images else None
            
            wishlist_data.append(WishlistItem(
                id=project.id,
                name=project.name,
                location=project.city,
                distance="1.4 km", # Placeholder as per request
                price_sqft=price_sqft,
                image_url=image_url,
                added_at=lead.wishlisted_at or lead.created_at
            ))

    return {
        "status": "success",
        "data": wishlist_data
    }

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_wishlist(
    current_user: User = Depends(deps.get_current_user)
) -> None:
    """
    Clear all items from the user's wishlist.
    """
    await ProjectLead.find(
        ProjectLead.user_id == current_user.id,
        ProjectLead.is_wishlisted == True
    ).update({"$set": {"is_wishlisted": False, "wishlisted_at": None}})
    
    return None
