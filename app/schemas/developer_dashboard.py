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



class StatMetric(BaseModel):
    """Metric with value, change, and trend"""
    value: float | int
    change: float | int
    trend: str  # "up", "down", "neutral"


class DashboardStats(BaseModel):
    """Top level dashboard stats"""
    visitors: StatMetric
    visit_bookings: StatMetric
    legal_consultations: StatMetric
    interested_buyers: StatMetric


class LeadsByProject(BaseModel):
    """Simplified leads by project metric"""
    project_name: str
    total_leads: int


class EnhancedDeveloperDashboard(BaseModel):
    """Enhanced dashboard with all analytics matches user request"""
    stats: DashboardStats
    visitors_leads_trend: List[TrendDataPoint]
    leads_by_project: List[LeadsByProject]
    projects_performance: List[ProjectPerformance]
    recent_activity: List[RecentActivityItem]
    lead_status_distribution: List[LeadStatusCount]

    class Config:
        from_attributes = True


# New Analytics Dashboard Schemas

class OverviewStats(BaseModel):
    """Overview section metrics with trends"""
    total_views: StatMetric
    total_leads: StatMetric
    wishlists: StatMetric
    conversion_rate: StatMetric


class PerformanceTrendPoint(BaseModel):
    """Single point in performance trend"""
    label: str  # e.g. "Jan", "Week 1"
    views: int
    leads: int
    conversions: int


class TopLocation(BaseModel):
    """Top performing location"""
    city: str
    views: int
    leads: int
    share: float  # percentage


class TrafficSource(BaseModel):
    """Traffic source breakdown"""
    source: str  # "Direct", "Google Search", etc.
    percentage: float
    count: int


class DeviceBreakdownItem(BaseModel):
    """Device usage item"""
    name: str
    value: float


class GeographicDistribution(BaseModel):
    """Geographic distribution by city"""
    city: str
    views: int
    leads: int
    share: float  # percentage


class ConversionFunnelStage(BaseModel):
    """Single stage in conversion funnel"""
    stage: str
    count: int
    percentage: float


class ConversionMetric(BaseModel):
    """Individual conversion metric"""
    metric_name: str
    rate: float  # percentage
    change: float  # percentage change


class LeadQualityItem(BaseModel):
    """Lead quality item"""
    quality: str
    count: int


class ProjectPerformanceRow(BaseModel):
    """Project performance table row"""
    project_name: str
    views: int
    leads: int
    conversion: float  # percentage
    trend: str  # "up", "down", "stable"


class AnalyticsDashboard(BaseModel):
    """Comprehensive analytics dashboard matching user request"""
    overview: OverviewStats
    performance_trend: List[PerformanceTrendPoint]
    traffic_sources: List[TrafficSource]
    device_breakdown: List[DeviceBreakdownItem]
    geographic_distribution: List[GeographicDistribution]
    project_performance: List[ProjectPerformanceRow]
    conversion_funnel: List[ConversionFunnelStage]
    conversion_metrics: List[ConversionMetric]
    lead_quality: List[LeadQualityItem]

    class Config:
        from_attributes = True
