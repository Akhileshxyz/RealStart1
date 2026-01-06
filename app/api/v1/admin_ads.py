from typing import Any, List, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User
from app.models.ad import Ad, AdType
from app.schemas.ad import AdCreate, AdUpdate, AdResponse
from datetime import datetime

router = APIRouter()

@router.get("/internal", response_model=List[AdResponse])
async def list_internal_ads(
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    List all internal ad campaigns.
    """
    return await Ad.find({"ad_type": AdType.INTERNAL}).to_list()

@router.post("/internal", response_model=AdResponse)
async def create_internal_ad(
    ad_in: AdCreate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Create a new internal ad campaign.
    """
    ad = Ad(
        **ad_in.model_dump(),
        ad_type=AdType.INTERNAL,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    await ad.save()
    return ad

@router.put("/internal/{ad_id}", response_model=AdResponse)
async def update_internal_ad(
    ad_id: UUID,
    ad_in: AdUpdate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update an internal ad campaign.
    """
    ad = await Ad.get(ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    update_data = ad_in.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    await ad.set(update_data)
    return ad

@router.delete("/internal/{ad_id}")
async def delete_ad(
    ad_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Delete (soft delete logic could be here, or hard delete) an ad.
    """
    ad = await Ad.get(ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    await ad.delete()
    return {"message": "Ad deleted successfully"}

# External Ads Integrations (Placeholders)
@router.get("/meta", response_model=Dict[str, Any])
async def get_meta_ads_performance(
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get Meta (Facebook/Instagram) ads performance.
    Placeholder for actual API integration.
    """
    return {
        "status": "connected",
        "campaigns": [
            {"name": "Summer Sale", "reach": 15000, "impressions": 45000, "spend": 500.0}
        ]
    }

@router.get("/google", response_model=Dict[str, Any])
async def get_google_ads_performance(
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get Google Ads performance.
    Placeholder for actual API integration.
    """
    return {
        "status": "connected",
        "campaigns": [
            {"name": "Brand Search", "clicks": 1200, "impressions": 20000, "spend": 350.0}
        ]
    }
