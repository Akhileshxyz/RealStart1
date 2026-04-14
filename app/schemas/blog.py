from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class BlogTheme(BaseModel):
    bg: str = "#1a2230"
    accent: str = "#94a3b8"


class BlogCreate(BaseModel):
    title: str
    slug: str
    subtitle: Optional[str] = None
    description: str
    content: Optional[str] = None
    category: str
    tag: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    bg_color: Optional[str] = None
    accent_color: Optional[str] = None
    image_url: Optional[str] = None
    author_name: Optional[str] = None
    author_avatar_url: Optional[str] = None
    author_role: Optional[str] = "UI/UX Designer"
    seo: dict[str, Any] = Field(default_factory=dict)
    is_published: bool = False
    published_at: Optional[datetime] = None


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tag: Optional[str] = None
    tags: Optional[list[str]] = None
    bg_color: Optional[str] = None
    accent_color: Optional[str] = None
    image_url: Optional[str] = None
    author_name: Optional[str] = None
    author_avatar_url: Optional[str] = None
    author_role: Optional[str] = None
    seo: Optional[dict[str, Any]] = None
    is_published: Optional[bool] = None
    published_at: Optional[datetime] = None


class BlogResponse(BaseModel):
    id: UUID
    slug: str
    title: str
    subtitle: Optional[str] = None
    description: str
    category: str
    tag: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    theme: BlogTheme = Field(default_factory=BlogTheme)
    image_url: Optional[str] = None
    author_name: Optional[str] = None
    author_avatar_url: Optional[str] = None
    author_role: Optional[str] = None
    seo: dict[str, Any] = Field(default_factory=dict)
    date_formatted: str
    is_published: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BlogDetailResponse(BlogResponse):
    content: Optional[str] = None


# --- Public Facing API Schemas (Matching USER requested structure) ---

class AuthorInfo(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    role: Optional[str] = None


class SEOInfo(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)


class PublicBlogListItem(BaseModel):
    id: str
    slug: str
    title: str
    desc: str
    tags: list[str]
    date: str
    image: Optional[str] = None


class PublicBlogDetail(BaseModel):
    id: str
    slug: str
    title: str
    subtitle: Optional[str] = None
    content_html: Optional[str] = None
    tags: list[str]
    date: str
    image: Optional[str] = None
    author: AuthorInfo
    seo: SEOInfo
    related_posts: list[PublicBlogListItem] = Field(default_factory=list)


class PaginatedBlogData(BaseModel):
    current_page: int
    last_page: int
    per_page: int
    total: int
    items: list[PublicBlogListItem]


class PaginatedBlogResponse(BaseModel):
    status: str = "success"
    data: PaginatedBlogData


class DetailBlogResponse(BaseModel):
    status: str = "success"
    data: PublicBlogDetail
