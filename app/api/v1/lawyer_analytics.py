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
        return LawyerAnalyticsData(metrics=[], monthly_data=[], case_type_data=[], resolution_data=[])
    
    leads = await LawyerLead.find({"lawyer_id": lawyer_profile.id}).to_list()

    total_cases = len(leads)
    active_clients = len({(l.client_phone or "", l.client_email or "") for l in leads if l.status != LawyerLeadStatus.LOST})
    paid_leads = [
        l for l in leads
        if l.payment_status == LawyerPaymentStatus.PAID and l.service_fee
    ]
    total_earnings_value = sum(l.service_fee or 0 for l in paid_leads)

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

    current_earnings = sum(l.service_fee or 0 for l in paid_leads if l.created_at >= period_start)
    prev_earnings = sum(l.service_fee or 0 for l in paid_leads if prev_period_start <= l.created_at < period_start)
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

    # 1. Monthly Data (Last 6 months)
    monthly_data = []
    for i in range(5, -1, -1):
        # Calculate month range
        target_date = now.replace(day=1)
        for _ in range(i):
            target_date = (target_date - timedelta(days=1)).replace(day=1)
        
        month_start = target_date
        if month_start.month == 12:
            next_month = month_start.replace(year=month_start.year + 1, month=1)
        else:
            next_month = month_start.replace(month=month_start.month + 1)
            
        month_leads = [l for l in leads if month_start <= l.created_at < next_month]
        month_paid_leads = [l for l in paid_leads if month_start <= l.created_at < next_month]
        
        monthly_data.append({
            "month": month_start.strftime("%b"),
            "cases": len(month_leads),
            "earnings": sum(l.service_fee or 0 for l in month_paid_leads),
            "clients": len({(l.client_phone or "", l.client_email or "") for l in month_leads})
        })

    # 2. Case Type Distribution
    type_counts: Dict[str, int] = {}
    for lead in leads:
        key = lead.service_type or "Other"
        type_counts[key] = type_counts.get(key, 0) + 1
    
    colors = [
        "hsl(var(--primary))",
        "hsl(var(--chart-2))",
        "hsl(var(--chart-3))",
        "hsl(var(--chart-4))",
        "hsl(var(--chart-5))"
    ]
    
    case_type_data = []
    sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
    for idx, (name, value) in enumerate(sorted_types):
        case_type_data.append({
            "name": name,
            "value": value,
            "color": colors[idx % len(colors)]
        })

    # 3. Resolution Data
    resolution_data = [
        {"status": "Won", "count": sum(1 for l in leads if l.status == LawyerLeadStatus.COMPLETED)},
        {"status": "Settled", "count": sum(1 for l in leads if l.status == LawyerLeadStatus.SOLVED)},
        {"status": "In Progress", "count": sum(1 for l in leads if l.status in [LawyerLeadStatus.CONTACTED, LawyerLeadStatus.CONVERTED, LawyerLeadStatus.FOLLOW_UP])},
        {"status": "Lost", "count": sum(1 for l in leads if l.status == LawyerLeadStatus.LOST)},
    ]

    return LawyerAnalyticsData(
        metrics=metrics,
        monthly_data=monthly_data,
        case_type_data=case_type_data,
        resolution_data=resolution_data
    )
