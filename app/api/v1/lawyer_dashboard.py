from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.models.user import User, UserRole
from app.models.lawyer import (
    LawyerProfile,
    LawyerLead,
    LawyerLeadStatus,
    LawyerPaymentStatus,
)
from beanie.operators import In
from beanie.operators import In
from app.models.project import Project, LegalDocumentStatus
from app.models.legal_call import LegalCallRequest, LegalCallStatus
from app.schemas.lawyer_portal import (
    LawyerDashboardData,
    LawyerDashboardStats,
    LawyerDashboardEarnings,
    LawyerDashboardAlert,
    LawyerCase,
    CaseStatus,
    CasePriority,
    ServiceType,
    LawyerScheduleEvent,
    EventType,
    format_indian_currency,
    format_indian_datetime,
)
from datetime import datetime, timedelta

router = APIRouter()


async def get_current_lawyer(
    current_user: User = Depends(deps.get_current_user),
) -> User:
    if current_user.role not in [UserRole.LAWYER, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user


async def get_lawyer_profile_id(user: User) -> UUID:
    if user.lawyer_profile_id:
        return user.lawyer_profile_id
    # Fallback to finding by user_id
    profile = await LawyerProfile.find_one(LawyerProfile.user_id == user.id)
    if profile:
        return profile.id
    raise HTTPException(status_code=404, detail="Lawyer profile not found")


@router.get("/dashboard", response_model=LawyerDashboardData)
async def get_dashboard(current_user: User = Depends(get_current_lawyer)) -> Any:
    lawyer_id = await get_lawyer_profile_id(current_user)

    now = datetime.utcnow()

    # 1. Stats
    leads = await LawyerLead.find(LawyerLead.lawyer_id == lawyer_id).to_list()
    total_leads_count = len(leads)
    active_leads_count = sum(
        1 for lead in leads
        if lead.status not in [LawyerLeadStatus.COMPLETED, LawyerLeadStatus.LOST]
    )
    completed_leads_count = sum(1 for lead in leads if lead.status == LawyerLeadStatus.COMPLETED)
    client_keys = {(lead.client_phone or "", lead.client_email or "") for lead in leads}
    total_clients_count = len(client_keys)

    week_start = now - timedelta(days=7)
    prev_week_start = now - timedelta(days=14)
    current_week = [l for l in leads if l.created_at >= week_start]
    previous_week = [l for l in leads if prev_week_start <= l.created_at < week_start]
    active_delta = len(current_week) - len(previous_week)
    total_clients_delta = len({(l.client_phone or "", l.client_email or "") for l in current_week})

    pending_docs_projects = await Project.find({"documents.status": LegalDocumentStatus.PENDING}).count()
    pending_reviews = pending_docs_projects
    urgent_pending = sum(
        1 for lead in leads
        if lead.status == LawyerLeadStatus.NEW and (now - lead.created_at).days >= 7
    )

    stats = LawyerDashboardStats(
        active_cases=active_leads_count,
        active_cases_delta=f"{active_delta:+d} this week",
        total_clients=total_clients_count,
        total_clients_delta=f"+{total_clients_delta} this week",
        pending_reviews=pending_reviews,
        pending_reviews_delta=f"{urgent_pending} urgent",
        completed_cases=completed_leads_count,
        completed_cases_delta=f"+{sum(1 for l in current_week if l.status == LawyerLeadStatus.COMPLETED)} this week",
    )

    # 2. Earnings
    paid_leads = [
        l for l in leads
        if l.payment_status == LawyerPaymentStatus.PAID and l.service_fee
    ]
    total_earnings_value = sum(l.service_fee or 0 for l in paid_leads)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    prev_month_start = (month_start - timedelta(days=1)).replace(day=1)
    current_month_earnings = sum(
        (l.service_fee or 0) for l in paid_leads if l.created_at >= month_start
    )
    previous_month_earnings = sum(
        (l.service_fee or 0) for l in paid_leads if prev_month_start <= l.created_at < month_start
    )
    delta_pct = 0.0
    if previous_month_earnings > 0:
        delta_pct = ((current_month_earnings - previous_month_earnings) / previous_month_earnings) * 100

    def sum_by_service(label: str) -> float:
        return sum(
            (l.service_fee or 0) for l in paid_leads
            if (l.service_type or "").lower() == label.lower()
        )

    earnings = LawyerDashboardEarnings(
        total_earnings=format_indian_currency(total_earnings_value),
        delta_text=f"{delta_pct:+.0f}% from last month",
        breakdown=[
            {"category": "Document Reviews", "amount": format_indian_currency(sum_by_service("Document Review"))},
            {"category": "Consultations", "amount": format_indian_currency(sum_by_service("Legal Consultation"))},
            {"category": "Title Searches", "amount": format_indian_currency(sum_by_service("Title Search"))},
        ],
    )

    # 3. Recent Cases
    recent_leads = sorted(leads, key=lambda l: l.created_at, reverse=True)[:5]
    recent_cases_list = []
    for lead in recent_leads:
        initials = "".join([n[0] for n in lead.client_name.split(" ")[:2]]).upper()
        status_map = {
            LawyerLeadStatus.NEW: CaseStatus.PENDING,
            LawyerLeadStatus.CONTACTED: CaseStatus.IN_PROGRESS,
            LawyerLeadStatus.CONVERTED: CaseStatus.IN_PROGRESS,
            LawyerLeadStatus.LOST: CaseStatus.ON_HOLD,
            LawyerLeadStatus.COMPLETED: CaseStatus.COMPLETED,
        }
        service_type = ServiceType.LEGAL_CONSULTATION
        if lead.service_type:
            for service in ServiceType:
                if service.value.lower() == lead.service_type.lower():
                    service_type = service
                    break

        priority = CasePriority.MEDIUM
        if lead.priority and lead.priority.upper() in CasePriority.__members__:
            priority = CasePriority[lead.priority.upper()]

        recent_cases_list.append(
            LawyerCase(
                id=str(lead.id),
                client_initials=initials,
                client_name=lead.client_name,
                project_name=lead.project_name,
                service_type=service_type,
                status=status_map.get(lead.status, CaseStatus.PENDING),
                priority=priority,
                location=lead.client_city,
                date=format_indian_datetime(lead.created_at),
                lead_id=str(lead.id),
            )
        )

    # 4. Schedule (today)
    calls = await LegalCallRequest.find(
        In(LegalCallRequest.status, [LegalCallStatus.ACCEPTED, LegalCallStatus.SCHEDULED])
    ).sort("created_at").limit(10).to_list()
    user_ids = list({call.user_id for call in calls})
    users = await User.find(User.id.in_(user_ids)).to_list() if user_ids else []
    user_map = {user.id: user.full_name for user in users}

    project_ids = list({call.project_id for call in calls})
    projects = await Project.find(Project.id.in_(project_ids)).to_list() if project_ids else []
    project_map = {project.id: project for project in projects}
    today_events = []
    for call in calls:
        schedule_time = call.scheduled_time or call.created_at
        if schedule_time.date() != now.date():
            continue
        project = project_map.get(call.project_id)
        title = "Legal Consultation Call"
        location = None
        if project:
            title = f"Legal Consultation - {project.name}"
            if project.city and project.state:
                location = f"{project.city}, {project.state}"
            elif project.city:
                location = project.city

        today_events.append(
            LawyerScheduleEvent(
                id=str(call.id),
                title=title,
                date=format_indian_datetime(schedule_time),
                time_str=schedule_time.strftime("%I:%M %p"),
                location=location,
                client_name=user_map.get(call.user_id),
                type=EventType.MEETING,
            )
        )

    # 5. Alerts
    alerts: List[LawyerDashboardAlert] = []
    if urgent_pending > 0:
        alerts.append(
            LawyerDashboardAlert(
                text=f"{urgent_pending} cases pending for more than 7 days",
                severity="high",
            )
        )
    if pending_reviews > 0:
        alerts.append(
            LawyerDashboardAlert(
                text=f"{pending_reviews} document reviews pending",
                severity="medium",
            )
        )

    return LawyerDashboardData(
        stats=stats,
        earnings=earnings,
        recent_cases=recent_cases_list,
        todays_schedule=today_events,
        alerts=alerts,
    )
