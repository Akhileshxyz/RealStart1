from pydantic import BaseModel
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime


class ProjectMetrics(BaseModel):
    """Metrics per project"""
    project_id: UUID
    project_name: str
    project_slug: str
    city: Optional[str] = None
    visitors: int
    plot_visits: int
    legal_consultations: int
    interested_visitors: int
    total_views: int


class TrendDataPoint(BaseModel):
    """Single data point for trend chart"""
    date: str  # ISO date string
    visitors: int
    leads: int


class LeadStatusCount(BaseModel):
    """Lead count by status"""
    status: str
    count: int


class CityMetrics(BaseModel):
    """Metrics grouped by city"""
    city: str
    leads: int
    visitors: int


class RecentActivityItem(BaseModel):
    """Recent activity entry"""
    activity_type: str  # "view", "wishlist", "legal_request", "visit_booking"
    user_name: str
    user_email: Optional[str] = None
    project_name: str
    project_slug: str
    timestamp: datetime


class ProjectPerformance(BaseModel):
    """Project performance metrics"""
    project_id: UUID
    project_name: str
    project_slug: str
    city: Optional[str] = None
    visitors: int
    conversion_rate: float  # percentage of visitors who became interested
    total_leads: int
    avg_time_on_project: Optional[float] = None  # in minutes


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


class EnhancedDeveloperDashboard(BaseModel):
    """Enhanced dashboard with all analytics"""
    # Time period info
    period_start: datetime
    period_end: datetime
    period_type: str

    # Summary Metrics
    total_visitors: int
    visit_bookings: int
    legal_consultations: int
    interested_buyers: int

    # Visitors & Leads Trend (time series data)
    visitors_leads_trend: List[TrendDataPoint]

    # Leads by Project
    leads_by_project: List[ProjectMetrics]

    # Leads by City (user location)
    leads_by_city: List[CityMetrics]

    # Projects Performance
    projects_performance: List[ProjectPerformance]

    # Recent Activity
    recent_activity: List[RecentActivityItem]

    # Lead Status Distribution
    lead_status_distribution: List[LeadStatusCount]

    class Config:
        from_attributes = True
