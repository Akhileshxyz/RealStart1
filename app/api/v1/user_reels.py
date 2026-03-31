from typing import Any, List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api import deps
from app.models.user import User
from app.models.reel import Reel, ReelLike, ReelComment, ReelSave
from app.schemas.reel import (
    ReelResponse, 
    ReelListResponse, 
    CommentCreate, 
    CommentResponse, 
    CommentListResponse,
    LikeResponse,
    SaveResponse
)

router = APIRouter()

@router.get("/", response_model=ReelListResponse)
async def list_reels(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    current_user: Optional[User] = Depends(deps.get_current_user_optional)
) -> Any:
    """
    Get reels feed (paginated, latest first).
    """
    skip = (page - 1) * size
    reels = await Reel.find().sort("-created_at").skip(skip).limit(size).to_list()
    
    reel_responses = []
    for reel in reels:
        resp = ReelResponse.model_validate(reel.model_dump())
        if current_user:
            # Check interaction states
            is_liked = await ReelLike.find_one(ReelLike.reel_id == reel.id, ReelLike.user_id == current_user.id)
            is_saved = await ReelSave.find_one(ReelSave.reel_id == reel.id, ReelSave.user_id == current_user.id)
            resp.is_liked = bool(is_liked)
            resp.is_saved = bool(is_saved)
        reel_responses.append(resp)

    return {
        "status": "success",
        "results": len(reel_responses),
        "data": reel_responses
    }

@router.get("/{reel_id}", response_model=ReelResponse)
async def get_reel(
    reel_id: UUID,
    current_user: Optional[User] = Depends(deps.get_current_user_optional)
) -> Any:
    """
    Get a single reel by ID.
    """
    reel = await Reel.get(reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
        
    resp = ReelResponse.model_validate(reel.model_dump())
    if current_user:
        is_liked = await ReelLike.find_one(ReelLike.reel_id == reel.id, ReelLike.user_id == current_user.id)
        is_saved = await ReelSave.find_one(ReelSave.reel_id == reel.id, ReelSave.user_id == current_user.id)
        resp.is_liked = bool(is_liked)
        resp.is_saved = bool(is_saved)
        
    return resp

@router.post("/{reel_id}/like", response_model=LikeResponse)
async def toggle_like(
    reel_id: UUID,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Toggle like/unlike for a reel.
    """
    reel = await Reel.get(reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
        
    existing_like = await ReelLike.find_one(ReelLike.reel_id == reel_id, ReelLike.user_id == current_user.id)
    
    if existing_like:
        await existing_like.delete()
        reel.likes_count = max(0, reel.likes_count - 1)
        await reel.save()
        return {"liked": False, "likes_count": reel.likes_count}
    else:
        new_like = ReelLike(reel_id=reel_id, user_id=current_user.id)
        await new_like.insert()
        reel.likes_count += 1
        await reel.save()
        return {"liked": True, "likes_count": reel.likes_count}

@router.get("/{reel_id}/likes/count")
async def get_likes_count(reel_id: UUID) -> Any:
    """
    Get total like count for a reel.
    """
    reel = await Reel.get(reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
    return {"reel_id": reel_id, "likes_count": reel.likes_count}

@router.post("/{reel_id}/comment", response_model=CommentResponse)
async def add_comment(
    reel_id: UUID,
    comment_in: CommentCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Add a comment to a reel.
    """
    reel = await Reel.get(reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
        
    comment = ReelComment(
        reel_id=reel_id,
        user_id=current_user.id,
        content=comment_in.content
    )
    await comment.insert()
    
    reel.comments_count += 1
    await reel.save()
    
    # Enrich with user info for response
    resp = CommentResponse.model_validate(comment.model_dump())
    resp.user_name = current_user.full_name
    resp.user_photo = current_user.photo_url
    return resp

@router.get("/{reel_id}/comments", response_model=CommentListResponse)
async def list_comments(
    reel_id: UUID,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
) -> Any:
    """
    Get paginated comments for a reel.
    """
    skip = (page - 1) * size
    comments = await ReelComment.find(ReelComment.reel_id == reel_id).sort("-created_at").skip(skip).limit(size).to_list()
    
    comment_responses = []
    for comm in comments:
        user = await User.get(comm.user_id)
        resp = CommentResponse.model_validate(comm.model_dump())
        if user:
            resp.user_name = user.full_name
            resp.user_photo = user.photo_url
        comment_responses.append(resp)
        
    return {
        "status": "success",
        "results": len(comment_responses),
        "data": comment_responses
    }

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    current_user: User = Depends(deps.get_current_user)
) -> None:
    """
    Delete own comment.
    """
    comment = await ReelComment.get(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
        
    if comment.user_id != current_user.id:
         raise HTTPException(status_code=403, detail="You can only delete your own comments")
         
    # Update reel comment count
    reel = await Reel.get(comment.reel_id)
    if reel:
        reel.comments_count = max(0, reel.comments_count - 1)
        await reel.save()
        
    await comment.delete()
    return None

@router.post("/{reel_id}/save", response_model=SaveResponse)
async def toggle_save(
    reel_id: UUID,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Toggle bookmark/save for a reel.
    """
    reel = await Reel.get(reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
        
    existing_save = await ReelSave.find_one(ReelSave.reel_id == reel_id, ReelSave.user_id == current_user.id)
    
    if existing_save:
        await existing_save.delete()
        return {"saved": False}
    else:
        new_save = ReelSave(reel_id=reel_id, user_id=current_user.id)
        await new_save.insert()
        return {"saved": True}

@router.get("/users/me/saved-reels", response_model=ReelListResponse)
async def get_saved_reels(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    List user's saved reels.
    """
    skip = (page - 1) * size
    saves = await ReelSave.find(ReelSave.user_id == current_user.id).sort("-created_at").skip(skip).limit(size).to_list()
    
    reel_ids = [s.reel_id for s in saves]
    reels = await Reel.find({"_id": {"$in": reel_ids}}).to_list()
    
    # Maintain order of saves
    reel_map = {r.id: r for r in reels}
    ordered_reels = []
    for s in saves:
        if s.reel_id in reel_map:
            reel = reel_map[s.reel_id]
            resp = ReelResponse.model_validate(reel.model_dump())
            # For saved reels, is_saved is true by definition
            # Let's check liking status too
            is_liked = await ReelLike.find_one(ReelLike.reel_id == reel.id, ReelLike.user_id == current_user.id)
            resp.is_liked = bool(is_liked)
            resp.is_saved = True
            ordered_reels.append(resp)

    return {
        "status": "success",
        "results": len(ordered_reels),
        "data": ordered_reels
    }
