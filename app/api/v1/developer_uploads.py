from typing import Any
from enum import Enum
from datetime import datetime
from pathlib import Path
import shutil
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.api import deps
from app.models.user import User, UserRole
from app.core.config import settings
from pydantic import BaseModel

router = APIRouter()

class DocumentType(str, Enum):
    RERA_APPROVAL = "RERA_APPROVAL"
    RTC = "RTC"
    DC_CONVERSION = "DC_CONVERSION"
    LAYOUT_APPROVAL = "LAYOUT_APPROVAL"
    PROJECT_IMAGE = "PROJECT_IMAGE"
    BROCHURE = "BROCHURE"
    OTHER = "OTHER"

class FileUploadResponse(BaseModel):
    file_url: str
    file_name: str
    file_type: str
    document_type: str
    uploaded_at: datetime

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    # Documents
    ".pdf": "application/pdf",
    # Images
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".heic": "image/heic",
    ".heif": "image/heif",
}

def validate_file(file: UploadFile) -> None:
    """Validate file type and size"""
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS.keys())}"
        )

    # Check content type
    if file.content_type and not any(
        file.content_type.startswith(ct.split('/')[0])
        for ct in ALLOWED_EXTENSIONS.values()
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid content type: {file.content_type}"
        )

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Upload a file (document or image) for a project.

    Supported file types:
    - Documents: PDF
    - Images: JPG, JPEG, PNG, HEIC, HEIF

    Document types:
    - RERA_APPROVAL: RERA approval certificate
    - RTC: Record of Rights, Tenancy and Crops
    - DC_CONVERSION: DC conversion approval
    - LAYOUT_APPROVAL: Layout plan approval
    - PROJECT_IMAGE: Project photos/images
    - BROCHURE: Project brochure
    - OTHER: Other documents

    Max file size: 10MB
    """
    # Verify role
    if current_user.role not in [UserRole.DEVELOPER, UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to upload files")

    # Validate file
    validate_file(file)

    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectory for developer
    developer_dir = upload_dir / str(current_user.id)
    developer_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectory for document type
    doc_type_dir = developer_dir / document_type.value.lower()
    doc_type_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = doc_type_dir / unique_filename

    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()  # Get position (file size)
    file.file.seek(0)  # Reset to beginning

    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Save file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    finally:
        file.file.close()

    # Generate file URL (relative path)
    file_url = f"/uploads/{current_user.id}/{document_type.value.lower()}/{unique_filename}"

    return FileUploadResponse(
        file_url=file_url,
        file_name=file.filename,
        file_type=file_ext,
        document_type=document_type.value,
        uploaded_at=datetime.utcnow()
    )

@router.delete("/upload")
async def delete_file(
    file_url: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete an uploaded file.
    Only the developer who uploaded the file can delete it.
    """
    # Verify role
    if current_user.role not in [UserRole.DEVELOPER, UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to delete files")

    # Extract file path from URL
    if not file_url.startswith("/uploads/"):
        raise HTTPException(status_code=400, detail="Invalid file URL")

    # Ensure the file belongs to the current user (security check)
    expected_prefix = f"/uploads/{current_user.id}/"
    if not file_url.startswith(expected_prefix) and current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this file")

    # Construct file path
    file_path = Path(settings.UPLOAD_DIR) / file_url.replace("/uploads/", "")

    # Check if file exists
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Delete file
    try:
        file_path.unlink()
        return {"message": "File deleted successfully", "file_url": file_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
