from datetime import datetime
from uuid import UUID
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field

class ReelBase(BaseModel):
    title: str
    description: Optional[Any] = None
    place: Optional[Any] = None
    video_url: str

class ReelCreate(ReelBase):
    pass

class ReelUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    place: Optional[str] = None

class ReelResponse(ReelBase):
    id: UUID
    uploaded_by: UUID
    likes_count: int
    comments_count: int
    status: str = "READY"
    processing_error: Optional[str] = None
    views_count: int = 0
    shares_count: int = 0
    is_active: bool = True
    landmark_id: Optional[UUID] = None
    landmark_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaginatedReelResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: List[ReelResponse]

class CommentCreate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: UUID
    reel_id: UUID
    user_id: UUID
    user_name: Optional[str] = None
    user_photo: Optional[str] = None
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReelListResponse(BaseModel):
    status: str = "success"
    results: int
    data: List[ReelResponse]

class CommentListResponse(BaseModel):
    status: str = "success"
    results: int
    data: List[CommentResponse]

class LikeResponse(BaseModel):
    status: str = "success"
    liked: bool
    likes_count: int

class SaveResponse(BaseModel):
    status: str = "success"
    saved: bool
