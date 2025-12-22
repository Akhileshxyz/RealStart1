from typing import Any, List, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api import deps
from app.models.user import User
from app.models.ad import Ad, AdType
from datetime import datetime

router = APIRouter()

@router.get("/internal", response_model=List[Ad])
async def list_internal_ads(
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    List all internal ad campaigns.
    """
    return await Ad.find({"ad_type": AdType.INTERNAL}).to_list()

@router.post("/internal", response_model=Ad)
async def create_internal_ad(
    ad_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Create a new internal ad campaign.
    """
    # Simply mapping dict to model for MVP.
    # In production use Pydantic schemas.
    ad = Ad(
        **ad_data,
        ad_type=AdType.INTERNAL,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    await ad.save()
    return ad

@router.put("/internal/{ad_id}", response_model=Ad)
async def update_internal_ad(
    ad_id: UUID,
    ad_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update an internal ad campaign.
    """
    ad = await Ad.get(ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    # Update fields
    for k, v in ad_data.items():
        if hasattr(ad, k):
            setattr(ad, k, v)
            
    ad.updated_at = datetime.utcnow()
    await ad.save()
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
