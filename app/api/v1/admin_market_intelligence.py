from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.models.market_intelligence import MarketIntelligence
from app.schemas.market_intelligence import (
    MarketIntelligenceCreate, 
    MarketIntelligenceUpdate, 
    MarketIntelligenceResponse
)
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=MarketIntelligenceResponse)
async def create_market_intelligence(
    intelligence_in: MarketIntelligenceCreate,
    current_user: Any = Depends(deps.get_current_active_admin)
) -> Any:
    """
    Create or update market intelligence for a locality.
    If intelligence already exists for the landmark_id, it updates it.
    """
    existing = await MarketIntelligence.find_one(
        MarketIntelligence.landmark_id == intelligence_in.landmark_id
    )
    
    if existing:
        # Update existing
        update_data = intelligence_in.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        await existing.update({"$set": update_data})
        return await MarketIntelligence.get(existing.id)
    
    # Create new
    intelligence = MarketIntelligence(**intelligence_in.model_dump())
    await intelligence.insert()
    return intelligence

@router.get("/{landmark_id}", response_model=MarketIntelligenceResponse)
async def get_market_intelligence_admin(
    landmark_id: UUID,
    current_user: Any = Depends(deps.get_current_active_admin)
) -> Any:
    """
    Get market intelligence for a locality (Admin view).
    """
    intelligence = await MarketIntelligence.find_one(
        MarketIntelligence.landmark_id == landmark_id
    )
    if not intelligence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Market intelligence not found for this landmark"
        )
    return intelligence

@router.put("/{landmark_id}", response_model=MarketIntelligenceResponse)
async def update_market_intelligence(
    landmark_id: UUID,
    intelligence_in: MarketIntelligenceUpdate,
    current_user: Any = Depends(deps.get_current_active_admin)
) -> Any:
    """
    Update market intelligence for a locality.
    """
    intelligence = await MarketIntelligence.find_one(
        MarketIntelligence.landmark_id == landmark_id
    )
    if not intelligence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Market intelligence not found"
        )
    
    update_data = intelligence_in.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    await intelligence.update({"$set": update_data})
    return await MarketIntelligence.get(intelligence.id)

@router.delete("/{landmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_market_intelligence(
    landmark_id: UUID,
    current_user: Any = Depends(deps.get_current_active_admin)
) -> None:
    """
    Delete market intelligence for a locality.
    """
    intelligence = await MarketIntelligence.find_one(
        MarketIntelligence.landmark_id == landmark_id
    )
    if not intelligence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Market intelligence not found"
        )
    await intelligence.delete()
    return None
