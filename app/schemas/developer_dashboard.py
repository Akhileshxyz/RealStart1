from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime


class ProjectMetrics(BaseModel):
    """Metrics per project"""
    project_id: UUID
    project_name: str
    project_slug: str
    visitors: int
    plot_visits: int
    legal_consultations: int
    interested_visitors: int
    total_views: int


class DeveloperDashboardMetrics(BaseModel):
    """Dashboard metrics for developer"""
    # Time period info
    period_start: datetime
    period_end: datetime
    period_type: str  # "day", "week", "month", "year", "custom"

    # Main metrics (filtered by time period)
    total_visitors: int  # Unique users who viewed
    total_plot_visits: int  # Visit bookings
    total_legal_consultations: int  # Legal requests

    # Additional metrics
    interested_visitors: int  # Users who wishlisted
    total_views: int  # Total view count (including repeat views)

    # Breakdown by project (optional detail)
    projects: List[ProjectMetrics]

    class Config:
        from_attributes = True
