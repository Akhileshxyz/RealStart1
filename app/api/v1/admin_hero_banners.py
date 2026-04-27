from typing import Any, List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile, Form
import shutil
import uuid
from pathlib import Path
import json

from app.api import deps
from app.models.user import User
from app.models.hero_banner import HeroBanner
from app.schemas.hero_banner import HeroBannerCreate, HeroBannerUpdate, HeroBannerResponse
from app.core.config import settings

router = APIRouter()

async def _save_banner_image(file: UploadFile, type: str = "web") -> str:
    """Save an uploaded banner image and return its relative URL."""
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Allowed: .jpg, .jpeg, .png, .webp")
    
    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    upload_dir = Path(settings.UPLOAD_DIR) / "banners"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    unique_filename = f"{type}_{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_filename
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")
    
    return f"/uploads/banners/{unique_filename}"

@router.get("/", response_model=List[HeroBannerResponse])
async def list_banners_admin(
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """List all hero banners for admin."""
    return await HeroBanner.find_all().sort(HeroBanner.order).to_list()

@router.post("/", response_model=HeroBannerResponse, status_code=status.HTTP_201_CREATED)
async def create_banner(
    data: str = Form(..., description="JSON string of banner data"),
    web_image: UploadFile = File(...),
    mobile_image: Optional[UploadFile] = File(None),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Create a new hero banner."""
    try:
        banner_in = HeroBannerCreate.model_validate(json.loads(data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON data: {str(e)}")

    payload = banner_in.model_dump()
    
    # Handle Web Image
    payload["image_url"] = await _save_banner_image(web_image, "web")
    
    # Handle Mobile Image
    if mobile_image:
        payload["mobile_image_url"] = await _save_banner_image(mobile_image, "mobile")
    else:
        # Fallback to web image if mobile not provided
        payload["mobile_image_url"] = payload["image_url"]

    banner = HeroBanner(**payload)
    await banner.insert()
    return banner

@router.patch("/{banner_id}", response_model=HeroBannerResponse)
async def update_banner(
    banner_id: UUID,
    data: str = Form(..., description="JSON string of update data"),
    web_image: Optional[UploadFile] = File(None),
    mobile_image: Optional[UploadFile] = File(None),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Update an existing hero banner."""
    banner = await HeroBanner.get(banner_id)
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")

    try:
        banner_in = HeroBannerUpdate.model_validate(json.loads(data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON data: {str(e)}")

    update_data = banner_in.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    if web_image:
        update_data["image_url"] = await _save_banner_image(web_image, "web")
    
    if mobile_image:
        update_data["mobile_image_url"] = await _save_banner_image(mobile_image, "mobile")

    await banner.set(update_data)
    return await HeroBanner.get(banner_id)

@router.delete("/{banner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_banner(
    banner_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> None:
    """Delete a hero banner."""
    banner = await HeroBanner.get(banner_id)
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    await banner.delete()
    return None
