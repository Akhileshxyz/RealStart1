from typing import Any, List, Optional
from uuid import UUID
from datetime import datetime
import json
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from app.api import deps
from app.models.user import User
from app.models.city import City
from app.schemas.city import CityCreate, CityUpdate, CityResponse
from app.core.config import settings
from pathlib import Path
import shutil

router = APIRouter()

_ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

def save_upload(file: UploadFile, sub_dir: str, filename_prefix: str = "") -> str:
    upload_root = Path(settings.UPLOAD_DIR)
    dest_dir = upload_root / sub_dir
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    ext = Path(file.filename).suffix or (".jpg" if "image" in (file.content_type or "") else ".pdf")
    filename = f"{filename_prefix}{datetime.utcnow().timestamp()}{ext}"
    dest_path = dest_dir / filename
    
    try:
        with dest_path.open("wb") as out:
            shutil.copyfileobj(file.file, out)
    finally:
        file.file.close()
    
    return f"/uploads/{sub_dir}/{filename}"


@router.get("/", response_model=List[CityResponse])
async def list_cities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=5000),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """List all cities."""
    cities = await City.find_all().skip(skip).limit(limit).to_list()
    return cities

@router.post("/", response_model=CityResponse)
async def create_city(
    data: str = Form(...), # JSON string of CityCreate
    files: List[UploadFile] = File(None),
    city_report: UploadFile = File(None),
    city_gif: UploadFile = File(None),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Create a new city with optional file uploads in one request."""
    try:
        city_dict = json.loads(data)
        city_in = CityCreate(**city_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON data: {str(e)}")

    # Uniqueness check
    if await City.find_one(City.name == city_in.name):
        raise HTTPException(status_code=400, detail="City name already exists")
    if await City.find_one(City.slug == city_in.slug):
        raise HTTPException(status_code=400, detail="City slug already exists")

    city = City(**city_in.model_dump())
    
    # Handle Image Uploads
    if files:
        for file in files:
            if file.content_type in _ALLOWED_IMAGE_TYPES:
                url = save_upload(file, f"cities/{city.id}")
                city.images.append(url)

    # Handle Report PDF Upload
    if city_report and city_report.filename:
        if city_report.filename.lower().endswith(".pdf"):
            url = save_upload(city_report, f"cities/{city.id}/reports", "report_")
            city.city_report_pdf = url

    # Handle GIF Upload
    if city_gif and city_gif.filename:
        if city_gif.filename.lower().endswith(".gif") or city_gif.content_type == "image/gif":
            url = save_upload(city_gif, f"cities/{city.id}", "animation_")
            city.city_gif = url

    await city.insert()
    return city


@router.get("/{city_id}", response_model=CityResponse)
async def get_city(
    city_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Get city details."""
    city = await City.get(city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city

@router.put("/{city_id}", response_model=CityResponse)
async def update_city(
    city_id: UUID,
    data: str = Form(...), # JSON string of CityUpdate
    files: List[UploadFile] = File(None),
    city_report: UploadFile = File(None),
    city_gif: UploadFile = File(None),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Update city details and handle file additions/replacements."""
    city = await City.get(city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    try:
        update_dict = json.loads(data)
        city_in = CityUpdate(**update_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON data: {str(e)}")

    update_data = city_in.model_dump(exclude_unset=True)
    
    # Validation
    if "slug" in update_data and update_data["slug"] != city.slug:
        if await City.find_one(City.slug == update_data["slug"]):
            raise HTTPException(status_code=400, detail="City slug already exists")
    if "name" in update_data and update_data["name"] != city.name:
        if await City.find_one(City.name == update_data["name"]):
            raise HTTPException(status_code=400, detail="City name already exists")

    # Update fields from JSON
    for key, value in update_data.items():
        setattr(city, key, value)

    # Handle New Image Uploads (Appended to existing or replaced if you sent a new list in 'data')
    if files:
        for file in files:
            if file.content_type in _ALLOWED_IMAGE_TYPES:
                url = save_upload(file, f"cities/{city.id}")
                city.images.append(url)

    # Handle New Report PDF Upload
    if city_report and city_report.filename:
        if city_report.filename.lower().endswith(".pdf"):
            url = save_upload(city_report, f"cities/{city.id}/reports", "report_")
            city.city_report_pdf = url

    # Handle New GIF Upload
    if city_gif and city_gif.filename:
        if city_gif.filename.lower().endswith(".gif") or city_gif.content_type == "image/gif":
            url = save_upload(city_gif, f"cities/{city.id}", "animation_")
            city.city_gif = url

    city.updated_at = datetime.utcnow()
    await city.save()
    return city


@router.delete("/{city_id}")
async def delete_city(
    city_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Delete a city."""
    city = await City.get(city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    await city.delete()
    return {"message": "City deleted successfully"}
