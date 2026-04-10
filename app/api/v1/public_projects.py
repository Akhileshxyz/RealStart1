from datetime import datetime, timezone, timedelta
from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.api import deps
from app.models.user import User
from app.models.lead import ProjectLead
from app.models.developer import Developer
from app.models.market_intelligence import MarketIntelligence
from app.models.review import Review, ReviewEntityType
from app.models.project import Project, ProjectStatus, LegalDocumentType
from app.schemas.project import (
    ProjectResponse, 
    PublicProjectDetailResponse,
    ProjectAmenity,
    ProjectInventoryItem,
    GrowthForecast,
    GrowthForecastDataPoint,
    LocationAdvantage,
    ProjectAgent,
    ProjectDocumentDetail,
    ProjectDocuments
)
from app.services.project_service import get_approved_projects, get_project_by_slug, get_project_by_id
from app.schemas.visit import ProjectAvailabilityResponse, DateAvailability, TimeSlot
from app.models.lead import ProjectLead

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.get("/", response_model=List[ProjectResponse])
@limiter.limit("60/minute")
async def list_public_projects(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    landmark_id: Optional[UUID] = None
) -> Any:
    """
    List all APPROVED projects visible to public.
    Support filtering by landmark_id (locality).
    TIER 1 CACHING: Results cached for 1 hour.
    RATE LIMIT: 60 requests per minute.
    """
    projects = await get_approved_projects(skip=skip, limit=limit, landmark_id=landmark_id, use_cache=True)
    return projects

async def _map_project_to_public_detail(project: Project) -> PublicProjectDetailResponse:
    # 1. Basic Info
    location_parts = []
    if project.landmark: location_parts.append(project.landmark)
    elif project.address_line_1: location_parts.append(project.address_line_1)
    if project.city: location_parts.append(project.city)
    location_name = ", ".join(location_parts) if location_parts else "Bengaluru"
    
    hero_image = project.gallery_images[0] if project.gallery_images else "/media/projects/hero.png"
    
    price_display = f"₹{int(project.min_price):,}/sqft" if project.min_price else "Price on Request"
    unit_type = project.property_type.value if project.property_type else "Plots"
    
    # 2. Overview
    overview = {
        "total_area": f"{project.total_area_sqft:,.0f} sqft" if project.total_area_sqft else "12 Acres",
        "total_units": f"{project.number_of_units} Units" if project.number_of_units else "184 Plots",
        "legal_status": "E-khata", # Placeholder or from project field if added
        "possession": project.possession_date.strftime("%b %Y") if project.possession_date else "Immediate",
        "water_source": "Borewell", # Placeholder
        "rera_status": "Approved" if project.rera_number else "Applied"
    }

    # 3. Amenities
    # Map simple strings to icons
    amenity_icons = {
        "Clubhouse": "/icons/home.svg",
        "Swimming Pool": "/icons/waves.svg",
        "Gym": "/icons/gym.svg",
        "Park": "/icons/tree.svg",
        "Security": "/icons/shield.svg",
    }
    amenities = [
        ProjectAmenity(name=a, icon_url=amenity_icons.get(a, "/icons/star.svg"))
        for a in project.amenities
    ] or [ProjectAmenity(name="Standard Amenities", icon_url="/icons/star.svg")]

    # 4. Inventory (Mock for now, or based on Project data if we had unit-level)
    # We can use min/max price to generate 1 item
    inventory = []
    if project.min_price:
        inventory.append(ProjectInventoryItem(
            dimension="30 × 40", # Placeholder
            area="1,200 sqft", # Placeholder
            price=f"₹{(project.min_price * 1200 / 100000):.2f} L",
            rate=f"@{int(project.min_price)}/sqft",
            status="Available"
        ))
    else:
        inventory = [ProjectInventoryItem(dimension="30 × 40", area="1,200 sqft", price="₹1.06cr", rate="@8900/sqft", status="Available")]

    # 5. Growth Forecast
    # Use MarketIntelligence if landmark_id exists
    forecast_data = []
    roi_text = "Projected +112% ROI over 5 years based on corridor momentum."
    if project.landmark_id:
        mi = await MarketIntelligence.find_one(MarketIntelligence.landmark_id == project.landmark_id)
        if mi and mi.growth_prediction:
            for p in mi.growth_prediction:
                forecast_data.append(GrowthForecastDataPoint(year=str(p.get("year")), price=float(p.get("price") or 0)))
    
    if not forecast_data:
         # Fallback data
         forecast_data = [
             GrowthForecastDataPoint(year="2024", price=8900),
             GrowthForecastDataPoint(year="2025", price=10200)
         ]
         
    growth_forecast = GrowthForecast(
        chart_label="Price Appreciation Forecast (₹/sqft)",
        roi_text=roi_text,
        data=forecast_data
    )

    # 6. Location Advantages
    # Map from nearby_facilities
    location_advantages = [
        LocationAdvantage(name=f, distance="4.0 km", duration="10 mins", type="airport")
        for f in project.nearby_facilities
    ] or [LocationAdvantage(name="Manyata Tech Park", distance="4.0 km", duration="10 mins", type="airport")]

    # 7. Agent
    developer = await Developer.get(project.developer_id)
    agent = ProjectAgent(
        name=developer.name if developer else "Ramesh Kumar",
        role="Senior Sales Manager",
        avatar_url=developer.logo_url if developer and developer.logo_url else "/media/agents/default.png",
        phone=developer.contact_phone if developer and developer.contact_phone else "+91 9876543210",
        is_verified=developer.is_verified if developer else True
    )

    # 8. Documents
    legal_docs = []
    technical_docs = []
    for d in project.documents:
        doc_detail = ProjectDocumentDetail(
            title=d.name,
            meta=f"Verified • {d.type.value}", 
            file_url=d.file_url,
            is_locked=False
        )
        if d.type in [LegalDocumentType.RERA_CERT, LegalDocumentType.SALE_DEED, LegalDocumentType.MOTHER_DEED, LegalDocumentType.ENCUMBRANCE_CERT]:
            legal_docs.append(doc_detail)
        else:
            technical_docs.append(doc_detail)
    
    # Defaults if empty
    if not legal_docs:
        legal_docs.append(ProjectDocumentDetail(title="RERA Approval", meta="Verified • 2.4 MB", file_url="/docs/rera.pdf"))
    if not technical_docs:
        technical_docs.append(ProjectDocumentDetail(title="Layout Plan", meta="High Res", file_url="/docs/plan.pdf"))

    # 0. Rating Calculation
    reviews = await Review.find(
        Review.entity_id == project.id,
        Review.entity_type == ReviewEntityType.PROJECT
    ).to_list()
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 4.8

    return PublicProjectDetailResponse(
        id=project.id,
        title=project.name,
        slug=project.slug,
        location_name=location_name,
        rating=round(avg_rating, 1),
        hero_image=hero_image,
        price_display=price_display,
        price_value=int(project.min_price) if project.min_price else None,
        unit_type=unit_type,
        description=project.description or "No description available",
        photos=project.gallery_images or [hero_image],
        overview=overview,
        amenities=amenities,
        inventory=inventory,
        growth_forecast=growth_forecast,
        location_advantages=location_advantages,
        agent=agent,
        documents=ProjectDocuments(legal=legal_docs, technical=technical_docs)
    )

