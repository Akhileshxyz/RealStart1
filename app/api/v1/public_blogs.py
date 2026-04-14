from typing import Any, List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from app.models.blog import Blog
from app.schemas.blog import (
    PublicBlogListItem,
    PublicBlogDetail,
    PaginatedBlogResponse,
    PaginatedBlogData,
    DetailBlogResponse,
    AuthorInfo,
    SEOInfo
)
import math

router = APIRouter()

def _map_blog_to_list_item(blog: Blog) -> PublicBlogListItem:
    return PublicBlogListItem(
        id=str(blog.id),
        slug=blog.slug,
        title=blog.title,
        desc=blog.description,
        tags=blog.tags if blog.tags else ([blog.tag] if blog.tag else []),
        date=blog.published_at.strftime("%d %b %Y") if blog.published_at else blog.created_at.strftime("%d %b %Y"),
        image=blog.image_url
    )

@router.get("/", response_model=PaginatedBlogResponse)
async def list_public_blogs(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None)
) -> Any:
    """
    List published blogs with pagination.
    """
    queryFilter = {Blog.is_published: True}
    if category:
        queryFilter[Blog.category] = category
    if tag:
        queryFilter[Blog.tag] = tag
    
    # Beanie query
    query = Blog.find(queryFilter)
    
    total = await query.count()
    last_page = math.ceil(total / per_page) if total > 0 else 1
    
    skip = (page - 1) * per_page
    blogs = await query.sort(-Blog.published_at).skip(skip).limit(per_page).to_list()
    
    items = [_map_blog_to_list_item(b) for b in blogs]
    
    return PaginatedBlogResponse(
        status="success",
        data=PaginatedBlogData(
            current_page=page,
            last_page=last_page,
            per_page=per_page,
            total=total,
            items=items
        )
    )

@router.get("/{slug}", response_model=DetailBlogResponse)
async def get_public_blog(slug: str) -> Any:
    """
    Get blog detail by slug.
    """
    blog = await Blog.find_one(Blog.slug == slug, Blog.is_published == True)
    if not blog:
         # Try by ID just in case
         try:
             blog_id = UUID(slug)
             blog = await Blog.find_one(Blog.id == blog_id, Blog.is_published == True)
         except ValueError:
             pass

    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    
    # Related posts logic: same category, excluding current one
    related_blogs = await Blog.find(
        Blog.category == blog.category,
        Blog.id != blog.id,
        Blog.is_published == True
    ).sort(-Blog.published_at).limit(3).to_list()
    
    related_items = [_map_blog_to_list_item(b) for b in related_blogs]
    
    detail = PublicBlogDetail(
        id=str(blog.id),
        slug=blog.slug,
        title=blog.title,
        subtitle=blog.subtitle,
        content_html=blog.content,
        tags=blog.tags if blog.tags else ([blog.tag] if blog.tag else []),
        date=blog.published_at.strftime("%d %b %Y") if blog.published_at else blog.created_at.strftime("%d %b %Y"),
        image=blog.image_url,
        author=AuthorInfo(
            name=blog.author_name,
            avatar=blog.author_avatar_url,
            role=blog.author_role or "UI/UX Designer"
        ),
        seo=SEOInfo(
            title=blog.seo.get("title") if blog.seo else None,
            description=blog.seo.get("description") if blog.seo else None,
            keywords=blog.seo.get("keywords") if blog.seo else []
        ),
        related_posts=related_items
    )
    
    return DetailBlogResponse(
        status="success",
        data=detail
    )
