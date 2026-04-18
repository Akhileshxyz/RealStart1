from typing import List, Optional, Any
from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.models.city import City
from app.models.landmark import Landmark
from app.models.project import Project, ProjectStatus
from app.models.lead import ProjectLead
from app.api import deps
from app.models.user import User
from app.utils.media import public_image_url
import re

router = APIRouter()

class SearchItem(BaseModel):
    uuid: UUID
    name: str
    image: Optional[str] = None
    slug: str
    description: Optional[str] = None
    is_liked: bool = False

class SearchResponse(BaseModel):
    cities: List[SearchItem]
    landmarks: List[SearchItem]
    projects: List[SearchItem]

class SearchRequest(BaseModel):
    query: str

@router.post("/", response_model=SearchResponse)
async def public_search(
    request: SearchRequest,
    current_user: Optional[User] = Depends(deps.get_current_user_optional)
) -> Any:
    """
    Search cities, landmarks, and projects by name/title.
    """
    query = request.query
    if not query or len(query) < 2:
        return {"cities": [], "landmarks": [], "projects": []}

    # Case-insensitive regex for search
    # We use regex with ^ for "starts with" or just containing
    # Let's use containing for better search experience as requested ("containing that query")
    regex_query = re.compile(f".*{re.escape(query)}.*", re.IGNORECASE)

    # 1. Search Cities
    cities = await City.find({
        "is_active": True,
        "$or": [
            {"name": regex_query},
            {"slug": regex_query}
        ]
    }).limit(10).to_list()
    
    found_city_ids = [c.id for c in cities]
    found_city_names = [c.name for c in cities]

    # 2. Search Landmarks: Direct name match OR belonging to a matched city
    landmarks = await Landmark.find({
        "$or": [
            {"name": regex_query},
            {"city": regex_query},
            {"city_id": {"$in": found_city_ids}},
            {"city": {"$in": found_city_names}}
        ]
    }).limit(20).to_list()

    # 3. Search Projects: Direct match OR belonging to a matched city
    projects = await Project.find({
        "status": ProjectStatus.APPROVED,
        "is_hidden": False,
        "is_active": True,
        "$or": [
            {"name": regex_query},
            {"city": regex_query},
            {"landmark": regex_query},
            {"city_id": {"$in": found_city_ids}},
            {"city": {"$in": found_city_names}}
        ]
    }).limit(30).to_list()

    # Handle is_liked logic for projects (wishlist)
    liked_project_ids = set()
    if current_user:
        leads = await ProjectLead.find(
            ProjectLead.user_id == current_user.id,
            ProjectLead.is_wishlisted == True
        ).to_list()
        liked_project_ids = {lead.project_id for lead in leads}

    # Format helpers
    def format_city(c: City) -> SearchItem:
        return SearchItem(
            uuid=c.id,
            name=c.name,
            image=public_image_url(c.images[0] if c.images else None),
            slug=c.slug,
            description=c.feature_description or c.city_description,
            is_liked=False # No explicit "liked" city system in current models
        )

    def format_landmark(l: Landmark) -> SearchItem:
        return SearchItem(
            uuid=l.id,
            name=l.name,
            image=public_image_url(l.images[0] if l.images else l.image_url),
            slug=str(l.id), # Landmark model lacks a slug field
            description=l.hero_desc or l.description,
            is_liked=False # No explicit "liked" landmark system in current models
        )

    def format_project(p: Project) -> SearchItem:
        return SearchItem(
            uuid=p.id,
            name=p.name,
            image=public_image_url(p.gallery_images[0] if p.gallery_images else None),
            slug=p.slug,
            description=p.description,
            is_liked=p.id in liked_project_ids
        )

    return {
        "cities": [format_city(c) for c in cities],
        "landmarks": [format_landmark(l) for l in landmarks],
        "projects": [format_project(p) for p in projects]
    }