@router.get("/{slug_or_id}", response_model=PublicProjectDetailResponse)
@limiter.limit("120/minute")
async def get_public_project(
    request: Request,
    slug_or_id: str,
    current_user: Optional[User] = Depends(deps.get_current_user_optional) # Need to implement optional Auth dep or handle try/except
) -> Any:
    """
    Get a specific APPROVED project by slug or project ID.
    Logs the view if user is logged in.
    """
    # Try ID first if it looks like a UUID
    project = None
    try:
        project_uuid = UUID(slug_or_id)
        project = await get_project_by_id(project_uuid, use_cache=True)
        # Verify status since public API only shows APPROVED/UNHIDDEN
        if project and (project.status != ProjectStatus.APPROVED or project.is_hidden):
            project = None
    except (ValueError, AttributeError):
        # Not a valid UUID, try as slug
        project = await get_project_by_slug(slug=slug_or_id, status=ProjectStatus.APPROVED, use_cache=True)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Log View if User is logged in
    if current_user:
        lead = await ProjectLead.find_one(
            ProjectLead.project_id == project.id,
            ProjectLead.user_id == current_user.id
        )
        if lead:
            lead.last_viewed_at = datetime.now(timezone.utc)
            lead.viewed_at_history.append(datetime.now(timezone.utc))
            await lead.save()
        else:
            lead = ProjectLead(
                project_id=project.id,
                user_id=current_user.id,
                viewed_at_history=[datetime.now(timezone.utc)]
            )
            await lead.insert()
            
    return await _map_project_to_public_detail(project)

@router.get("/{project_id}/availability", response_model=ProjectAvailabilityResponse)
@limiter.limit("60/minute")
async def get_project_availability(
    request: Request,
    project_id: UUID,
    start_date: str = Query(..., example="2026-04-10"),
    end_date: str = Query(..., example="2026-04-17")
) -> Any:
    """
    Get available visit slots for a project within a date range.
    """
    # Verify project exists
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Fetch existing bookings for this project in this range to mark as unavailable
    existing_bookings = await ProjectLead.find(
        ProjectLead.project_id == project_id,
        ProjectLead.visit_date >= start_date,
        ProjectLead.visit_date <= end_date,
        ProjectLead.visit_status == "BOOKED"
    ).to_list()

    booked_slots = {} # {(date, time): True}
    for b in existing_bookings:
        booked_slots[(b.visit_date, b.visit_time)] = True

    # Generate slots logic (10 AM to 5 PM, 1 hour intervals)
    standard_slots = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
    
    # Parse dates
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    availability = []
    curr_dt = start_dt
    while curr_dt <= end_dt:
        date_str = curr_dt.strftime("%Y-%m-%d")
        slots = []
        for s in standard_slots:
            is_available = not booked_slots.get((date_str, s), False)
            # Simple rule: No visits on Sundays (0=Mon, 6=Sun)
            if curr_dt.weekday() == 6:
                is_available = False
            
            slots.append(TimeSlot(time=s, available=is_available))
        
        availability.append(DateAvailability(date=date_str, slots=slots))
        curr_dt += timedelta(days=1)

    # 3. Format Project Mini Detail
    location_parts = []
    if project.landmark: location_parts.append(project.landmark)
    elif project.address_line_1: location_parts.append(project.address_line_1)
    if project.city: location_parts.append(project.city)
    location_name = ", ".join(location_parts) if location_parts else "Bengaluru"
    
    price_display = f"₹{int(project.min_price):,}/sqft" if project.min_price else "Price on Request"
    hero_image = project.gallery_images[0] if project.gallery_images else "/media/projects/hero.png"

    return ProjectAvailabilityResponse(
        project_id=project_id,
        project={
            "id": project.id,
            "title": project.name,
            "location_name": location_name,
            "price_display": price_display,
            "hero_image": hero_image
        },
        availability=availability
    )
