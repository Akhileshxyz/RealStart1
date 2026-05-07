from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Dict, Any
from beanie import Document
from pydantic import Field


class BlogTheme(Dict):
    """Optional visual theme overrides for the blog card."""
    pass


class Blog(Document):
    id: UUID = Field(default_factory=uuid4)
    slug: str

    title: str
    title_kn: Optional[str] = None
    subtitle: Optional[str] = None
    subtitle_kn: Optional[str] = None
    description: str  # Short excerpt / card summary
    description_kn: Optional[str] = None
    content: Optional[str] = None  # Full HTML/MD body (for detail page)
    content_kn: Optional[str] = None

    category: str  # e.g. "Commercial", "Residential", "Market Trends"
    tag: Optional[str] = None  # e.g. "Trending", "New", "Featured"
    tags: list[str] = Field(default_factory=list)

    # Visual overrides: {"bg": "#1a2230", "accent": "#94a3b8"}
    bg_color: Optional[str] = None
    accent_color: Optional[str] = None

    # Cover / thumbnail image
    image_url: Optional[str] = None

    # Author
    author_name: Optional[str] = None
    author_avatar_url: Optional[str] = None
    author_role: Optional[str] = "UI/UX Designer"

    # SEO Metadata
    seo: dict[str, Any] = Field(default_factory=dict)

    is_published: bool = False
    published_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "blogs"
        indexes = [
            "is_published",
            "category",
            "slug",
            "-published_at",
        ]
