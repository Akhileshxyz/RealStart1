"""
Admin Blogs API
===============
Full CRUD for blog posts, plus publish/unpublish toggle.
All endpoints require admin authentication.
"""
from typing import Any, List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile, Form
import shutil
import uuid
from pathlib import Path

from app.api import deps
from app.models.user import User
from app.models.blog import Blog
from app.schemas.blog import BlogCreate, BlogUpdate, BlogResponse, BlogDetailResponse
from app.core.redis_client import redis_client
from app.core.config import settings

router = APIRouter()


def _build_blog_response(blog: Blog) -> BlogDetailResponse:
    from app.schemas.blog import BlogTheme
    return BlogDetailResponse(
        id=blog.id,
        slug=blog.slug,
        title=blog.title,
        subtitle=blog.subtitle,
        description=blog.description,
        content=blog.content,
        category=blog.category,
        tag=blog.tag,
        tags=blog.tags or [],
        theme=BlogTheme(
            bg=blog.bg_color or "#1a2230",
            accent=blog.accent_color or "#94a3b8",
        ),
        image_url=blog.image_url,
        author_name=blog.author_name,
        author_avatar_url=blog.author_avatar_url,
        author_role=blog.author_role,
        seo=blog.seo or {},
        date_formatted=(blog.published_at or blog.created_at).strftime("%d/%m/%Y %I:%M %p"),
        is_published=blog.is_published,
        created_at=blog.created_at,
    )


async def _invalidate_blog_caches() -> None:
    """Clear all public blog cache entries after any mutation."""
    await redis_client.delete_pattern(redis_client.make_key("public", "blogs", "*"))


async def _save_blog_image(file: UploadFile) -> str:
    """Save an uploaded blog image and return its relative URL."""
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Allowed: .jpg, .jpeg, .png, .webp")
    
    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    upload_dir = Path(settings.UPLOAD_DIR) / "blogs"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_filename
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")
    
    return f"/uploads/blogs/{unique_filename}"


# ---------------------------------------------------------------------------
# LIST
# ---------------------------------------------------------------------------

@router.get("/", response_model=List[BlogDetailResponse])
async def list_blogs_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=5000),
    is_published: Optional[bool] = Query(None),
    category: Optional[str] = Query(None),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    List all blogs (published and draft).
    Supports filtering by published state or category.
    """
    query = Blog.find()
    if is_published is not None:
        query = query.find(Blog.is_published == is_published)
    if category:
        query = query.find(Blog.category == category)

    blogs = await query.sort(-Blog.created_at).skip(skip).limit(limit).to_list()
    return [_build_blog_response(b) for b in blogs]


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

@router.post("/", response_model=BlogDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_blog(
    data: str = Form(..., description="JSON string of blog data (matching BlogCreate schema)"),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Create a new blog post via Form Data.
    The 'data' field should contain the JSON string of blog attributes.
    Optional 'image' file upload.
    """
    try:
        import json
        blog_in = BlogCreate.model_validate(json.loads(data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON data: {str(e)}")

    payload = blog_in.model_dump()

    # Handle Image Upload
    if image:
        payload["image_url"] = await _save_blog_image(image)

    # Auto-set published_at if publishing now and not explicitly provided
    if payload.get("is_published") and not payload.get("published_at"):
        payload["published_at"] = datetime.utcnow()

    blog = Blog(**payload)
    await blog.insert()

    if blog.is_published:
        await _invalidate_blog_caches()

    return _build_blog_response(blog)


# ---------------------------------------------------------------------------
# GET ONE
# ---------------------------------------------------------------------------

@router.get("/{blog_id}", response_model=BlogDetailResponse)
async def get_blog_admin(
    blog_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Get a single blog post (admin view includes draft content)."""
    blog = await Blog.get(blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return _build_blog_response(blog)


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

@router.put("/{blog_id}", response_model=BlogDetailResponse)
async def update_blog(
    blog_id: UUID,
    data: str = Form(..., description="JSON string of update data (matching BlogUpdate schema)"),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update blog metadata or content via Form Data.
    """
    blog = await Blog.get(blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    try:
        import json
        blog_in = BlogUpdate.model_validate(json.loads(data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON data: {str(e)}")

    update_data = blog_in.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    # Handle conditional Image Upload
    if image:
        # Optionally delete old image if it exists and was a local upload
        if blog.image_url and blog.image_url.startswith("/uploads/blogs/"):
            old_path = Path(settings.UPLOAD_DIR) / "blogs" / Path(blog.image_url).name
            if old_path.exists():
                try:
                    old_path.unlink()
                except:
                    pass
        
        update_data["image_url"] = await _save_blog_image(image)

    # Auto-set published_at when first publishing
    if update_data.get("is_published") and not blog.published_at:
        update_data.setdefault("published_at", datetime.utcnow())

    await blog.set(update_data)
    await _invalidate_blog_caches()

    return _build_blog_response(await Blog.get(blog_id))


# ---------------------------------------------------------------------------
# PUBLISH / UNPUBLISH TOGGLE
# ---------------------------------------------------------------------------

@router.patch("/{blog_id}/publish", response_model=BlogDetailResponse)
async def toggle_publish(
    blog_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Toggle the `is_published` state of a blog post."""
    blog = await Blog.get(blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    new_state = not blog.is_published
    update = {
        "is_published": new_state,
        "updated_at": datetime.utcnow(),
    }
    if new_state and not blog.published_at:
        update["published_at"] = datetime.utcnow()

    await blog.set(update)
    await _invalidate_blog_caches()

    return _build_blog_response(await Blog.get(blog_id))


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog(
    blog_id: UUID,
    current_user: User = Depends(deps.get_current_active_admin),
) -> None:
    """Permanently delete a blog post."""
    blog = await Blog.get(blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    await blog.delete()
    await _invalidate_blog_caches()
    return None
