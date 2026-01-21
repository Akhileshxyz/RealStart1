from typing import Any, List, Dict
from fastapi import APIRouter, Depends
from app.api import deps
from app.models.user import User
from app.models.lawyer import (
    LawyerLead,
    LawyerLeadStatus,
    LawyerProfile,
    LawyerPaymentStatus,
)
from app.schemas.lawyer_portal import LawyerAnalyticsData, LawyerAnalyticsMetric, format_indian_currency
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/analytics", response_model=LawyerAnalyticsData)
async def get_analytics(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    lawyer_profile = await LawyerProfile.find_one(LawyerProfile.user_id == current_user.id)
    if not lawyer_profile:
        return LawyerAnalyticsData(metrics=[], charts=[])
    leads = await LawyerLead.find(LawyerLead.lawyer_id == lawyer_profile.id).to_list()
    total_cases = len(leads)
    active_clients = len({(l.client_phone or "", l.client_email or "") for l in leads if l.status != LawyerLeadStatus.LOST})
    paid_leads = [
        l for l in leads
        if l.payment_status == LawyerPaymentStatus.PAID and l.fee_amount
    ]
    total_earnings_value = sum(l.fee_amount or 0 for l in paid_leads)

    completed_leads = [l for l in leads if l.status == LawyerLeadStatus.COMPLETED]
    avg_resolution = 0
    if completed_leads:
        avg_resolution = int(
            sum((l.updated_at - l.created_at).days for l in completed_leads) / len(completed_leads)
        )

    # Deltas (last 30 days vs previous 30 days)
    now = datetime.utcnow()
    period_start = now - timedelta(days=30)
    prev_period_start = now - timedelta(days=60)
    current_cases = [l for l in leads if l.created_at >= period_start]
    prev_cases = [l for l in leads if prev_period_start <= l.created_at < period_start]
    cases_delta = len(current_cases) - len(prev_cases)

    current_clients = len({(l.client_phone or "", l.client_email or "") for l in current_cases})
    prev_clients = len({(l.client_phone or "", l.client_email or "") for l in prev_cases})
    clients_delta = current_clients - prev_clients

    current_earnings = sum((l.fee_amount or 0) for l in paid_leads if l.created_at >= period_start)
    prev_earnings = sum((l.fee_amount or 0) for l in paid_leads if prev_period_start <= l.created_at < period_start)
    earnings_delta_pct = 0.0
    if prev_earnings > 0:
        earnings_delta_pct = ((current_earnings - prev_earnings) / prev_earnings) * 100

    metrics = [
        LawyerAnalyticsMetric(
            id="total_cases",
            title="Total Cases",
            value=total_cases,
            delta=f"{cases_delta:+d}",
            delta_label="last 30 days",
        ),
        LawyerAnalyticsMetric(
            id="active_clients",
            title="Active Clients",
            value=active_clients,
            delta=f"{clients_delta:+d}",
            delta_label="last 30 days",
        ),
        LawyerAnalyticsMetric(
            id="total_earnings",
            title="Total Earnings",
            value=format_indian_currency(total_earnings_value),
            delta=f"{earnings_delta_pct:+.0f}%",
            delta_label="last 30 days",
        ),
        LawyerAnalyticsMetric(
            id="avg_resolution_time",
            title="Avg Resolution Time",
            value=f"{avg_resolution} days",
            delta="0%",
            delta_label="last 30 days",
        ),
    ]

    # Charts
    months: List[str] = []
    case_series: List[int] = []
    earnings_series: List[float] = []
    for i in range(5, -1, -1):
        month_start = (now.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        months.append(month_start.strftime("%b"))
        month_cases = [l for l in leads if month_start <= l.created_at < next_month]
        case_series.append(len(month_cases))
        month_earnings = sum(
            (l.fee_amount or 0) for l in paid_leads if month_start <= l.created_at < next_month
        )
        earnings_series.append(month_earnings)

    type_counts: Dict[str, int] = {}
    for lead in leads:
        key = lead.service_type or "Other"
        type_counts[key] = type_counts.get(key, 0) + 1

    resolution_counts = {
        "Completed": sum(1 for l in leads if l.status == LawyerLeadStatus.COMPLETED),
        "Lost": sum(1 for l in leads if l.status == LawyerLeadStatus.LOST),
        "In Progress": sum(1 for l in leads if l.status in [LawyerLeadStatus.CONTACTED, LawyerLeadStatus.CONVERTED, LawyerLeadStatus.FOLLOW_UP]),
        "Pending": sum(1 for l in leads if l.status == LawyerLeadStatus.NEW),
    }

    acquisition_months: List[str] = []
    acquisition_data: List[int] = []
    for i in range(7, -1, -1):
        month_start = (now.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        acquisition_months.append(month_start.strftime("%b"))
        month_clients = {
            (l.client_phone or "", l.client_email or "")
            for l in leads
            if month_start <= l.created_at < next_month
        }
        acquisition_data.append(len(month_clients))

    charts = [
        {
            "id": "cases_earnings_trend",
            "title": "Cases & Earnings Trend",
            "type": "combo",
            "months": months,
            "series": [
                {"name": "cases", "label": "cases", "data": case_series, "color": "#FF9500"},
                {"name": "earnings", "label": "earnings", "data": earnings_series, "color": "#FF9500", "type": "line"},
            ],
        },
        {
            "id": "case_type_distribution",
            "title": "Case Type Distribution",
            "type": "donut",
            "data": [
                {"name": name, "value": value, "color": "#FF9500"}
                for name, value in type_counts.items()
            ],
        },
        {
            "id": "case_resolution",
            "title": "Case Resolution",
            "type": "bar",
            "categories": list(resolution_counts.keys()),
            "data": [
                {"name": "Cases", "data": list(resolution_counts.values())}
            ],
        },
        {
            "id": "client_acquisition",
            "title": "Client Acquisition",
            "type": "bar",
            "months": acquisition_months,
            "data": [
                {"name": "New Clients", "data": acquisition_data}
            ],
        },
    ]

    return LawyerAnalyticsData(metrics=metrics, charts=charts)
