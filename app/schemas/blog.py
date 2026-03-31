from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class BlogTheme(BaseModel):
    bg: str = "#1a2230"
    accent: str = "#94a3b8"


class BlogCreate(BaseModel):
    title: str
    description: str
    content: Optional[str] = None
    category: str
    tag: Optional[str] = None
    bg_color: Optional[str] = None
    accent_color: Optional[str] = None
    image_url: Optional[str] = None
    author_name: Optional[str] = None
    author_avatar_url: Optional[str] = None
    is_published: bool = False
    published_at: Optional[datetime] = None


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tag: Optional[str] = None
    bg_color: Optional[str] = None
    accent_color: Optional[str] = None
    image_url: Optional[str] = None
    author_name: Optional[str] = None
    author_avatar_url: Optional[str] = None
    is_published: Optional[bool] = None
    published_at: Optional[datetime] = None


class BlogResponse(BaseModel):
    id: UUID
    title: str
    description: str
    category: str
    tag: Optional[str] = None
    # Composed theme object for frontend card rendering
    theme: BlogTheme = Field(default_factory=BlogTheme)
    image_url: Optional[str] = None
    author_name: Optional[str] = None
    author_avatar_url: Optional[str] = None
    date_formatted: str  # e.g. "08/04/2025 04:30 PM"
    is_published: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BlogDetailResponse(BlogResponse):
    content: Optional[str] = None
